import json
import os
import csv
import time
import logging
import hashlib
import re
import argparse
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Set
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalInterviewProcessor:
    def __init__(self, proxy_api_key: Optional[str] = None):
        # Директории и пути
        self.data_dir: Path = Path(__file__).resolve().parent
        self.processed_dir: Path = self.data_dir / "processed_csv"
        self.cache_path: Path = self.data_dir / "llm_cache.json"

        # Секреты (.env → ENV)
        self._load_dotenv(self.data_dir / ".env")
        self.proxy_api_key: str = proxy_api_key or os.getenv("PROXY_API_KEY", "").strip()
        if not self.proxy_api_key:
            raise RuntimeError("PROXY_API_KEY is not set. Provide it via ENV or sobes-data/.env")

        # HTTP/LLM
        self.proxy_api_url = "https://api.proxyapi.ru/openai/v1/chat/completions"
        self.model = "gpt-4.1-mini"
        self.headers = {
            "Authorization": f"Bearer {self.proxy_api_key}",
            "Content-Type": "application/json",
        }

        # Промпт и целевой CSV формат (схема как в test_3_blocks.py)
        self.prompt_template = (
            """Ты - эксперт по анализу IT-собеседований. Извлеки ВСЕ отдельные вопросы и задачи из текста интервью.

ИЗВЛЕКАЙ ПОЛНЫЕ формулировки задач, но:
- ПРОПУСКАЙ неинформативные ссылки ("отсюда", "с того собеса")
- ОБЪЕДИНЯЙ фрагменты в цельные задачи
- СОХРАНЯЙ технические детали и требования
- НЕ извлекай бессмысленные обрывки ("Иначе false", "Возвращает данные")
- ИЗВЛЕКАЙ даже короткие, но осмысленные вопросы ("event-loop", "Что такое замыкания")

 КРИТИЧЕСКИ ВАЖНО:
- Каждый вопрос = отдельная строка
- Каждая задача = отдельная строка
- НЕ РАЗБИВАЙ одну задачу на части! Если по смыслу это одна задача — делай ОДНУ строку
- Каждая строка должна иметь СМЫСЛ как отдельный вопрос/задача
- Поле company оставляй пустым (я подставлю сам)
- Извлеки дату из текста в формате YYYY-MM-DD (если не удалось — оставь пустым)
- Используй interview_id: {interview_id} для группировки всех вопросов из этого собеседования
- Возвращай ТОЛЬКО чистый CSV БЕЗ ```csv``` блоков и БЕЗ заголовка

CSV ФОРМАТ:
id,question_text,company,date,interview_id

ПРАВИЛЬНЫЕ ПРИМЕРЫ:
q1,"Реализуйте функцию debounce с настраиваемой задержкой",Яндекс,2025-07-18,interview_001
q2,"Promise задача: определить что выводится в консоль при обработке асинхронного кода",Яндекс,2025-07-18,interview_001
q3,"Задача на замыкание: написать функцию runOnce которая выполняется только один раз",Сбер,2025-07-17,interview_002
q4,"event-loop",Яндекс,2025-07-14,interview_003

 ДОПОЛНИТЕЛЬНО:
- Если в тексте есть код функций или классов, сформулируй отдельные задачи по ним (например: getRoute, parallelLimit)
- Не используй переводы строк внутри вопроса; заменяй их пробелами

 СТРОГОСТЬ CSV:
 - Ровно 5 полей, без заголовка
 - Кавычки только вокруг question_text
 - Не добавляй лишних пробелов по краям полей
 - Поле company оставь пустым
 - interview_id оставляй таким, как передан: {interview_id}

 ФОРМУЛИРОВКИ БЕЗ КОДА:
 - Если в вопрос попал код — перефразуй в краткую постановку задачи одной строкой, без многострочного кода

ОБРАБОТАЙ:
{full_content}"""
        )

        # Кэш и стандартизация компаний
        self._cache: Dict[str, str] = self._load_cache()
        self._company_map: Dict[str, str] = self._load_company_standardization()
        # Глобальный бюджет по количеству обрабатываемых records (full_content)
        self.global_record_budget: Optional[int] = None

    def send_to_llm(self, content: str, company_for_log: str, interview_id: str) -> Optional[str]:
        """Отправляет контент в LLM и возвращает CSV-строку (без заголовка)."""
        prompt = self.prompt_template.format(full_content=content, interview_id=interview_id)

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 2000,
        }

        try:
            logger.info(f"LLM запрос: {company_for_log} / {interview_id}")
            response = requests.post(
                self.proxy_api_url,
                headers=self.headers,
                json=payload,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                csv_content = result["choices"][0]["message"]["content"].strip()
                return csv_content
            else:
                logger.error(f"Ошибка API: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Ошибка отправки для {company_for_log}: {str(e)}")
            return None

    def process_company_batch(self, company_data: dict, output_dir: Path) -> bool:
        """Обрабатывает все интервью одной компании c кэшем/дедуп/фильтрами."""
        raw_company = company_data.get("company", "")
        company_norm = self._normalize_company(raw_company) or "Unknown"
        records = company_data.get("records", [])

        logger.info(f"Обработка компании {company_norm} ({len(records)} интервью)")

        # Создаем директорию если не существует
        output_dir.mkdir(parents=True, exist_ok=True)

        # Дедуп по нормализованному question_text
        seen_q_hashes: Set[str] = set()
        # Счётчики для автогенерации id в формате qN по каждому interview_id
        id_counters: Dict[str, int] = {}

        # Буфер: сначала заголовок в целевом формате
        header = ["id", "question_text", "company", "date", "interview_id"]
        rows_to_write: List[List[str]] = [header]

        # Простая статистика качества извлечения
        stats_header_skipped = 0
        stats_parse_errors = 0
        stats_invalid_filtered = 0
        stats_duplicates_skipped = 0
        stats_rows_appended = 0
        stats_llm_lines = 0
        stats_cache_hits = 0

        for i, record in enumerate(records):
            if self.global_record_budget is not None and self.global_record_budget <= 0:
                break
            full_content = (record.get("full_content", "") or "").strip()
            if not full_content:
                logger.warning(f"Пустой контент для {company_norm} интервью {i}")
                # Учитываем попытку даже с пустым блоком, чтобы не зациклиться
                if self.global_record_budget is not None:
                    self.global_record_budget -= 1
                continue

            interview_id = self._make_interview_id(company_norm, i)
            content_hash = self._hash_content(full_content)

            # Кэш по содержимому
            if content_hash in self._cache:
                csv_result = self._cache[content_hash]
                logger.info(f"КЭШ hit: {company_norm} / {interview_id}")
                stats_cache_hits += 1
            else:
                csv_result = self.send_to_llm(full_content, company_norm, interview_id)
                if not csv_result:
                    # Пауза и продолжим, если ошибка API
                    time.sleep(0.5)
                    continue
                self._cache[content_hash] = csv_result
                self._save_cache()

            # Постобработка: убрать возможный заголовок, распарсить CSV
            for line in [ln.strip() for ln in csv_result.split("\n") if ln.strip()]:
                stats_llm_lines += 1
                if line.lower().startswith("id,"):
                    stats_header_skipped += 1
                    continue
                try:
                    # Надежный разбор CSV строки
                    parsed = next(csv.reader([line]))
                    # Допуск: если LLM опустила поле company, придёт 4 колонки
                    if len(parsed) == 5:
                        _id, q_text, company_field, date_field, intr_id = parsed[:5]
                    elif len(parsed) == 4:
                        _id, q_text, date_field, intr_id = parsed[:4]
                        company_field = ""
                    else:
                        stats_parse_errors += 1
                        continue

                    # Нормализация и фильтры
                    q_text_norm = self._normalize_text(q_text)
                    if not self._is_valid_text(q_text_norm):
                        stats_invalid_filtered += 1
                        continue

                    q_hash = hashlib.md5(q_text_norm.encode("utf-8")).hexdigest()
                    if q_hash in seen_q_hashes:
                        stats_duplicates_skipped += 1
                        continue
                    seen_q_hashes.add(q_hash)

                    # Компания: берём из исходного JSON, игнорируем поле из LLM
                    company_final = company_norm
                    # Дата: пытаемся извлечь из исходного текста, иначе оставляем то, что пришло от LLM
                    date_extracted = self._extract_date_from_text(full_content) or (date_field or "").strip()

                    # Перезаписываем interview_id на наш, чтобы стабилизировать группировку
                    # Нормализуем id: если не q\d+, присваиваем последовательный qN в рамках interview_id
                    if not re.match(r"^q\d+$", _id or ""):
                        next_idx = id_counters.get(interview_id, 0) + 1
                        id_counters[interview_id] = next_idx
                        _id = f"q{next_idx}"

                    row_out = [_id, q_text.strip(), company_final, date_extracted, interview_id]
                    rows_to_write.append(row_out)
                    stats_rows_appended += 1
                except Exception:
                    stats_parse_errors += 1
                    continue

            # Рейтконтроль
            time.sleep(0.2)

            # Декремент глобального бюджета после обработки одного блока
            if self.global_record_budget is not None:
                self.global_record_budget -= 1

        # Сохраняем результат
        output_file = output_dir / f"{company_norm.replace(' ', '_')}.csv"
        try:
            with output_file.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(
                    f,
                    quoting=csv.QUOTE_ALL,
                    quotechar='"',
                    escapechar='\\',
                    doublequote=True,
                )
                writer.writerows(rows_to_write)

            logger.info(
                f"Сохранен файл {output_file} с {max(0, len(rows_to_write)-1)} вопросами"
            )
            logger.info(
                f"Статистика для {company_norm}: rows={stats_rows_appended}, dup_skipped={stats_duplicates_skipped}, "
                f"invalid_filtered={stats_invalid_filtered}, parse_errors={stats_parse_errors}, headers_skipped={stats_header_skipped}, "
                f"llm_lines={stats_llm_lines}, cache_hits={stats_cache_hits}"
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения файла {output_file}: {str(e)}")
            return False

    def process_all_companies(self, json_file: Path, output_dir: Path, limit: Optional[int] = None, record_limit: Optional[int] = None):
        """Обрабатывает компании из JSON файла с опциональным лимитом."""
        try:
            with json_file.open("r", encoding="utf-8") as f:
                companies_data = json.load(f)

            if limit is not None:
                companies_data = companies_data[:limit]
                logger.info(f"Обработка ограничена до {limit} компаний")

            logger.info(f"Загружено {len(companies_data)} компаний")

            # Устанавливаем глобальный лимит по количеству records
            self.global_record_budget = record_limit

            processed_count = 0
            failed_count = 0

            for company_data in companies_data:
                if self.global_record_budget is not None and self.global_record_budget <= 0:
                    break
                success = self.process_company_batch(company_data, output_dir)
                processed_count += int(bool(success))
                failed_count += int(not success)
                time.sleep(1.0)

            logger.info(
                f"Завершена обработка: {processed_count} успешно, {failed_count} ошибок"
            )
            # Сброс бюджета
            self.global_record_budget = None
        except Exception as e:
            logger.error(f"Ошибка обработки файла {json_file}: {str(e)}")

    def merge_csv_files(self, input_dir: Path, output_file: Path):
        """Объединяет все CSV файлы в один с глобальной дедупликацией по question_text."""
        csv_files = [f.name for f in input_dir.glob('*.csv')]

        if not csv_files:
            logger.warning("Не найдено CSV файлов для объединения")
            return

        header = None
        seen_q_hashes: Set[str] = set()
        merged_rows: List[List[str]] = []
        duplicates_skipped_merge = 0

        for csv_file in csv_files:
            file_path = input_dir / csv_file
            try:
                with file_path.open('r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row_idx, row in enumerate(reader):
                        if not row:
                            continue
                        # Заголовок
                        if row_idx == 0 and row and row[0].strip().lower() == 'id':
                            if header is None:
                                header = row
                            continue
                        # Дедуп по question_text (второе поле)
                        if len(row) < 2:
                            continue
                        q_text_norm = self._normalize_text(row[1])
                        q_hash = hashlib.md5(q_text_norm.encode('utf-8')).hexdigest()
                        if q_hash in seen_q_hashes:
                            duplicates_skipped_merge += 1
                            continue
                        seen_q_hashes.add(q_hash)
                        merged_rows.append(row)
            except Exception as e:
                logger.error(f"Ошибка чтения {csv_file}: {str(e)}")

        # Сохраняем объединенный файл
        try:
            with output_file.open('w', encoding='utf-8', newline='') as f:
                writer = csv.writer(
                    f,
                    quoting=csv.QUOTE_ALL,
                    quotechar='"',
                    escapechar='\\',
                    doublequote=True,
                )
                if header:
                    writer.writerow(header)
                writer.writerows(merged_rows)

            logger.info(f"Создан объединенный файл {output_file} с {len(merged_rows)} записями; дубликатов снято: {duplicates_skipped_merge}")

        except Exception as e:
            logger.error(f"Ошибка создания объединенного файла: {str(e)}")

    # ------------------------- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ -------------------------
    def _load_dotenv(self, dotenv_path: Path) -> None:
        """Простая загрузка .env без зависимостей."""
        if not dotenv_path.exists():
            return
        try:
            for line in dotenv_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
        except Exception:
            pass

    def _load_cache(self) -> Dict[str, str]:
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    def _save_cache(self) -> None:
        try:
            with self.cache_path.open("w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False)
        except Exception:
            pass

    def _hash_content(self, content: str) -> str:
        """Версионированный ключ кэша: текст + модель + версия промпта."""
        content_norm = " ".join(content.split()).strip().lower()
        prompt_ver = hashlib.md5(self.prompt_template.encode("utf-8")).hexdigest()
        key = f"{content_norm}::model={self.model}::prompt={prompt_ver}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()

    def _normalize_text(self, text: str) -> str:
        return " ".join((text or "").split()).strip()

    def _is_valid_text(self, text: str, min_length: int = 0) -> bool:
        # Убираем длиновой порог: принимаем короткие содержательные вопросы
        if not text:
            return False
        garbage = {
            "use strict",
            "// ---",
            "/*",
            "*/",
            "...",
            ".",
            "undefined",
            "null",
        }
        low = text.strip().lower()
        if low in garbage:
            return False
        # Отфильтровываем слишком общие/пустые формулировки
        garbage_substrings = [
            "описание отсутствует",
            "детали задачи не указаны",
        ]
        for phrase in garbage_substrings:
            if phrase in low:
                return False
        return True

    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """Ищет первую дату формата YYYY-MM-DD в исходном тексте."""
        try:
            m = re.search(r"(20\d{2}-\d{2}-\d{2})", text)
            return m.group(1) if m else None
        except Exception:
            return None

    def _make_interview_id(self, company: str, idx: int) -> str:
        base = company.replace(" ", "_")[:40]
        return f"interview_{base}_{idx:03d}"

    def _load_company_standardization(self) -> Dict[str, str]:
        """Мини-словарь нормализации компаний из companies_* и ручного маппинга."""
        mapping: Dict[str, str] = {}

        # Из companies_final_clean.json (справочник компаний)
        companies_json = self.data_dir / "companies_final_clean.json"
        if companies_json.exists():
            try:
                with companies_json.open("r", encoding="utf-8") as f:
                    companies = json.load(f)
                for c in companies:
                    if isinstance(c, str) and c.strip():
                        mapping.setdefault(c.strip().lower(), c.strip())
            except Exception:
                pass

        # Из companies_extracted.md (точные привязки)
        companies_md = self.data_dir / "companies_extracted.md"
        if companies_md.exists():
            try:
                content = companies_md.read_text(encoding="utf-8")
                import re
                for m in re.finditer(r"- \*\*Компания\*\*:\s*([^\n]+)", content):
                    name = m.group(1).strip()
                    if name and name.lower() not in {"нет данных", "нет названия компании"}:
                        mapping.setdefault(name.lower(), name)
            except Exception:
                pass

        # Ручной маппинг (частые кейсы)
        manual = {
            "сбербанк": "Сбер",
            "сбер": "Сбер",
            "альфа-банк": "Альфа-Банк",
            "альфабанк": "Альфа-Банк",
            "альфабанк": "Альфа-Банк",
            "яндекс": "Яндекс",
            "yandex": "Яндекс",
            "втб": "ВТБ",
            "авито": "Авито",
            "тинькофф": "Т-Банк",
            "т-банк": "Т-Банк",
            "gazprombank": "Газпромбанк",
            "gazprom": "Газпромбанк",
            "домклик": "Domclick",
            "domclick": "Domclick",
            "ozon": "Ozon",
            "озон": "Ozon",
            "wildberries": "Wildberries",
            "вк видео": "ВК",
            "вк": "ВК",
            "циан": "Циан",
            "cian": "Циан",
            "purrweb": "Purrweb",
        }
        for k, v in manual.items():
            mapping.setdefault(k, v)

        return mapping

    def _normalize_company(self, name: Optional[str]) -> str:
        if not name:
            return "Unknown"
        clean = str(name).strip()
        low = clean.lower()

        # Быстрый manual/справочник
        # точное
        if low in self._company_map:
            return self._company_map[low]
        # подстрочное
        for key, val in self._company_map.items():
            if key and key in low and len(key) >= 3:
                return val
        # Капитализация по умолчанию
        return " ".join(w.capitalize() for w in clean.split())


def main():
    parser = argparse.ArgumentParser(description="Extract interview questions to CSV (LLM-powered)")
    parser.add_argument("--company-limit", type=int, default=None, help="Ограничить число компаний (по порядку из JSON)")
    parser.add_argument("--record-limit", type=int, default=None, help="Ограничить число интервью-блоков (records) суммарно для теста")
    parser.add_argument("--model", type=str, default=None, help="Переопределить модель (например, gpt-4o-mini)")
    parser.add_argument("--input-json", type=str, default=None, help="Путь к входному JSON (по умолчанию MASSIV_GROUPED.json)")
    args = parser.parse_args()

    # Конфигурация путей (без хардкодов)
    processor = FinalInterviewProcessor()
    if args.model:
        processor.model = args.model

    input_json = Path(args.input_json).resolve() if args.input_json else (processor.data_dir / "MASSIV_GROUPED.json")
    output_dir = processor.processed_dir
    final_csv = processor.data_dir / "interview_questions_clean.csv"

    company_limit = args.company_limit
    record_limit = args.record_limit

    print("ЗАПУСК ФИНАЛЬНОЙ ОБРАБОТКИ")
    print(f"Лимит компаний: {company_limit if company_limit is not None else 'все'}; лимит records: {record_limit if record_limit is not None else 'нет'}")

    # Обрабатываем компании
    processor.process_all_companies(input_json, output_dir, company_limit, record_limit)

    # Объединяем все CSV в один файл
    processor.merge_csv_files(output_dir, final_csv)

    print("Обработка завершена!")
    print(f"Результат: {final_csv}")


if __name__ == "__main__":
    main()
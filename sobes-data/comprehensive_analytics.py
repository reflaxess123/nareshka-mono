#!/usr/bin/env python3
"""
Точный поиск записей собеседований по компаниям.
Использует FlashText + fuzzy fallback для максимальной точности.
"""

import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional
import argparse
from dataclasses import dataclass
from functools import lru_cache

try:
    from flashtext import KeywordProcessor
    from rapidfuzz import process, fuzz
    from tqdm import tqdm
    import yaml
except ImportError as e:
    print(f"❌ Отсутствует зависимость: {e}")
    print("Установите основные зависимости: pip install flashtext rapidfuzz tqdm pyyaml")
    exit(1)

@dataclass
class InterviewRecord:
    timestamp: str
    company: str
    content: str
    hash: str

class CompanyMatcher:
    def __init__(self, companies: List[str]):
        self.companies = companies
        self.stop_words = {'tech', 'systems', 'global', 'group', 'company', 'банк', 'технологии'}
        self.aliases = self._load_aliases()
        self.keyword_processor = self._build_keyword_processor()
    
    @lru_cache(maxsize=1000)
    def _normalize(self, text: str) -> str:
        """Нормализация с кэшированием (без лемматизации)"""
        text = text.lower().strip()
        # Убираем организационно-правовые формы
        prefixes = ['ооо', 'оао', 'зао', 'пао', 'гк', 'ltd', 'llc', 'inc', 'corp']
        for prefix in prefixes:
            text = re.sub(rf'\b{prefix}\b', '', text)
        
        # Простая нормализация без лемматизации
        words = re.findall(r'\w+', text)
        normalized = []
        for word in words:
            if len(word) > 2 and word not in self.stop_words:
                normalized.append(word)
        
        return ' '.join(normalized)
    
    def _load_aliases(self) -> Dict[str, List[str]]:
        """Загрузка алиасов из YAML файла"""
        aliases_file = Path('aliases.yml')
        yaml_aliases = {}
        
        if aliases_file.exists():
            with open(aliases_file, 'r', encoding='utf-8') as f:
                yaml_aliases = yaml.safe_load(f) or {}
        
        # Строим окончательный словарь алиасов
        result = {}
        for company in self.companies:
            normalized = self._normalize(company)
            aliases_list = [company, normalized, company.lower()]
            
            # Добавляем из YAML если есть
            if company in yaml_aliases:
                aliases_list.extend(yaml_aliases[company])
            
            # Убираем дубликаты и пустые строки
            result[company] = list(set(alias for alias in aliases_list if alias and len(alias) > 2))
        
        return result
    
    def _build_keyword_processor(self) -> KeywordProcessor:
        """Строим KeywordProcessor для быстрого поиска"""
        kp = KeywordProcessor(case_sensitive=False)
        
        for company, aliases_list in self.aliases.items():
            for alias in aliases_list:
                # Избегаем коротких алиасов и однобуквенных слов
                if len(alias) > 3 and not re.match(r'^[a-z]\d+$', alias.lower()):
                    kp.add_keyword(alias, company)
        
        return kp
    
    def _extract_company_lines(self, text: str) -> List[str]:
        """Извлекает строки с упоминанием компаний"""
        company_lines = []
        lines = text.split('\n')
        
        for line in lines:
            if re.search(r'компания[\s:]+|работодатель[\s:]+|employer[\s:]+', line, re.IGNORECASE):
                company_lines.append(line.strip())
        
        return company_lines
    
    def find_companies_exact(self, text: str) -> Set[str]:
        """Точный поиск через FlashText + проверка границ слов"""
        found = set()
        
        # Быстрый поиск через FlashText
        flash_matches = self.keyword_processor.extract_keywords(text)
        
        # Проверяем каждое совпадение на границы слов
        for company in flash_matches:
            for alias in self.aliases[company]:
                if len(alias) > 3 and re.search(rf'\b{re.escape(alias)}\b', text, re.IGNORECASE):
                    # Дополнительная проверка - алиас должен быть рядом со словом "компания"
                    context_pattern = rf'(компания[\s:]*.*?{re.escape(alias)}|{re.escape(alias)}.*?компания)'
                    if re.search(context_pattern, text, re.IGNORECASE) or len(alias) > 6:
                        found.add(company)
                        break
        
        return found
    
    def find_companies_fuzzy(self, text: str, threshold: int = 90) -> Tuple[Set[str], List[Dict]]:
        """Fuzzy поиск только по строкам с 'Компания:'"""
        found = set()
        ambiguous = []
        
        company_lines = self._extract_company_lines(text)
        if not company_lines:
            return found, ambiguous
        
        # Создаем пул всех алиасов для поиска
        alias_to_company = {}
        for company, aliases_list in self.aliases.items():
            for alias in aliases_list:
                alias_to_company[alias] = company
        
        alias_pool = list(alias_to_company.keys())
        
        # Fuzzy поиск по каждой строке с компанией
        for line in company_lines:
            normalized_line = self._normalize(line)
            matches = process.extract(normalized_line, alias_pool, 
                                    scorer=fuzz.partial_ratio, limit=3)
            
            for alias, score, _ in matches:
                if score >= threshold:
                    company = alias_to_company[alias]
                    found.add(company)
                    
                    # Логируем сомнительные случаи
                    if 90 <= score <= 95:
                        ambiguous.append({
                            'company': company,
                            'alias': alias,
                            'score': score,
                            'line': line,
                            'normalized_line': normalized_line
                        })
        
        return found, ambiguous

class InterviewExtractor:
    def __init__(self, companies_file: str, interviews_file: str):
        self.companies = self._load_companies(companies_file)
        self.matcher = CompanyMatcher(self.companies)
        self.interviews_text = self._load_interviews(interviews_file)
        self.ambiguous_cases = []
        
    def _load_companies(self, file_path: str) -> List[str]:
        """Загружаем список компаний"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_interviews(self, file_path: str) -> str:
        """Загружаем текст с записями собеседований"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _normalize_block_for_hash(self, text: str) -> str:
        """Нормализация блока для хэширования (убираем лишние пробелы)"""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _segment_blocks(self) -> List[str]:
        """Сегментация блоков в 3 шага"""
        text = self.interviews_text
        
        # Шаг 1: split по датам в начале строки
        date_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        blocks = re.split(date_pattern, text, flags=re.MULTILINE)
        
        # Объединяем даты с содержимым
        merged_blocks = []
        current_timestamp = None
        
        for block in blocks:
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', block):
                current_timestamp = block
            elif current_timestamp and block.strip():
                merged_blocks.append(f"{current_timestamp}\n{block}")
                current_timestamp = None
        
        # Шаг 2: дополнительное разбиение длинных блоков
        final_blocks = []
        for block in merged_blocks:
            if len(block) > 10000:  # Если блок слишком длинный
                # Разбиваем по "Компания:" или "Этап"
                sub_blocks = re.split(r'\n(?=Компания[\s:]|Этап)', block)
                final_blocks.extend(sub_blocks)
            else:
                final_blocks.append(block)
        
        # Шаг 3: fallback разбиение по двойным переносам
        result_blocks = []
        for block in final_blocks:
            if len(block) > 5000 and '\n\n' in block:
                sub_blocks = re.split(r'\n{2,}', block)
                result_blocks.extend([b.strip() for b in sub_blocks if b.strip()])
            else:
                result_blocks.append(block.strip())
        
        return [b for b in result_blocks if len(b) > 10]
    
    def _parse_interview_blocks(self) -> List[InterviewRecord]:
        """Разбиваем текст на блоки интервью с улучшенной сегментацией"""
        records = []
        blocks = self._segment_blocks()
        
        for block in blocks:
            # Извлекаем timestamp из начала блока
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', block)
            timestamp = timestamp_match.group() if timestamp_match else "unknown"
            
            # Нормализуем для хэширования
            normalized_content = self._normalize_block_for_hash(block)
            record_hash = hashlib.md5(normalized_content.encode('utf-8')).hexdigest()
            
            records.append(InterviewRecord(
                timestamp=timestamp,
                company="",  # Будет заполнено позже
                content=block,
                hash=record_hash
            ))
        
        return records
    
    def extract_company_interviews(self) -> Dict[str, List[InterviewRecord]]:
        """Извлекаем записи собеседований для каждой компании"""
        records = self._parse_interview_blocks()
        company_interviews = defaultdict(list)
        processed_hashes = set()
        
        print(f"Найдено {len(records)} блоков для анализа")
        
        for record in tqdm(records, desc="Анализ блоков"):
            # Избегаем дубликатов
            if record.hash in processed_hashes:
                continue
            processed_hashes.add(record.hash)
            
            # Сначала точный поиск
            exact_companies = self.matcher.find_companies_exact(record.content)
            
            if exact_companies:
                # Если нашли точные совпадения
                for company in exact_companies:
                    record.company = company
                    company_interviews[company].append(record)
            else:
                # Если точных нет - пробуем fuzzy только по строкам с "Компания:"
                fuzzy_companies, ambiguous = self.matcher.find_companies_fuzzy(record.content)
                self.ambiguous_cases.extend(ambiguous)
                
                for company in fuzzy_companies:
                    record.company = company
                    company_interviews[company].append(record)
        
        return dict(company_interviews)
    
    def generate_report(self, output_file: str):
        """Генерируем отчет"""
        company_interviews = self.extract_company_interviews()
        
        # Готовим результат
        result = []
        total_matches = 0
        
        for company in self.companies:
            interviews = company_interviews.get(company, [])
            count = len(interviews)
            total_matches += count
            
            if count > 0:
                result.append({
                    "company": company,
                    "count": count,
                    "records": [
                        {
                            "timestamp": record.timestamp,
                            "content": record.content[:500] + "..." if len(record.content) > 500 else record.content,
                            "full_content": record.content
                        }
                        for record in interviews
                    ]
                })
        
        # Сортируем по количеству записей (по убыванию)
        result.sort(key=lambda x: x['count'], reverse=True)
        
        # Сохраняем результат
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Сохраняем сомнительные случаи
        if self.ambiguous_cases:
            ambiguous_file = output_file.replace('.json', '_ambiguous.json')
            with open(ambiguous_file, 'w', encoding='utf-8') as f:
                json.dump(self.ambiguous_cases, f, ensure_ascii=False, indent=2)
            print(f"⚠️  Сомнительные случаи сохранены в: {ambiguous_file}")
        
        # Выводим статистику
        print(f"\n=== РЕЗУЛЬТАТЫ АНАЛИЗА ===")
        print(f"Всего компаний в списке: {len(self.companies)}")
        print(f"Найдено компаний с записями: {len(result)}")
        print(f"Общее количество записей: {total_matches}")
        print(f"Сомнительных случаев: {len(self.ambiguous_cases)}")
        print(f"\nТОП-10 компаний по количеству записей:")
        
        for i, item in enumerate(result[:10], 1):
            print(f"{i:2d}. {item['company']:30} - {item['count']:3d} записей")
        
        print(f"\nРезультат сохранен в: {output_file}")
        
        return result

def main():
    parser = argparse.ArgumentParser(description='Извлечение записей собеседований по компаниям')
    parser.add_argument('companies_json', help='JSON файл со списком компаний')
    parser.add_argument('interviews_txt', help='TXT файл с записями собеседований')
    parser.add_argument('--output', '-o', default='interview_matches.json', 
                       help='Выходной JSON файл (по умолчанию: interview_matches.json)')
    
    args = parser.parse_args()
    
    # Проверяем существование файлов
    if not Path(args.companies_json).exists():
        print(f"Ошибка: файл {args.companies_json} не найден")
        return
    
    if not Path(args.interviews_txt).exists():
        print(f"Ошибка: файл {args.interviews_txt} не найден")
        return
    
    # Запускаем извлечение
    extractor = InterviewExtractor(args.companies_json, args.interviews_txt)
    extractor.generate_report(args.output)

if __name__ == "__main__":
    main()
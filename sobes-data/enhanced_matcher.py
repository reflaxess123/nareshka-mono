#!/usr/bin/env python3
"""
ИСПРАВЛЕННАЯ версия скрипта для точного поиска записей собеседований.
Убраны ложные срабатывания, улучшена точность поиска.
"""

import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Tuple
import argparse
from dataclasses import dataclass

try:
    from flashtext import KeywordProcessor
    from rapidfuzz import process, fuzz
    from tqdm import tqdm
    import yaml
except ImportError as e:
    print(f"❌ Отсутствует зависимость: {e}")
    print("Установите: pip install flashtext rapidfuzz tqdm pyyaml")
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
        self.aliases = self._build_company_aliases()
        self.keyword_processor = self._build_keyword_processor()
        
    def _build_company_aliases(self) -> Dict[str, List[str]]:
        """Строим алиасы для компаний с фильтрацией проблемных"""
        aliases = {}
        
        # Загружаем из YAML если есть
        yaml_aliases = {}
        aliases_file = Path('aliases.yml')
        if aliases_file.exists():
            with open(aliases_file, 'r', encoding='utf-8') as f:
                yaml_aliases = yaml.safe_load(f) or {}
        
        for company in self.companies:
            company_aliases = []
            
            # Добавляем само название компании
            if len(company) > 3 and not self._is_problematic_name(company):
                company_aliases.append(company)
            
            # Добавляем нормализованное название
            normalized = self._normalize_company_name(company)
            if len(normalized) > 3 and normalized != company.lower():
                company_aliases.append(normalized)
            
            # Добавляем из YAML
            if company in yaml_aliases:
                for alias in yaml_aliases[company]:
                    if len(alias) > 3 and not self._is_problematic_name(alias):
                        company_aliases.append(alias)
            
            # Убираем дубликаты
            aliases[company] = list(set(company_aliases))
        
        return aliases
    
    def _is_problematic_name(self, name: str) -> bool:
        """Проверяет, является ли название проблемным (дающим ложные срабатывания)"""
        name_lower = name.lower()
        
        # Слишком короткие названия
        if len(name) <= 3:
            return True
        
        # Паттерны типа "T2", "X5", "S8" и т.п.
        if re.match(r'^[a-z]\d+$', name_lower):
            return True
        
        # Слишком общие слова
        common_words = {'company', 'group', 'tech', 'it', 'система', 'технологии', 'банк'}
        if name_lower in common_words:
            return True
        
        return False
    
    def _normalize_company_name(self, name: str) -> str:
        """Нормализация названия компании"""
        name = name.lower().strip()
        
        # Убираем организационно-правовые формы
        prefixes = ['ооо', 'оао', 'зао', 'пао', 'гк', 'ltd', 'llc', 'inc', 'corp']
        for prefix in prefixes:
            name = re.sub(rf'\b{prefix}\b', '', name)
        
        # Убираем лишние символы и пробелы
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _build_keyword_processor(self) -> KeywordProcessor:
        """Строим KeywordProcessor только для надежных алиасов"""
        kp = KeywordProcessor(case_sensitive=False)
        
        for company, aliases_list in self.aliases.items():
            for alias in aliases_list:
                if len(alias) > 4:  # Только длинные алиасы для точности
                    kp.add_keyword(alias, company)
        
        return kp
    
    def _extract_company_lines(self, text: str) -> List[str]:
        """Извлекает строки с упоминанием компаний"""
        company_lines = []
        lines = text.split('\n')
        
        for line in lines:
            # Ищем строки с явным указанием компании
            if re.search(r'компания[\s:]+', line, re.IGNORECASE):
                company_lines.append(line.strip())
        
        return company_lines
    
    def find_companies_in_text(self, text: str) -> Set[str]:
        """Находим компании с высокой точностью"""
        found = set()
        
        # 1. Сначала ищем в строках с "Компания:"
        company_lines = self._extract_company_lines(text)
        
        for line in company_lines:
            # Точный поиск по строкам с компанией
            for company, aliases_list in self.aliases.items():
                for alias in aliases_list:
                    if len(alias) > 4:  # Только длинные алиасы
                        pattern = rf'\b{re.escape(alias)}\b'
                        if re.search(pattern, line, re.IGNORECASE):
                            found.add(company)
                            break
        
        # 2. Если не нашли в строках с "Компания:", ищем через FlashText по всему тексту
        if not found:
            flash_matches = self.keyword_processor.extract_keywords(text)
            for company in flash_matches:
                # Дополнительная проверка контекста
                for alias in self.aliases[company]:
                    if len(alias) > 4:
                        pattern = rf'\b{re.escape(alias)}\b'
                        if re.search(pattern, text, re.IGNORECASE):
                            # Проверяем, что алиас находится в разумном контексте
                            context_window = 100
                            matches = list(re.finditer(pattern, text, re.IGNORECASE))
                            for match in matches:
                                start = max(0, match.start() - context_window)
                                end = min(len(text), match.end() + context_window)
                                context = text[start:end].lower()
                                
                                # Контекст должен содержать слова, связанные с собеседованием
                                interview_keywords = ['собеседование', 'интервью', 'вакансия', 'работа', 'зп', 'этап', 'технич']
                                if any(keyword in context for keyword in interview_keywords):
                                    found.add(company)
                                    break
        
        return found

class InterviewExtractor:
    def __init__(self, companies_file: str, interviews_file: str):
        self.companies = self._load_companies(companies_file)
        self.matcher = CompanyMatcher(self.companies)
        self.interviews_text = self._load_interviews(interviews_file)
        
    def _load_companies(self, file_path: str) -> List[str]:
        """Загружаем список компаний"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_interviews(self, file_path: str) -> str:
        """Загружаем текст с записями собеседований"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _segment_blocks(self) -> List[str]:
        """Улучшенная сегментация блоков"""
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
            if len(block) > 10000:
                # Разбиваем по "Компания:" или "Этап"
                sub_blocks = re.split(r'\n(?=Компания[\s:]|Этап)', block)
                final_blocks.extend(sub_blocks)
            else:
                final_blocks.append(block)
        
        # Фильтруем слишком короткие блоки
        return [b.strip() for b in final_blocks if len(b.strip()) > 50]
    
    def _normalize_for_hash(self, text: str) -> str:
        """Нормализация для хэширования"""
        return re.sub(r'\s+', ' ', text.strip())
    
    def extract_company_interviews(self) -> Dict[str, List[InterviewRecord]]:
        """Извлекаем записи собеседований"""
        blocks = self._segment_blocks()
        company_interviews = defaultdict(list)
        processed_hashes = set()
        
        print(f"Найдено {len(blocks)} блоков для анализа")
        
        for block in tqdm(blocks, desc="Анализ блоков"):
            # Создаем хэш для дедупликации
            normalized_content = self._normalize_for_hash(block)
            block_hash = hashlib.md5(normalized_content.encode('utf-8')).hexdigest()
            
            if block_hash in processed_hashes:
                continue
            processed_hashes.add(block_hash)
            
            # Извлекаем timestamp
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', block)
            timestamp = timestamp_match.group() if timestamp_match else "unknown"
            
            # Ищем компании
            found_companies = self.matcher.find_companies_in_text(block)
            
            for company in found_companies:
                record = InterviewRecord(
                    timestamp=timestamp,
                    company=company,
                    content=block,
                    hash=block_hash
                )
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
        
        # Сортируем по количеству записей
        result.sort(key=lambda x: x['count'], reverse=True)
        
        # Сохраняем результат
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Статистика
        print(f"\n=== РЕЗУЛЬТАТЫ АНАЛИЗА ===")
        print(f"Всего компаний в списке: {len(self.companies)}")
        print(f"Найдено компаний с записями: {len(result)}")
        print(f"Общее количество записей: {total_matches}")
        print(f"\nТОП-15 компаний по количеству записей:")
        
        for i, item in enumerate(result[:15], 1):
            print(f"{i:2d}. {item['company']:30} - {item['count']:3d} записей")
        
        print(f"\nРезультат сохранен в: {output_file}")
        
        return result

def main():
    parser = argparse.ArgumentParser(description='Извлечение записей собеседований по компаниям (исправленная версия)')
    parser.add_argument('companies_json', help='JSON файл со списком компаний')
    parser.add_argument('interviews_txt', help='TXT файл с записями собеседований')
    parser.add_argument('--output', '-o', default='interview_results_fixed.json', 
                       help='Выходной JSON файл')
    
    args = parser.parse_args()
    
    # Проверяем файлы
    if not Path(args.companies_json).exists():
        print(f"❌ Файл {args.companies_json} не найден")
        return
    
    if not Path(args.interviews_txt).exists():
        print(f"❌ Файл {args.interviews_txt} не найден")
        return
    
    # Запускаем
    try:
        extractor = InterviewExtractor(args.companies_json, args.interviews_txt)
        extractor.generate_report(args.output)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1

if __name__ == "__main__":
    main()
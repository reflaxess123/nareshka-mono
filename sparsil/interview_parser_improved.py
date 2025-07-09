import json
import re
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime

class ImprovedInterviewParser:
    def __init__(self, json_file: str):
        """Инициализация парсера с загрузкой данных"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.messages = self.data['messages']
        self.parsed_interviews = []
        
        # Список слов-исключений для фильтрации мусора
        self.garbage_keywords = [
            'напиши', 'придирается', 'спрашивает', 'почему', 'как', 'что',
            'где', 'когда', 'зачем', 'какой', 'какая', 'какие', 'сколько'
        ]
        
        # Паттерны для очистки названий компаний
        self.cleanup_patterns = [
            r'\s*\(.*?\)\s*$',  # Убираем скобки в конце
            r'\s*финал\s*$',    # Убираем "финал"
            r'\s*\d+\s*этап\s*$',  # Убираем "1 этап", "2 этап"
            r'^\d+\.\s*',       # Убираем номера в начале "1. "
            r'\s*\d{2}\.\d{2}\s*$',  # Убираем даты типа "08.07"
            r'\s*техничка\s*$', # Убираем "техничка"
            r'\s*встреча\s+с\s+\w+\s*$',  # Убираем "встреча с лидом"
        ]
        
    def is_garbage_message(self, text: str) -> bool:
        """Проверяет, является ли сообщение мусором"""
        first_line = text.split('\n')[0].strip().lower()
        
        # Проверяем на хэштеги
        if first_line.startswith('#'):
            return True
            
        # Проверяем на код в первой строке
        if first_line.startswith('```') or first_line.startswith('`'):
            return True
            
        # Проверяем на мусорные ключевые слова
        for keyword in self.garbage_keywords:
            if keyword in first_line:
                return True
                
        # Проверяем длину - слишком короткие названия подозрительны
        if len(first_line) < 3:
            return True
            
        return False
        
    def extract_company_name(self, text: str) -> Optional[str]:
        """Извлекает название компании из первой строки текста"""
        if not text.strip():
            return None
            
        # Проверяем на мусор
        if self.is_garbage_message(text):
            return None
            
        first_line = text.split('\n')[0].strip()
        
        # Паттерны для различных форматов названий компаний
        patterns = [
            r'^Компания[:\s]+(.+?)(?:\s*\n|$)',  # "Компания: Название"
            r'^Название компании\s*[-–:]\s*(.+?)(?:\s*\n|$)',  # "Название компании - Название"
            r'^[-–]\s*(.+?)(?:\s*\(|$)',  # "- Название (детали)"
            r'^(.+?)\s*\(.*?\)(?:\s*\n|$)',  # "Название (детали)" - но только если есть скобки
            r'^(.+?)(?:\s*\n|$)',  # Просто первая строка
        ]
        
        for pattern in patterns:
            match = re.search(pattern, first_line, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                
                # Очищаем от лишних символов и паттернов
                company = re.sub(r'[:\-–]+$', '', company).strip()
                
                # Применяем паттерны очистки
                for cleanup_pattern in self.cleanup_patterns:
                    company = re.sub(cleanup_pattern, '', company, flags=re.IGNORECASE).strip()
                
                # Проверяем финальное название
                if company and len(company) > 2 and not company.startswith('```'):
                    # Дополнительная проверка на мусор
                    if not any(keyword in company.lower() for keyword in self.garbage_keywords):
                        return company
        
        return None
    
    def is_continuation_message(self, current_msg: Dict, prev_msg: Dict) -> bool:
        """Проверяет, является ли сообщение продолжением предыдущего"""
        # Проверяем последовательные ID
        if current_msg['id'] == prev_msg['id'] + 1:
            # Проверяем, что от одного автора
            if current_msg.get('from_id') == prev_msg.get('from_id'):
                # Проверяем временной интервал (не более 10 минут)
                try:
                    curr_time = datetime.fromisoformat(current_msg['date'].replace('Z', '+00:00'))
                    prev_time = datetime.fromisoformat(prev_msg['date'].replace('Z', '+00:00'))
                    time_diff = (curr_time - prev_time).total_seconds()
                    
                    if time_diff <= 600:  # 10 минут
                        return True
                except:
                    pass
        return False
    
    def merge_continuation_messages(self) -> List[Dict]:
        """Объединяет растянутые сообщения в одно"""
        merged_messages = []
        i = 0
        
        while i < len(self.messages):
            current_msg = self.messages[i].copy()
            
            # Ищем продолжения
            j = i + 1
            while j < len(self.messages):
                if self.is_continuation_message(self.messages[j], self.messages[j-1]):
                    # Объединяем текст
                    current_msg['text'] += '\n' + self.messages[j]['text']
                    # Обновляем дату на последнюю
                    current_msg['date'] = self.messages[j]['date']
                    j += 1
                else:
                    break
            
            merged_messages.append(current_msg)
            i = j
            
        return merged_messages
    
    def clean_text(self, text: str) -> str:
        """Очищает текст от лишних символов и форматирования"""
        # Убираем лишние переносы строк
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Убираем лишние пробелы
        text = re.sub(r' {2,}', ' ', text)
        # Убираем пробелы в начале и конце строк
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines).strip()
    
    def extract_salary_info(self, text: str) -> Optional[str]:
        """Извлекает информацию о зарплате"""
        salary_patterns = [
            r'ЗП[:\s]*([^\n]+)',
            r'зарплата[:\s]*([^\n]+)',
            r'от\s+(\d+)\s*к',
            r'до\s+(\d+)\s*к',
            r'(\d+)\s*[-–]\s*(\d+)\s*к',
            r'(\d+)\s*к\s*руб',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_feedback_info(self, text: str) -> Optional[str]:
        """Извлекает информацию о фидбеке"""
        feedback_patterns = [
            r'фидбек[:\s]*([^\n]+)',
            r'feedback[:\s]*([^\n]+)',
            r'(прошел|не прошел|отказ|принят)',
            r'успех собеса[:\s]*([^\n]+)',
        ]
        
        for pattern in feedback_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def parse_interviews(self) -> List[Dict]:
        """Основной метод парсинга интервью"""
        merged_messages = self.merge_continuation_messages()
        
        for msg in merged_messages:
            text = msg['text']
            company_name = self.extract_company_name(text)
            
            if company_name:
                # Извлекаем содержимое интервью (всё после первой строки)
                lines = text.split('\n')
                interview_content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                
                # Извлекаем дополнительную информацию
                salary_info = self.extract_salary_info(text)
                feedback_info = self.extract_feedback_info(text)
                
                interview_data = {
                    'id': msg['id'],
                    'company_name': company_name,
                    'interview_content': self.clean_text(interview_content),
                    'full_text': self.clean_text(text),
                    'date': msg['date'],
                    'author': msg.get('from_username', 'Unknown'),
                    'author_id': msg.get('from_id'),
                    'message_length': len(text),
                    'has_code': '```' in text,
                    'has_salary': salary_info is not None,
                    'salary_info': salary_info,
                    'has_feedback': feedback_info is not None,
                    'feedback_info': feedback_info,
                    'question_count': len(re.findall(r'^\d+[\.\)]\s', text, re.MULTILINE)),
                    'task_count': text.lower().count('задача'),
                }
                
                self.parsed_interviews.append(interview_data)
        
        return self.parsed_interviews
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику по данным"""
        if not self.parsed_interviews:
            self.parse_interviews()
            
        stats = {
            'total_interviews': len(self.parsed_interviews),
            'unique_companies': len(set(interview['company_name'] for interview in self.parsed_interviews)),
            'interviews_with_code': sum(1 for interview in self.parsed_interviews if interview['has_code']),
            'interviews_with_salary': sum(1 for interview in self.parsed_interviews if interview['has_salary']),
            'interviews_with_feedback': sum(1 for interview in self.parsed_interviews if interview['has_feedback']),
            'avg_questions_per_interview': sum(interview['question_count'] for interview in self.parsed_interviews) / len(self.parsed_interviews),
            'avg_tasks_per_interview': sum(interview['task_count'] for interview in self.parsed_interviews) / len(self.parsed_interviews),
            'top_companies': self._get_top_companies(),
            'authors_count': len(set(interview['author'] for interview in self.parsed_interviews)),
        }
        
        return stats
    
    def _get_top_companies(self) -> List[Dict]:
        """Возвращает топ компаний по количеству интервью"""
        company_counts = {}
        for interview in self.parsed_interviews:
            company = interview['company_name']
            company_counts[company] = company_counts.get(company, 0) + 1
        
        return sorted(
            [{'company': company, 'count': count} for company, count in company_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:15]
    
    def export_to_csv(self, filename: str = 'improved_interviews.csv'):
        """Экспортирует данные в CSV"""
        if not self.parsed_interviews:
            self.parse_interviews()
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if self.parsed_interviews:
                fieldnames = self.parsed_interviews[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.parsed_interviews)
        
        print(f"Улучшенные данные экспортированы в {filename}")
    
    def export_to_json(self, filename: str = 'improved_interviews.json'):
        """Экспортирует данные в JSON"""
        if not self.parsed_interviews:
            self.parse_interviews()
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.parsed_interviews, f, ensure_ascii=False, indent=2)
        
        print(f"Улучшенные данные экспортированы в {filename}")
    
    def export_companies_only(self, filename: str = 'improved_companies_list.txt'):
        """Экспортирует только список компаний"""
        if not self.parsed_interviews:
            self.parse_interviews()
            
        companies = sorted(set(interview['company_name'] for interview in self.parsed_interviews))
        
        with open(filename, 'w', encoding='utf-8') as f:
            for company in companies:
                f.write(f"{company}\n")
        
        print(f"Улучшенный список компаний экспортирован в {filename}")
    
    def export_statistics(self, filename: str = 'improved_statistics.txt'):
        """Экспортирует статистику в текстовый файл"""
        stats = self.get_statistics()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== УЛУЧШЕННАЯ СТАТИСТИКА СОБЕСЕДОВАНИЙ ===\n\n")
            f.write(f"Всего интервью: {stats['total_interviews']}\n")
            f.write(f"Уникальных компаний: {stats['unique_companies']}\n")
            f.write(f"С кодом: {stats['interviews_with_code']}\n")
            f.write(f"С зарплатой: {stats['interviews_with_salary']}\n")
            f.write(f"С фидбеком: {stats['interviews_with_feedback']}\n")
            f.write(f"Среднее количество вопросов: {stats['avg_questions_per_interview']:.1f}\n")
            f.write(f"Среднее количество задач: {stats['avg_tasks_per_interview']:.1f}\n")
            f.write(f"Авторов: {stats['authors_count']}\n\n")
            
            f.write("=== ТОП 15 КОМПАНИЙ ===\n")
            for item in stats['top_companies']:
                f.write(f"{item['company']}: {item['count']} интервью\n")
        
        print(f"Улучшенная статистика экспортирована в {filename}")

# Пример использования
if __name__ == "__main__":
    parser = ImprovedInterviewParser('telegram_topic_messages.json')
    
    # Парсим данные
    interviews = parser.parse_interviews()
    
    # Выводим статистику
    stats = parser.get_statistics()
    print("=== УЛУЧШЕННАЯ СТАТИСТИКА ===")
    print(f"Всего интервью: {stats['total_interviews']}")
    print(f"Уникальных компаний: {stats['unique_companies']}")
    print(f"С кодом: {stats['interviews_with_code']}")
    print(f"С зарплатой: {stats['interviews_with_salary']}")
    print(f"С фидбеком: {stats['interviews_with_feedback']}")
    print(f"Среднее количество вопросов: {stats['avg_questions_per_interview']:.1f}")
    print(f"Среднее количество задач: {stats['avg_tasks_per_interview']:.1f}")
    print(f"Авторов: {stats['authors_count']}")
    
    print("\n=== ТОП 15 КОМПАНИЙ ===")
    for item in stats['top_companies']:
        print(f"{item['company']}: {item['count']} интервью")
    
    # Экспортируем в разные форматы
    parser.export_to_csv()
    parser.export_to_json()
    parser.export_companies_only()
    parser.export_statistics() 
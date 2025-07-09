import json
import re
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime

class FinalInterviewParser:
    def __init__(self, json_file: str):
        """Инициализация парсера с загрузкой данных"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.messages = self.data['messages']
        self.parsed_interviews = []
        
    def clean_company_name(self, company: str) -> str:
        """Максимально очищает название компании"""
        if not company:
            return company
            
        # Убираем звездочки и кавычки
        company = re.sub(r'[*"]+', '', company)
        
        # Убираем хэштеги
        company = re.sub(r'^#', '', company)
        
        # Убираем номера в начале
        company = re.sub(r'^\d+\.\s*', '', company)
        
        # Убираем этапы и финалы
        company = re.sub(r'\s*\(.*?этап.*?\)', '', company, flags=re.IGNORECASE)
        company = re.sub(r'\s*\d+\s*этап\s*', '', company, flags=re.IGNORECASE)
        company = re.sub(r'\s*финал\s*$', '', company, flags=re.IGNORECASE)
        company = re.sub(r'\s*техничка\s*$', '', company, flags=re.IGNORECASE)
        
        # Убираем даты
        company = re.sub(r'\s*\d{2}\.\d{2}\s*$', '', company)
        
        # Убираем "встреча с..."
        company = re.sub(r'\s*встреча\s+с\s+\w+\s*$', '', company, flags=re.IGNORECASE)
        
        # Убираем "Название компании:"
        company = re.sub(r'^Название компании\s*[-:]\s*', '', company, flags=re.IGNORECASE)
        
        # Убираем лишние символы в конце
        company = re.sub(r'[:\-–.]+$', '', company)
        
        # Убираем лишние пробелы
        company = re.sub(r'\s+', ' ', company).strip()
        
        return company
    
    def extract_company_name(self, text: str) -> Optional[str]:
        """Извлекает название компании из первой строки текста"""
        if not text.strip():
            return None
            
        first_line = text.split('\n')[0].strip()
        
        # Фильтруем мусор
        if (first_line.startswith('```') or 
            first_line.startswith('#') or
            len(first_line) < 3 or
            any(word in first_line.lower() for word in ['напиши', 'придирается', 'спрашивает', 'почему так'])):
            return None
        
        # Паттерны для извлечения названия
        patterns = [
            r'^Компания[:\s]+(.+?)(?:\s*\n|$)',
            r'^Название компании\s*[-–:]\s*(.+?)(?:\s*\n|$)',
            r'^[-–]\s*(.+?)(?:\s*\n|$)',
            r'^(.+?)(?:\s*\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, first_line, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                company = self.clean_company_name(company)
                
                if company and len(company) > 2:
                    return company
        
        return None
    
    def is_continuation_message(self, current_msg: Dict, prev_msg: Dict) -> bool:
        """Проверяет, является ли сообщение продолжением предыдущего"""
        if current_msg['id'] == prev_msg['id'] + 1:
            if current_msg.get('from_id') == prev_msg.get('from_id'):
                try:
                    curr_time = datetime.fromisoformat(current_msg['date'].replace('Z', '+00:00'))
                    prev_time = datetime.fromisoformat(prev_msg['date'].replace('Z', '+00:00'))
                    time_diff = (curr_time - prev_time).total_seconds()
                    return time_diff <= 600  # 10 минут
                except:
                    pass
        return False
    
    def merge_continuation_messages(self) -> List[Dict]:
        """Объединяет растянутые сообщения в одно"""
        merged_messages = []
        i = 0
        
        while i < len(self.messages):
            current_msg = self.messages[i].copy()
            
            j = i + 1
            while j < len(self.messages):
                if self.is_continuation_message(self.messages[j], self.messages[j-1]):
                    current_msg['text'] += '\n' + self.messages[j]['text']
                    current_msg['date'] = self.messages[j]['date']
                    j += 1
                else:
                    break
            
            merged_messages.append(current_msg)
            i = j
            
        return merged_messages
    
    def parse_interviews(self) -> List[Dict]:
        """Основной метод парсинга интервью"""
        merged_messages = self.merge_continuation_messages()
        
        for msg in merged_messages:
            text = msg['text']
            company_name = self.extract_company_name(text)
            
            if company_name:
                lines = text.split('\n')
                interview_content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                
                # Извлекаем зарплату
                salary_match = re.search(r'ЗП[:\s]*([^\n]+)', text, re.IGNORECASE)
                salary_info = salary_match.group(1).strip() if salary_match else None
                
                # Извлекаем фидбек
                feedback_patterns = [
                    r'фидбек[:\s]*([^\n]+)',
                    r'успех собеса[:\s]*([^\n]+)',
                    r'(прошел|не прошел|отказ|принят)',
                ]
                feedback_info = None
                for pattern in feedback_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        feedback_info = match.group(1).strip()
                        break
                
                interview_data = {
                    'id': msg['id'],
                    'company_name': company_name,
                    'interview_content': interview_content,
                    'full_text': text,
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
            
        company_counts = {}
        for interview in self.parsed_interviews:
            company = interview['company_name']
            company_counts[company] = company_counts.get(company, 0) + 1
        
        top_companies = sorted(
            [{'company': company, 'count': count} for company, count in company_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:20]
        
        stats = {
            'total_interviews': len(self.parsed_interviews),
            'unique_companies': len(company_counts),
            'interviews_with_code': sum(1 for i in self.parsed_interviews if i['has_code']),
            'interviews_with_salary': sum(1 for i in self.parsed_interviews if i['has_salary']),
            'interviews_with_feedback': sum(1 for i in self.parsed_interviews if i['has_feedback']),
            'avg_questions_per_interview': sum(i['question_count'] for i in self.parsed_interviews) / len(self.parsed_interviews),
            'avg_tasks_per_interview': sum(i['task_count'] for i in self.parsed_interviews) / len(self.parsed_interviews),
            'top_companies': top_companies,
            'authors_count': len(set(i['author'] for i in self.parsed_interviews)),
        }
        
        return stats
    
    def export_all(self):
        """Экспортирует все данные в разные форматы"""
        if not self.parsed_interviews:
            self.parse_interviews()
        
        # CSV
        with open('final_interviews.csv', 'w', newline='', encoding='utf-8') as csvfile:
            if self.parsed_interviews:
                fieldnames = self.parsed_interviews[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.parsed_interviews)
        
        # JSON
        with open('final_interviews.json', 'w', encoding='utf-8') as f:
            json.dump(self.parsed_interviews, f, ensure_ascii=False, indent=2)
        
        # Список компаний
        companies = sorted(set(i['company_name'] for i in self.parsed_interviews))
        with open('final_companies_list.txt', 'w', encoding='utf-8') as f:
            for company in companies:
                f.write(f"{company}\n")
        
        # Статистика
        stats = self.get_statistics()
        with open('final_statistics.txt', 'w', encoding='utf-8') as f:
            f.write("=== ФИНАЛЬНАЯ СТАТИСТИКА СОБЕСЕДОВАНИЙ ===\n\n")
            f.write(f"Всего интервью: {stats['total_interviews']}\n")
            f.write(f"Уникальных компаний: {stats['unique_companies']}\n")
            f.write(f"С кодом: {stats['interviews_with_code']}\n")
            f.write(f"С зарплатой: {stats['interviews_with_salary']}\n")
            f.write(f"С фидбеком: {stats['interviews_with_feedback']}\n")
            f.write(f"Среднее количество вопросов: {stats['avg_questions_per_interview']:.1f}\n")
            f.write(f"Среднее количество задач: {stats['avg_tasks_per_interview']:.1f}\n")
            f.write(f"Авторов: {stats['authors_count']}\n\n")
            
            f.write("=== ТОП 20 КОМПАНИЙ ===\n")
            for item in stats['top_companies']:
                f.write(f"{item['company']}: {item['count']} интервью\n")
        
        print("Все файлы экспортированы:")
        print("- final_interviews.csv")
        print("- final_interviews.json") 
        print("- final_companies_list.txt")
        print("- final_statistics.txt")

# Использование
if __name__ == "__main__":
    parser = FinalInterviewParser('telegram_topic_messages.json')
    
    # Парсим данные
    interviews = parser.parse_interviews()
    
    # Выводим статистику
    stats = parser.get_statistics()
    print("=== ФИНАЛЬНАЯ СТАТИСТИКА ===")
    print(f"Всего интервью: {stats['total_interviews']}")
    print(f"Уникальных компаний: {stats['unique_companies']}")
    print(f"С кодом: {stats['interviews_with_code']}")
    print(f"С зарплатой: {stats['interviews_with_salary']}")
    print(f"С фидбеком: {stats['interviews_with_feedback']}")
    print(f"Среднее количество вопросов: {stats['avg_questions_per_interview']:.1f}")
    print(f"Среднее количество задач: {stats['avg_tasks_per_interview']:.1f}")
    print(f"Авторов: {stats['authors_count']}")
    
    print("\n=== ТОП 20 КОМПАНИЙ ===")
    for item in stats['top_companies']:
        print(f"{item['company']}: {item['count']} интервью")
    
    # Экспортируем всё
    parser.export_all() 
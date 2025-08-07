import json
import requests
import time
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalInterviewProcessor:
    def __init__(self, proxy_api_key: str):
        self.proxy_api_key = proxy_api_key
        self.proxy_api_url = "https://api.proxyapi.ru/openai/v1/chat/completions"
        self.model = "gpt-4.1-mini"
        self.headers = {
            "Authorization": f"Bearer {self.proxy_api_key}",
            "Content-Type": "application/json"
        }
        
        self.prompt_template = """Ты - эксперт по анализу IT-собеседований. Извлеки ВСЕ отдельные вопросы и задачи из текста интервью.

КРИТИЧЕСКИ ВАЖНО:
- Каждый вопрос = отдельная строка  
- Каждая задача = отдельная строка
- НЕ пропускай ничего и НЕ придумывай детали
- Если ссылка на другие задачи ("отсюда", "с этого собеса") - пиши как есть, НЕ придумывай
- question_text должен быть КОРОТКИМ (максимум 70 символов)
- Определи компанию из текста 
- Извлеки дату из текста в формате YYYY-MM-DD
- Возвращай ТОЛЬКО чистый CSV БЕЗ ```csv``` блоков и БЕЗ заголовка

CSV ФОРМАТ:
id,question_text,company,category,difficulty,date

КАТЕГОРИИ: algorithms,frontend,backend,system_design,soft_skills
СЛОЖНОСТЬ: junior,middle,senior

ПРИМЕРЫ:
q1,"Реализуйте функцию debounce",Яндекс,frontend,middle,2025-07-18
q2,"Что такое замыкания",Сбер,frontend,junior,2025-07-15
q3,"Расскажи про опыт",Тинькофф,soft_skills,junior,2025-07-10

ОБРАБОТАЙ:
{full_content}"""

    def send_to_llm(self, content: str, company: str) -> str:
        """Отправляет контент в LLM и возвращает CSV"""
        prompt = self.prompt_template.format(full_content=content)
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0,
            "max_tokens": 2000
        }
        
        try:
            logger.info(f"Отправка запроса для компании {company}")
            response = requests.post(
                self.proxy_api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                csv_content = result['choices'][0]['message']['content'].strip()
                logger.info(f"Успешно обработан батч для {company}")
                return csv_content
            else:
                logger.error(f"Ошибка API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка отправки для {company}: {str(e)}")
            return None

    def process_company_batch(self, company_data: dict, output_dir: str) -> bool:
        """Обрабатывает все интервью одной компании"""
        company = company_data.get('company', 'unknown')
        records = company_data.get('records', [])
        
        logger.info(f"Обработка компании {company} ({len(records)} интервью)")
        
        # Создаем директорию если не существует
        os.makedirs(output_dir, exist_ok=True)
        
        all_csv_rows = []
        
        # Добавляем заголовок
        header = "id,question_text,company,category,difficulty,date"
        all_csv_rows.append(header)
        
        for i, record in enumerate(records):
            full_content = record.get('full_content', '')
            
            if not full_content.strip():
                logger.warning(f"Пустой контент для {company} интервью {i}")
                continue
            
            # Отправляем в LLM
            csv_result = self.send_to_llm(full_content, f"{company}_{i}")
            
            if csv_result:
                # Удаляем заголовок если он есть в ответе
                lines = csv_result.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('id,'):
                        all_csv_rows.append(line)
            
            # Пауза между запросами
            time.sleep(1)
        
        # Сохраняем результат
        output_file = os.path.join(output_dir, f"{company.replace(' ', '_')}.csv")
        
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                for row in all_csv_rows:
                    f.write(row + '\n')
            
            logger.info(f"Сохранен файл {output_file} с {len(all_csv_rows)-1} вопросами")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения файла {output_file}: {str(e)}")
            return False

    def process_all_companies(self, json_file: str, output_dir: str, limit: int = None):
        """Обрабатывает компании из JSON файла с опциональным лимитом"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                companies_data = json.load(f)
            
            # Ограничиваем количество если нужно
            if limit:
                companies_data = companies_data[:limit]
                logger.info(f"Обработка ограничена до {limit} компаний")
            
            logger.info(f"Загружено {len(companies_data)} компаний")
            
            processed_count = 0
            failed_count = 0
            
            for company_data in companies_data:
                success = self.process_company_batch(company_data, output_dir)
                
                if success:
                    processed_count += 1
                else:
                    failed_count += 1
                
                # Пауза между компаниями
                time.sleep(2)
            
            logger.info(f"Завершена обработка: {processed_count} успешно, {failed_count} ошибок")
            
        except Exception as e:
            logger.error(f"Ошибка обработки файла {json_file}: {str(e)}")

    def merge_csv_files(self, input_dir: str, output_file: str):
        """Объединяет все CSV файлы в один"""
        csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
        
        if not csv_files:
            logger.warning("Не найдено CSV файлов для объединения")
            return
        
        all_rows = []
        header_added = False
        
        for csv_file in csv_files:
            file_path = os.path.join(input_dir, csv_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Добавляем заголовок только один раз
                    if i == 0 and line.startswith('id,'):
                        if not header_added:
                            all_rows.append(line)
                            header_added = True
                        continue
                    
                    all_rows.append(line)
                    
            except Exception as e:
                logger.error(f"Ошибка чтения {csv_file}: {str(e)}")
        
        # Сохраняем объединенный файл
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                for row in all_rows:
                    f.write(row + '\n')
            
            logger.info(f"Создан объединенный файл {output_file} с {len(all_rows)-1} записями")
            
        except Exception as e:
            logger.error(f"Ошибка создания объединенного файла: {str(e)}")


def main():
    # КОНФИГУРАЦИЯ
    PROXY_API_KEY = "sk-yseNQGJXYUnn4YjrnwNJnwW7bsnwFg8K"
    INPUT_JSON = "C:/Users/refla/nareshka-mono/sobes-data/MASSIV_GROUPED.json"
    OUTPUT_DIR = "C:/Users/refla/nareshka-mono/sobes-data/processed_csv"
    FINAL_CSV = "C:/Users/refla/nareshka-mono/sobes-data/interview_questions_clean.csv"
    
    # ЛИМИТ ДЛЯ ТЕСТА (None = все компании)
    COMPANY_LIMIT = 3  # Для начала обработаем только первые 3 компании
    
    # Создаем процессор
    processor = FinalInterviewProcessor(PROXY_API_KEY)
    
    print("ЗАПУСК ФИНАЛЬНОЙ ОБРАБОТКИ")
    print(f"Лимит: {COMPANY_LIMIT} компаний" if COMPANY_LIMIT else "Все компании")
    
    # Обрабатываем компании
    processor.process_all_companies(INPUT_JSON, OUTPUT_DIR, COMPANY_LIMIT)
    
    # Объединяем все CSV в один файл
    processor.merge_csv_files(OUTPUT_DIR, FINAL_CSV)
    
    print("Обработка завершена!")
    print(f"Результат: {FINAL_CSV}")


if __name__ == "__main__":
    main()
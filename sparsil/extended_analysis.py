#!/usr/bin/env python3
"""
Расширенный анализ всех собранных данных из чата Frontend – TO THE JOB
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional

# Все собранные данные (расширенные)
EXTENDED_COLLECTED_MESSAGES = [
    # Первая порция данных (уже была)
    {"who": "budkakdomaputnic", "when": "2025-07-08 21:19:16", "text": "https://telemost.yandex.ru/j/13592002799790"},
    {"who": "theibd56", "when": "2025-07-08 18:00:35", "text": "Компания: Спортс (Sports.ru) \nСсылка на ваку: сам написал hr\nВилка: хз (назвал 250-300, сказали в вилке все норм)\n\n1. вопросы по опыту\n2. грейд разработчиков в команде?\n3. как код ревью проходит?\n4. если уйдешь с проекта как думаешь что станет работать хуже?\n5. представь что есть три открытые вкладки (потом вкладка на пк и тф) перечисли способы общения между ними?\n6. как разделяли зону ответственности на проектах?\n7. как по загруженности на проектах?\n8. с чем бы не хотел работать?\n9. что хотел бы поднатоскать/изучить?\n10. мы пишем на Vue тебе норм, как к такому относишься?\n\nЗадачи как здесь - https://t.me/c/2071074234/489/138602"},
    {"who": "danimaxi54", "when": "2025-07-08 17:48:29", "text": "задача из северстали"},
    {"who": "Mankeym", "when": "2025-07-08 17:47:41", "text": "//Дан массив ссылок: ['url1', 'url2', ...] и лимит одновременных запросов (limit) Необходимо реализовать функцию, которыя опросит урлы в том //порядку, в котором они идут в массиве, и вызовет callback с массивом ответов ['url1_answer', 'url2_anser', ...] так, чтобы в любой момент //времени выполнялось не более limit запросов (как только любой из них завершился, сразу же отправится следующий) Т.е. нужно реализовать шину с шириной равной limit.\n// доп. добавить мемоизацию\nfunction parallelLimit(urls, limit, callback) {\n    // Если limit больше количества URL, устанавливаем его равным длине массива URL\n    limit = Math.min(limit, urls.length);\n    \n    let results = new Array(urls.length);\n    let active = 0;\n    let index = 0;\n    const cache = new Map(); // Добавляем кэш для мемоизации\n    \n    function processNext() {\n        if (index >= urls.length && active === 0) {\n            callback(results);\n            return;\n        }\n        \n        while (index < urls.length && active < limit) {\n            const currIndex = index;\n            const url = urls[currIndex];\n            index++;\n            active++;\n            \n            // Проверяем наличие URL в кэше\n            if (cache.has(url)) {\n                // Если URL уже в кэше, берём результат оттуда\n                results[currIndex] = cache.get(url);\n                active--;\n                // Используем setTimeout для асинхронности и предотвращения переполнения стека\n                setTimeout(processNext, 0);\n            } else {\n                // Если URL нет в кэше, выполняем запрос\n                fetch(url)\n                    .then(response => {\n                        // Сохраняем ответ в кэш\n                        cache.set(url, response);\n                        results[currIndex] = response;\n                        active--;\n                        processNext();\n                    });\n            }\n        }\n    }\n    \n    // Обработка пустого массива URL\n    if (urls.length === 0) {\n        callback(results);\n        return;\n    }\n    \n    processNext();\n}"},
    
    # Новые данные из расширенного сбора
    {"who": "sentryDispatch", "when": "2025-07-08 17:30:43", "text": "Помогите в яндексе, на алгосах, сейчас отойду и не смогу помочь"},
    {"who": "sentryDispatch", "when": "2025-07-08 17:28:51", "text": "const getNodes = (tree, type) => {\n  let result = [];\n  const stack = [tree];  // Стек начинается с корня дерева\n\n  while (stack.length > 0) {\n    const node = stack.pop();  // Берем узел из стека\n\n    // Если тип узла совпадает с заданным, добавляем его в результат\n    if (node.type === type) {\n      result.push(node);  // Добавляем весь узел\n    }\n\n    // Если у узла есть дочерние элементы, добавляем их в стек\n    if (node.children) {\n      stack.push(...node.children);  // Добавляем все дочерние элементы\n    }\n  }\n\n  return result;\n};"},
    {"who": "VP262626", "when": "2025-07-08 17:27:59", "text": "Полученный от сервера HTML-документ браузер преобразует в DOM дерево.\n\n5. Загружаются и парсятся css-стили, формируется CSSOM (CSS Object Model). Загружается JS, если при парсинге html встречается script, то он блокирует дальнейший рендер, пока скрипт не отработает\n\n6. На основе DOM и CSSOM формируется дерево рендеринга, или render tree — набор объектов рендеринга. Render tree дублирует структуру DOM, но сюда не попадают невидимые элементы (например — <head>, или элементы со стилем display:none;). Также, каждая строка текста представлена в дереве рендеринга как отдельный renderer. Каждый объект рендеринга содержит соответствующий ему объект DOM и рассчитанный для этого объекта стиль. Проще говоря, render tree описывает визуальное представление DOM.\n\n 7. Для каждого элемента render tree рассчитывается положение на странице и его размеры, высота, ширина, происходит стадия layout.\n\n8. Происходит отрисовка каждого отдельного узла в браузере — painting."},
    {"who": "VP262626", "when": "2025-07-08 17:27:52", "text": "1. Браузер парсит URL и проверяет, есть ли соответствие между IP-адресом и доменом в своем кэше.\n\n- Если не находит в кэше браузера, то он обращается к операционной системе. Операционная система проверяет информацию в системном файле hosts, который содержит записи о соответствии доменов и IP-адресов.\n\n- Если и в системном файле hosts соответствия не найдено, браузер отправляет DNS запрос. Этот запрос содержит имя сервера, которое должно быть преобразовано в IP-адрес. Запрос отправляется к DNS-серверу, который возвращает IP-адрес сайта и полученный ответ на DNS запрос сохраняется в кэше.\n\n2. Когда IP адрес становится известен, браузер начинает установку соединения к серверу с помощью TCP рукопожатия. Выполняется обмен флагами в 3 этапа: SYN, SYN-ACK и ACK для согласования параметров и подтверждения соединения.\n\n3. Когда мы установили соединение, браузер отправляет GET запрос для получения HTML файла."},
    {"who": "sentryDispatch", "when": "2025-07-08 17:24:15", "text": "Временная сложность:\nВремя: O(N), где N — количество узлов в дереве.\n\nМы проходим по всем узлам только один раз, что даёт линейную сложность по времени.\n\nПространственная сложность:\nПамять: O(N), так как в худшем случае, если все узлы находятся на одном уровне (или в случае самой глубокой вложенности), стек может хранить все узлы одновременно."},
    {"who": "sentryDispatch", "when": "2025-07-08 17:16:28", "text": "Для улучшения решения задачи группировки анаграмм, мы можем использовать подсчёт частоты символов, вместо сортировки строки. Это подход позволит уменьшить сложность алгоритма.\n\nПодсчёт частоты символов:\nВместо того чтобы сортировать строку, можно посчитать частоту появления каждого символа.\n\nПолученная частота будет уникальной для всех анаграмм одного набора символов, поэтому такие слова можно будет группировать.\n\nКак это работает:\nКаждое слово превращаем в строку, которая будет представлять собой частоты символов (например, для \"трос\" и \"сорт\" это будет одинаковая строка).\n\nСтрока, представляющая частоты, используется как ключ для группировки анаграмм."},
    {"who": "sentryDispatch", "when": "2025-07-08 17:07:22", "text": "function groupAnagrams(list) {\n  const map = new Map();\n\n  for (const word of list) {\n    // Ключ — отсортированные буквы слова\n    const key = word.split('').sort().join('');\n    \n    // Добавляем слово в соответствующую группу\n    if (!map.has(key)) {\n      map.set(key, []);\n    }\n    map.get(key).push(word);\n  }\n\n  // Возвращаем массив сгруппированных слов\n  return Array.from(map.values());\n}"},
    {"who": "danimaxi54", "when": "2025-07-08 17:00:40", "text": "return pages.map(({id, titile, site_id}) => ({\n        id,\n        title,\n        site: sitesMap.get(site_id) // Достаем сайт из Map за O(1)\n    }));"},
    {"who": "danimaxi54", "when": "2025-07-08 16:59:10", "text": "// Создаем Map для быстрого доступа к сайтам по id\n    const sitesMap = new Map();\n    sites.forEach(site => sitesMap.set(site.id, site));"},
    {"who": "danimaxi54", "when": "2025-07-08 16:58:08", "text": "скажи я хочу оптимально сделать алгос"},
]

class ExtendedInterviewAnalyzer:
    def __init__(self):
        self.interview_keywords = [
            "собеседование", "интервью", "interview", "запись", "видео", 
            "аудио", "разбор", "ревью", "code review", "техническое",
            "задача", "алгоритм", "live coding", "скрин", "демо", "тест",
            "лайвкод", "вакансия", "компания", "hr", "вилка", "зарплата",
            "грейд", "опыт", "проект", "задачи", "сложность", "северсталь",
            "яндекс", "алгосы", "помогите"
        ]
        
        self.company_keywords = [
            "sports.ru", "спортс", "северсталь", "яндекс", "google", 
            "microsoft", "meta", "amazon", "netflix", "uber", "airbnb"
        ]
        
        self.algorithm_keywords = [
            "o(n)", "o(1)", "сложность", "алгоритм", "дерево", "стек",
            "хэш", "map", "массив", "итерация", "рекурсия", "dfs", "bfs"
        ]
        
        self.technical_keywords = [
            "react", "vue", "angular", "javascript", "typescript", "node.js",
            "python", "java", "c++", "golang", "rust", "algorithm", "алгоритм",
            "async", "await", "promise", "callback", "fetch", "api", "rest",
            "useeffect", "usestate", "component", "hook", "dom", "virtual dom",
            "html", "css", "cssom", "render tree", "layout", "painting"
        ]
    
    def extract_algorithms_and_tasks(self, messages: List[Dict]) -> List[Dict]:
        """Извлекает алгоритмические задачи и их решения"""
        algorithm_tasks = []
        
        for msg in messages:
            text = msg.get("text", "")
            
            # Проверяем, содержит ли сообщение алгоритмическую задачу
            is_algorithm = any(keyword in text.lower() for keyword in self.algorithm_keywords)
            has_code = bool(re.search(r'function|const|let|var|class|=>', text))
            has_complexity = bool(re.search(r'o\([^)]+\)', text.lower()))
            
            if is_algorithm or has_code or has_complexity:
                task_info = {
                    "author": msg.get("who", "Unknown"),
                    "timestamp": msg.get("when", ""),
                    "text": text,
                    "complexity_mentioned": has_complexity,
                    "has_code": has_code,
                    "task_type": self.classify_task_type(text),
                    "technologies": [tech for tech in self.technical_keywords if tech in text.lower()]
                }
                algorithm_tasks.append(task_info)
        
        return algorithm_tasks
    
    def classify_task_type(self, text: str) -> str:
        """Классифицирует тип задачи"""
        text_lower = text.lower()
        
        if "дерево" in text_lower or "tree" in text_lower:
            return "Tree Traversal"
        elif "анаграмм" in text_lower or "anagram" in text_lower:
            return "String Processing"
        elif "параллел" in text_lower or "parallel" in text_lower:
            return "Concurrency"
        elif "fetch" in text_lower or "запрос" in text_lower:
            return "Network/API"
        elif "map" in text_lower or "хэш" in text_lower:
            return "Data Structures"
        elif "браузер" in text_lower or "dom" in text_lower:
            return "Browser/Frontend"
        elif "singleton" in text_lower or "паттерн" in text_lower:
            return "Design Patterns"
        else:
            return "General Algorithm"
    
    def extract_interview_questions(self, messages: List[Dict]) -> List[Dict]:
        """Извлекает вопросы с собеседований"""
        interview_questions = []
        
        for msg in messages:
            text = msg.get("text", "")
            
            # Поиск нумерованных вопросов
            questions = re.findall(r'^\d+\.\s(.+)$', text, re.MULTILINE)
            
            if questions:
                interview_info = {
                    "author": msg.get("who", "Unknown"),
                    "timestamp": msg.get("when", ""),
                    "company": self.extract_company(text),
                    "salary": self.extract_salary(text),
                    "questions": questions,
                    "total_questions": len(questions)
                }
                interview_questions.append(interview_info)
        
        return interview_questions
    
    def extract_company(self, text: str) -> Optional[str]:
        """Извлекает название компании"""
        company_match = re.search(r'компания:\s*([^\\n]+)', text.lower())
        if company_match:
            return company_match.group(1).strip()
        
        for company in self.company_keywords:
            if company in text.lower():
                return company
        
        return None
    
    def extract_salary(self, text: str) -> Optional[str]:
        """Извлекает зарплатную вилку"""
        salary_match = re.search(r'(\d{2,3})-(\d{2,3})', text)
        if salary_match:
            return f"{salary_match.group(1)}-{salary_match.group(2)}k"
        return None
    
    def analyze_extended_data(self) -> Dict:
        """Проводит расширенный анализ всех данных"""
        print("🔍 Проводим расширенный анализ собранных данных...")
        
        # Извлекаем алгоритмические задачи
        algorithm_tasks = self.extract_algorithms_and_tasks(EXTENDED_COLLECTED_MESSAGES)
        
        # Извлекаем вопросы с собеседований
        interview_questions = self.extract_interview_questions(EXTENDED_COLLECTED_MESSAGES)
        
        # Группируем по авторам
        by_author = {}
        for msg in EXTENDED_COLLECTED_MESSAGES:
            author = msg.get("who", "Unknown")
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(msg)
        
        # Анализируем технические темы
        tech_discussions = self.analyze_technical_discussions(EXTENDED_COLLECTED_MESSAGES)
        
        # Статистика
        stats = {
            "total_messages": len(EXTENDED_COLLECTED_MESSAGES),
            "algorithm_tasks": len(algorithm_tasks),
            "interview_questions": len(interview_questions),
            "unique_authors": len(by_author),
            "tech_discussions": len(tech_discussions),
            "companies_mentioned": len(set(q["company"] for q in interview_questions if q["company"])),
            "analysis_date": datetime.now().isoformat()
        }
        
        return {
            "statistics": stats,
            "algorithm_tasks": algorithm_tasks,
            "interview_questions": interview_questions,
            "tech_discussions": tech_discussions,
            "messages_by_author": by_author,
            "all_messages": EXTENDED_COLLECTED_MESSAGES
        }
    
    def analyze_technical_discussions(self, messages: List[Dict]) -> List[Dict]:
        """Анализирует технические обсуждения"""
        tech_discussions = []
        
        for msg in messages:
            text = msg.get("text", "")
            tech_terms = [term for term in self.technical_keywords if term in text.lower()]
            
            if len(tech_terms) >= 3 or len(text) > 200:  # Длинные технические сообщения
                discussion = {
                    "author": msg.get("who", "Unknown"),
                    "timestamp": msg.get("when", ""),
                    "text": text,
                    "tech_terms": tech_terms,
                    "topic": self.classify_topic(text),
                    "is_explanation": "объясн" in text.lower() or "работает" in text.lower()
                }
                tech_discussions.append(discussion)
        
        return tech_discussions
    
    def classify_topic(self, text: str) -> str:
        """Классифицирует тему обсуждения"""
        text_lower = text.lower()
        
        if "браузер" in text_lower or "dom" in text_lower or "render" in text_lower:
            return "Browser Internals"
        elif "react" in text_lower or "vue" in text_lower or "component" in text_lower:
            return "Frontend Frameworks"
        elif "async" in text_lower or "promise" in text_lower or "fetch" in text_lower:
            return "Asynchronous Programming"
        elif "алгоритм" in text_lower or "сложность" in text_lower:
            return "Algorithms & Complexity"
        elif "паттерн" in text_lower or "singleton" in text_lower:
            return "Design Patterns"
        else:
            return "General Programming"
    
    def save_extended_results(self, data: Dict, filename: str = "extended_interview_analysis.json"):
        """Сохраняет расширенные результаты"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"📁 Расширенные результаты сохранены в {filename}")
    
    def print_extended_summary(self, data: Dict):
        """Выводит расширенную сводку"""
        stats = data["statistics"]
        
        print("\n" + "="*90)
        print("🚀 РАСШИРЕННЫЙ АНАЛИЗ ЗАПИСЕЙ СОБЕСЕДОВАНИЙ - Frontend – TO THE JOB")
        print("="*90)
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"  Всего сообщений: {stats['total_messages']}")
        print(f"  Алгоритмических задач: {stats['algorithm_tasks']}")
        print(f"  Отчетов о собеседованиях: {stats['interview_questions']}")
        print(f"  Технических обсуждений: {stats['tech_discussions']}")
        print(f"  Уникальных авторов: {stats['unique_authors']}")
        print(f"  Упомянутых компаний: {stats['companies_mentioned']}")
        
        print(f"\n🧮 АЛГОРИТМИЧЕСКИЕ ЗАДАЧИ:")
        for task in data["algorithm_tasks"][:5]:
            print(f"\n  📝 {task['author']} ({task['timestamp']}):")
            print(f"     Тип: {task['task_type']}")
            if task['complexity_mentioned']:
                print(f"     ⚡ Упомянута сложность алгоритма")
            if task['has_code']:
                print(f"     💻 Содержит код")
            if task['technologies']:
                print(f"     🛠️ Технологии: {', '.join(task['technologies'][:3])}")
            
            text_preview = task['text'][:150] + "..." if len(task['text']) > 150 else task['text']
            print(f"     📄 {text_preview}")
        
        print(f"\n🏢 ОТЧЕТЫ О СОБЕСЕДОВАНИЯХ:")
        for report in data["interview_questions"]:
            print(f"\n  👤 {report['author']} ({report['timestamp']}):")
            if report['company']:
                print(f"     🏢 Компания: {report['company']}")
            if report['salary']:
                print(f"     💰 Зарплата: {report['salary']}")
            print(f"     ❓ Вопросов: {report['total_questions']}")
            for i, question in enumerate(report['questions'][:3], 1):
                print(f"       {i}. {question}")
            if report['total_questions'] > 3:
                print(f"       ... и еще {report['total_questions'] - 3} вопросов")
        
        print(f"\n🔬 ТЕХНИЧЕСКИЕ ОБСУЖДЕНИЯ:")
        topics = {}
        for discussion in data["tech_discussions"]:
            topic = discussion['topic']
            topics[topic] = topics.get(topic, 0) + 1
        
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            print(f"  📚 {topic}: {count} обсуждений")
        
        print(f"\n👥 САМЫЕ АКТИВНЫЕ УЧАСТНИКИ:")
        author_counts = {}
        for msg in data["all_messages"]:
            author = msg.get("who", "Unknown")
            author_counts[author] = author_counts.get(author, 0) + 1
        
        for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            print(f"  {author}: {count} сообщений")
        
        print(f"\n📅 Дата анализа: {stats['analysis_date']}")
        print("="*90)

def main():
    analyzer = ExtendedInterviewAnalyzer()
    
    print("🔍 Расширенный анализатор записей собеседований")
    print("="*60)
    
    # Проводим расширенный анализ
    data = analyzer.analyze_extended_data()
    
    # Сохраняем результаты
    analyzer.save_extended_results(data)
    
    # Выводим расширенную сводку
    analyzer.print_extended_summary(data)
    
    print(f"\n✅ Расширенный анализ завершен!")
    print(f"📊 Проанализировано {len(EXTENDED_COLLECTED_MESSAGES)} сообщений")
    print("📁 Файл: extended_interview_analysis.json")

if __name__ == "__main__":
    main() 
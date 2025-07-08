#!/usr/bin/env python3
"""
Конвертер записей собеседований из JSON в Markdown
Создает читаемый MD файл без ошибок и пропусков
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

def sanitize_markdown(text: str) -> str:
    """Экранирование специальных символов для Markdown"""
    if not text:
        return ""
    
    # Экранируем основные MD символы
    text = text.replace('\\', '\\\\')
    text = text.replace('`', '\\`')
    text = text.replace('*', '\\*')
    text = text.replace('_', '\\_')
    text = text.replace('#', '\\#')
    text = text.replace('[', '\\[')
    text = text.replace(']', '\\]')
    text = text.replace('(', '\\(')
    text = text.replace(')', '\\)')
    
    return text

def format_date(date_str: str) -> tuple:
    """Форматирование даты для отображения"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        formatted = dt.strftime('%Y-%m-%d %H:%M')
        year_month = dt.strftime('%Y-%m')
        return formatted, year_month, dt
    except:
        return date_str, "unknown", None

def extract_company_name(text: str) -> str:
    """Извлечение названия компании из текста"""
    if not text:
        return "Неизвестная компания"
    
    # Ищем паттерны компаний
    company_patterns = [
        r'[Кк]омпания:\s*([^\n\r]+)',
        r'([A-Za-zА-Яа-я0-9\s\.]+)\s*\(',
        r'^([A-Za-zА-Яа-я0-9\s\.]+)',
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text.strip())
        if match:
            company = match.group(1).strip()
            if len(company) > 3 and len(company) < 50:
                return company
    
    # Если не нашли - берем первые слова
    words = text.strip().split()[:3]
    return ' '.join(words) if words else "Неизвестная компания"

def validate_message(msg: Dict[str, Any]) -> bool:
    """Валидация корректности сообщения"""
    required_fields = ['id', 'date', 'text']
    
    for field in required_fields:
        if field not in msg:
            print(f"⚠️ Пропущено поле {field} в сообщении ID {msg.get('id', 'unknown')}")
            return False
    
    if not msg['text'] or len(msg['text'].strip()) < 10:
        print(f"⚠️ Слишком короткий текст в сообщении ID {msg['id']}")
        return False
    
    return True

def convert_to_markdown():
    """Основная функция конвертации"""
    
    print("🔄 КОНВЕРТАЦИЯ JSON → MARKDOWN")
    print("=" * 50)
    
    # Загружаем данные
    try:
        with open('telegram_topic_messages.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Файл telegram_topic_messages.json не найден!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return False
    
    messages = data.get('messages', [])
    print(f"📁 Загружено сообщений: {len(messages)}")
    
    # Фильтруем только записи собеседований
    interview_records = []
    skipped_count = 0
    
    for msg in messages:
        # Проверяем что это запись собеседования (ответ на тему 489)
        if msg.get('reply_to_msg_id') != 489:
            continue
            
        # Валидируем сообщение
        if not validate_message(msg):
            skipped_count += 1
            continue
            
        interview_records.append(msg)
    
    print(f"✔️ Записей собеседований: {len(interview_records)}")
    print(f"⚠️ Пропущено некорректных: {skipped_count}")
    
    if not interview_records:
        print("❌ Не найдено корректных записей собеседований!")
        return False
    
    # Сортируем по дате (от старых к новым)
    interview_records.sort(key=lambda x: x['date'])
    
    # Подготавливаем статистику
    by_month = defaultdict(list)
    companies = set()
    
    for record in interview_records:
        _, month_key, dt = format_date(record['date'])
        by_month[month_key].append(record)
        
        company = extract_company_name(record['text'])
        companies.add(company)
    
    # Генерируем Markdown
    markdown_content = []
    
    # Заголовок
    first_date, _, _ = format_date(interview_records[0]['date'])
    last_date, _, _ = format_date(interview_records[-1]['date'])
    
    markdown_content.extend([
        "# 📋 Записи собеседований Frontend разработчиков",
        "",
        f"**Источник:** Telegram топик \"Записи собеседований\"",
        f"**Период:** {first_date} — {last_date}",
        f"**Всего записей:** {len(interview_records)}",
        f"**Уникальных компаний:** {len(companies)}",
        "",
        "---",
        ""
    ])
    
    # Оглавление по месяцам
    markdown_content.extend([
        "## 📅 Оглавление по месяцам",
        ""
    ])
    
    for month in sorted(by_month.keys()):
        month_records = by_month[month]
        try:
            month_name = datetime.strptime(month + '-01', '%Y-%m-%d').strftime('%B %Y')
        except:
            month_name = month
        
        month_anchor = month.replace('-', '')
        markdown_content.append(f"- [{month_name}](#{month_anchor}) ({len(month_records)} записей)")
    
    markdown_content.extend(["", "---", ""])
    
    # Записи по месяцам
    current_month = None
    record_counter = 0
    
    for record in interview_records:
        formatted_date, month_key, dt = format_date(record['date'])
        
        # Новый месяц - добавляем заголовок
        if month_key != current_month:
            current_month = month_key
            
            try:
                month_name = datetime.strptime(month_key + '-01', '%Y-%m-%d').strftime('%B %Y')
            except:
                month_name = month_key
            
            month_anchor = month_key.replace('-', '')
            markdown_content.extend([
                f"## {month_name} {{#{month_anchor}}}",
                ""
            ])
        
        # Запись собеседования
        record_counter += 1
        company = extract_company_name(record['text'])
        
        markdown_content.extend([
            f"### {record_counter}. {company}",
            "",
            f"**📅 Дата:** {formatted_date}",
            f"**🆔 ID:** {record['id']}",
            "",
            "**📝 Описание:**",
            "",
            "```",
            record['text'],
            "```",
            "",
            "---",
            ""
        ])
    
    # Финальная статистика
    markdown_content.extend([
        "## 📊 Статистика",
        "",
        f"- **Общее количество записей:** {len(interview_records)}",
        f"- **Период сбора данных:** {first_date} — {last_date}",
        f"- **Количество месяцев:** {len(by_month)}",
        f"- **Уникальных компаний:** {len(companies)}",
        "",
        "### Распределение по месяцам:",
        ""
    ])
    
    for month in sorted(by_month.keys()):
        count = len(by_month[month])
        try:
            month_name = datetime.strptime(month + '-01', '%Y-%m-%d').strftime('%B %Y')
        except:
            month_name = month
        markdown_content.append(f"- **{month_name}:** {count} записей")
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    markdown_content.extend(["", f"*Сгенерировано: {current_time}*"])
    
    # Сохраняем файл
    output_file = 'interview_records.md'
    
    try:
        file_content = '\n'.join(markdown_content)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"✅ УСПЕШНО СОЗДАН: {output_file}")
        print(f"📄 Размер файла: {len(file_content)} символов")
        print(f"📝 Записей обработано: {len(interview_records)}")
        print(f"⚠️ Пропущено: {skipped_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")
        return False

if __name__ == "__main__":
    success = convert_to_markdown()
    if success:
        print("\n🎉 Конвертация завершена успешно!")
    else:
        print("\n💥 Конвертация завершилась с ошибками!") 
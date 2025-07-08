#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Массовый сборщик всех сообщений из Telegram чата
Управляет процессом сбора через MCP API
"""

import json
import os
from typing import List, Dict, Any
import time

class MassTelegramScraper:
    def __init__(self, total_messages: int = 155797, batch_size: int = 20):
        self.total_messages = total_messages
        self.batch_size = batch_size
        self.chat_name = "Frontend – TO THE JOB"
        self.results_dir = "telegram_scraping_results"
        self.progress_file = "scraping_progress.json"
        
        # Создаем директорию для результатов
        os.makedirs(self.results_dir, exist_ok=True)
        
    def generate_offset_list(self) -> List[int]:
        """Генерирует список всех offset'ов для сбора"""
        offsets = []
        current_offset = self.total_messages
        
        while current_offset > 0:
            offsets.append(current_offset)
            current_offset -= self.batch_size
            
        return offsets
    
    def save_progress(self, current_offset: int, completed_offsets: List[int]):
        """Сохраняет прогресс выполнения"""
        progress = {
            "current_offset": current_offset,
            "completed_offsets": completed_offsets,
            "total_completed": len(completed_offsets),
            "timestamp": time.time()
        }
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    def load_progress(self) -> Dict[str, Any]:
        """Загружает прогресс выполнения"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"completed_offsets": [], "current_offset": self.total_messages}
    
    def create_batch_file(self, offset: int, batch_num: int) -> str:
        """Создает файл для конкретного batch'а"""
        filename = f"{self.results_dir}/batch_{batch_num:04d}_offset_{offset}.json"
        return filename
    
    def get_next_offset_to_process(self) -> int:
        """Возвращает следующий offset для обработки"""
        progress = self.load_progress()
        completed = set(progress.get("completed_offsets", []))
        all_offsets = self.generate_offset_list()
        
        for offset in all_offsets:
            if offset not in completed:
                return offset
        
        return -1  # Все offset'ы обработаны
    
    def mark_offset_completed(self, offset: int):
        """Отмечает offset как завершенный"""
        progress = self.load_progress()
        completed = progress.get("completed_offsets", [])
        
        if offset not in completed:
            completed.append(offset)
            
        self.save_progress(offset, completed)
    
    def get_completion_stats(self) -> Dict[str, Any]:
        """Возвращает статистику выполнения"""
        progress = self.load_progress()
        all_offsets = self.generate_offset_list()
        completed = progress.get("completed_offsets", [])
        
        return {
            "total_batches": len(all_offsets),
            "completed_batches": len(completed),
            "remaining_batches": len(all_offsets) - len(completed),
            "completion_percentage": (len(completed) / len(all_offsets)) * 100,
            "next_offset": self.get_next_offset_to_process()
        }
    
    def combine_all_results(self) -> List[Dict[str, Any]]:
        """Объединяет все результаты в один список"""
        all_messages = []
        
        # Получаем все файлы результатов
        result_files = [f for f in os.listdir(self.results_dir) if f.startswith("batch_") and f.endswith(".json")]
        result_files.sort()  # Сортируем по имени файла
        
        for filename in result_files:
            filepath = os.path.join(self.results_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                    if isinstance(batch_data, list):
                        all_messages.extend(batch_data)
                    elif isinstance(batch_data, dict) and 'messages' in batch_data:
                        all_messages.extend(batch_data['messages'])
            except Exception as e:
                print(f"Ошибка при чтении {filename}: {e}")
        
        return all_messages
    
    def save_final_result(self):
        """Сохраняет финальный результат"""
        all_messages = self.combine_all_results()
        
        final_result = {
            "chat_name": self.chat_name,
            "total_messages_collected": len(all_messages),
            "collection_timestamp": time.time(),
            "messages": all_messages
        }
        
        with open("all_telegram_messages_complete.json", 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        
        print(f"Сохранено {len(all_messages)} сообщений в all_telegram_messages_complete.json")
        return len(all_messages)

def main():
    scraper = MassTelegramScraper()
    
    print("=== МАССОВЫЙ СБОРЩИК TELEGRAM СООБЩЕНИЙ ===")
    print(f"Целевой чат: {scraper.chat_name}")
    print(f"Всего сообщений для сбора: {scraper.total_messages}")
    
    # Показываем статистику
    stats = scraper.get_completion_stats()
    print(f"\nСтатистика:")
    print(f"Всего batch'ей: {stats['total_batches']}")
    print(f"Завершено: {stats['completed_batches']}")
    print(f"Осталось: {stats['remaining_batches']}")
    print(f"Прогресс: {stats['completion_percentage']:.1f}%")
    
    # Получаем следующий offset для обработки
    next_offset = stats['next_offset']
    if next_offset == -1:
        print("\n✅ ВСЕ OFFSET'Ы ОБРАБОТАНЫ!")
        print("Объединяем результаты...")
        total_collected = scraper.save_final_result()
        print(f"🎉 Собрано {total_collected} сообщений!")
    else:
        print(f"\n📋 Следующий offset для обработки: {next_offset}")
        print(f"Номер batch'а: {stats['total_batches'] - stats['remaining_batches'] + 1}")
        
        # Создаем инструкцию для MCP вызова
        batch_num = stats['total_batches'] - stats['remaining_batches'] + 1
        print(f"\n🤖 ИНСТРУКЦИЯ ДЛЯ MCP ВЫЗОВА:")
        print(f"mcp_telegram_tg_dialog(name='{scraper.chat_name}', offset={next_offset})")
        print(f"Сохранить результат в: {scraper.create_batch_file(next_offset, batch_num)}")
    
    # Показываем все offset'ы для справки
    all_offsets = scraper.generate_offset_list()
    print(f"\nВсего offset'ов: {len(all_offsets)}")
    print(f"От {max(all_offsets)} до {min(all_offsets)}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from mass_scraper import MassTelegramScraper

def update_progress(completed_offset: int):
    scraper = MassTelegramScraper()
    scraper.mark_offset_completed(completed_offset)
    
    stats = scraper.get_completion_stats()
    print(f"✅ Offset {completed_offset} отмечен как завершенный")
    print(f"Прогресс: {stats['completed_batches']}/{stats['total_batches']} ({stats['completion_percentage']:.1f}%)")
    
    next_offset = stats['next_offset']
    if next_offset == -1:
        print("🎉 ВСЕ OFFSET'Ы ЗАВЕРШЕНЫ!")
        return None
    else:
        batch_num = stats['total_batches'] - stats['remaining_batches'] + 1
        print(f"📋 Следующий offset: {next_offset}")
        print(f"Batch номер: {batch_num}")
        print(f"Файл: {scraper.create_batch_file(next_offset, batch_num)}")
        return next_offset

if __name__ == "__main__":
    if len(sys.argv) > 1:
        completed_offset = int(sys.argv[1])
        update_progress(completed_offset)
    else:
        scraper = MassTelegramScraper()
        stats = scraper.get_completion_stats()
        next_offset = stats['next_offset']
        if next_offset != -1:
            batch_num = stats['total_batches'] - stats['remaining_batches'] + 1
            print(f"Следующий offset: {next_offset}")
            print(f"Batch: {batch_num}")
            print(f"Файл: {scraper.create_batch_file(next_offset, batch_num)}")
        else:
            print("Все offset'ы завершены!") 
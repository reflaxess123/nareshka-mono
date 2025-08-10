#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФИНАЛЬНЫЙ СКРИПТ ЗАПУСКА BERTOPIC АНАЛИЗА
Запускай это вместо старого run_analysis.py
"""

import os
import sys
import subprocess
import time

def main():
    print("="*60)
    print("🚀 ЗАПУСК BERTOPIC АНАЛИЗА ИНТЕРВЬЮ")
    print("="*60)
    
    # Проверка Python
    print("\n📌 Проверка окружения...")
    python_version = sys.version
    print(f"   Python: {python_version.split()[0]}")
    
    # Установка зависимостей
    print("\n📦 Установка/проверка зависимостей...")
    deps = [
        "bertopic==0.16.4",
        "sentence-transformers>=2.2.2", 
        "umap-learn>=0.5.3",
        "hdbscan>=0.8.33",
        "scikit-learn>=1.2.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.15.0",
        "matplotlib>=3.7.0",
        "tqdm>=4.65.0"
    ]
    
    print("   Устанавливаем пакеты...")
    for dep in deps:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", dep], 
                      capture_output=True)
    print("   ✅ Все зависимости установлены")
    
    # Параметры анализа
    print("\n⚙️  ПАРАМЕТРЫ АНАЛИЗА:")
    INPUT_FILE = "../datasets/interview_questions_BAZA.csv"
    OUTPUT_DIR = "outputs_bertopic"
    MIN_TOPIC_SIZE = 15  # Минимум вопросов в теме (оптимальный баланс)
    CREATE_VISUALIZATIONS = True  # Создавать визуализации
    
    print(f"   📄 Входной файл: {INPUT_FILE}")
    print(f"   📁 Папка результатов: {OUTPUT_DIR}")
    print(f"   🎯 Мин. размер темы: {MIN_TOPIC_SIZE}")
    print(f"   📊 Визуализации: {'Да' if CREATE_VISUALIZATIONS else 'Нет'}")
    
    # Формирование команды
    cmd = [
        sys.executable,
        "bertopic_analysis.py",
        "--input", INPUT_FILE,
        "--output", OUTPUT_DIR,
        "--min-topic-size", str(MIN_TOPIC_SIZE)
    ]
    
    if CREATE_VISUALIZATIONS:
        cmd.append("--visualizations")
    
    # Запуск анализа
    print("\n" + "="*60)
    print("🚀 ЗАПУСКАЕМ АНАЛИЗ...")
    print("⏱️  Это займет несколько минут для 8.5k вопросов")
    print("="*60 + "\n")
    
    start_time = time.time()
    
    try:
        # Запуск с выводом в реальном времени
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1
        )
        
        # Вывод в реальном времени
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
        
        # Ждем завершения
        return_code = process.wait()
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*60)
        if return_code == 0:
            print(f"✅ АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
            print(f"⏱️  Время выполнения: {elapsed/60:.1f} минут")
            print(f"📁 Результаты сохранены в: {OUTPUT_DIR}/")
            print("\nФайлы результатов:")
            print("  • questions_with_clusters.csv - вопросы с кластерами")
            print("  • enriched_questions.csv - обогащенные данные")
            print("  • cluster_labels.csv - описания кластеров")
            print("  • top_topics_global.csv - топ темы")
            print("  • by_company_top_clusters.csv - анализ по компаниям")
            if CREATE_VISUALIZATIONS:
                print("  • *.html - интерактивные визуализации")
        else:
            print(f"❌ ОШИБКА! Код завершения: {return_code}")
            print(f"⏱️  Время работы: {elapsed/60:.1f} минут")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Анализ прерван пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
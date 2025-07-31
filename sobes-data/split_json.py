#!/usr/bin/env python3
"""
Скрипт для разделения JSON файла на части с умным разделением
Минимум 500 строк, но если объект не завершен - ищем завершение
"""

import os
from pathlib import Path

def find_next_object_end(lines, start_index):
    """
    Ищет следующий конец объекта после start_index
    Ищет строки, которые заканчиваются на }, или }
    """
    for i in range(start_index, len(lines)):
        line = lines[i].strip()
        # Ищем строки, которые заканчиваются концом объекта
        if line.endswith('},') or (line.endswith('}') and not line.endswith('{}')):
            # Проверяем, что это не вложенный объект по отступам
            # Если отступ небольшой (2-4 пробела), скорее всего это конец основного объекта
            if len(lines[i]) - len(lines[i].lstrip()) <= 6:  # отступ до 6 символов
                return i

    return len(lines) - 1

def split_file_smart(input_file_path, min_lines_per_file=500):
    """
    Разделяет JSON файл на части с умным разделением
    """
    input_path = Path(input_file_path)

    if not input_path.exists():
        print(f"Файл {input_file_path} не найден!")
        return

    # Создаем папку для разделенных файлов
    output_dir = input_path.parent / f"{input_path.stem}_split_smart"
    output_dir.mkdir(exist_ok=True)

    print(f"Читаем файл: {input_file_path}")
    print(f"Результат будет сохранен в: {output_dir}")

    # Читаем все строки
    with open(input_file_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    total_lines = len(all_lines)
    print(f"Общее количество строк в файле: {total_lines}")
    print(f"Минимум строк на файл: {min_lines_per_file}")
    print()

    file_num = 1
    current_line_index = 0

    while current_line_index < total_lines:
        # Определяем минимальную границу (минимум 500 строк)
        min_end_index = current_line_index + min_lines_per_file - 1

        # Если это меньше общего количества строк, ищем завершение объекта
        if min_end_index < total_lines - 1:
            # Ищем конец объекта ПОСЛЕ минимальной границы
            actual_end_index = find_next_object_end(all_lines, min_end_index)

            # Если не нашли подходящий конец в разумных пределах, берем +100 строк от минимума
            if actual_end_index - min_end_index > 200:  # если слишком далеко
                actual_end_index = min_end_index + 100
        else:
            # Это последний файл - берем все оставшиеся строки
            actual_end_index = total_lines - 1

        # Извлекаем строки для текущего файла
        chunk_lines = all_lines[current_line_index:actual_end_index + 1]

        # Сохраняем файл
        output_file = output_dir / f"{input_path.stem}_part_{file_num:03d}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(chunk_lines)

        start_line_num = current_line_index + 1
        end_line_num = actual_end_index + 1
        lines_count = len(chunk_lines)

        print(f"Создан файл: {output_file.name}")
        print(f"  Строки: {start_line_num}-{end_line_num} ({lines_count} строк)")

        # Переходим к следующему файлу
        current_line_index = actual_end_index + 1
        file_num += 1

        # Защита от бесконечного цикла
        if current_line_index >= total_lines:
            break

    print(f"\nВсего создано файлов: {file_num - 1}")

def main():
    input_file = r"C:\Users\refla\nareshka-mono\sobes-data\MASSIV_GROUPED.json"

    print("=== Умное разделение JSON файла ===")
    print(f"Исходный файл: {input_file}")
    print(f"Минимум строк на файл: 500 (+ до завершения объекта)")
    print()

    split_file_smart(input_file, min_lines_per_file=500)

    print("\nРазделение завершено!")

if __name__ == "__main__":
    main()

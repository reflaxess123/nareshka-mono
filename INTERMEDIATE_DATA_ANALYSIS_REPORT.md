# 📊 АНАЛИЗ ПРОМЕЖУТОЧНЫХ ДАННЫХ SOBES-DATA
**Обновлено: 2025-08-26 (после частичной очистки)**

## 📌 РЕЗЮМЕ

Проведен детальный анализ директории `sobes-data` после частичной очистки мусорных файлов. Документированы готовые промежуточные данные для переиспользования в ML-пайплайнах.

**Текущее состояние:**
- 🎯 **8,532 вопроса** полностью обработаны и категоризированы (100% покрытие)
- 🧠 **182 кластера** с каноническими формулировками и ключевыми словами
- 📁 **3 активные директории** с результатами + остатки мусора
- 🚀 **4 основных скрипта** обработки данных
- ⚠️ **19 мусорных файлов** еще требуют удаления
- 💾 **Эмбеддингов нет** - генерируются на лету

---

## 🗂️ ТЕКУЩАЯ СТРУКТУРА (после очистки)

### 📁 **analysis/**

#### ⚠️ Мусорные файлы к удалению:
```bash
run_analysis.py              # 924-строчный монстр
categorize_remaining_v2.py   # устаревший
enrich_outputs.py            # одноразовый
fix_categories.py            # исправления
postprocess_v2.py            # есть новая версия
nul                          # мусор
```

#### ✅ Рабочие скрипты:
```bash
bertopic_analysis.py         # главный ML-пайплайн
generate_final_api_data.py   # генерация JSON для API
create_final_questions.py    # объединение источников
create_api_ready_data.py     # подготовка для API
import_clusters.py           # импорт в БД
```

---

### 📁 **outputs_api_ready/**

#### ✅ Актуальные файлы (ИСПОЛЬЗОВАТЬ):
- **questions_full_final.json** (3.6MB) - 8,532 вопроса с метаданными
- **dashboard_stats_final.json** - статистика для дашбордов
- **search_index_final.json** - поисковый индекс
- **api_summary.json** - сводка по файлам
- **company_stats.json** - статистика 380+ компаний
- **questions_by_category.json** - вопросы по категориям

#### ❌ Дубликаты к удалению (12 файлов):
```
questions_full.json, questions_full_v2.json, questions_full_updated.json
categories.json, categories_updated.json
dashboard_stats.json, dashboard_stats_updated.json
search_index.json
clusters.json, frontend_structure.json
uncategorized_questions.json
questions_for_db.csv
```

---

### 📁 **outputs_bertopic_final/**

✅ **Финальная категоризация всех 8.5k вопросов:**
- **all_questions_with_categories.csv** - полный датасет
- **clusters_final.csv** - 182 кластера
- **category_summary_final.csv** - сводка категорий
- **questions_categories_simple.csv** - для импорта
- **top_topics_final.csv** - топ темы

**Статус:** Источник данных в БД

---

### 📁 **outputs_production/**

🔧 **GPT-лейблы кластеров:**
- labels_gpt-4.1-mini_ct0.75_nn30_mc0.00.jsonl
- labels_gpt-4.1-mini_ct0.65_nn30_mc0.00.jsonl

---

## 🛠️ ПОЛНЫЙ ПАЙПЛАЙН ОБРАБОТКИ

### Скрипты по этапам:

#### 1. **Обработка MD файлов** → CSV
```bash
# Исходные MD
sobes-data/initial-data/mark-down-reports/*.md (119 файлов)
    ↓
# Процессор через GPT
sobes-data/scripts/final_processor.py
    ↓
# Импорт в БД
back/scripts/import_llm_reports.py
```

#### 2. **ML кластеризация** (BERTopic)
```bash
# Входные данные
sobes-data/datasets/interview_questions_BAZA.csv (8.5k вопросов)
    ↓
# BERTopic анализ
sobes-data/analysis/bertopic_analysis.py
    ↓
# Результат: 182 кластера
outputs_bertopic_final/clusters_final.csv
```

#### 3. **Постобработка и категоризация**
```bash
# GPT-обогащение (НЕТ postprocess_with_gpt.py - удален!)
# Используется встроенная логика в bertopic_analysis.py
    ↓
# Генерация API данных
sobes-data/analysis/generate_final_api_data.py
    ↓
# JSON для фронтенда
outputs_api_ready/*_final.json
```

#### 4. **Импорт в PostgreSQL**
```bash
# Главный импорт
back/scripts/import_final_categorized_data.py
    ↓
# Таблицы БД
InterviewQuestion (8,532 записи)
InterviewCluster (182 записи)
InterviewCategory (13 записей)
```

---

## 📊 СТАТИСТИКА ДАННЫХ

### Объемы:
- **Вопросов обработано:** 8,532
- **Кластеров создано:** 182
- **Категорий:** 13
- **Компаний:** 380+
- **Интервью источников:** 893

### Качество:
- **Покрытие кластеризацией:** 75.87%
- **Покрытие категоризацией:** 100%
- **Средний кластер:** 35.6 вопросов

### Топ категории:
1. JavaScript Core - 2,364 (27.71%)
2. React - 1,775 (20.80%)
3. Soft Skills - 932 (10.92%)
4. TypeScript - 769 (9.01%)
5. Другое - 700 (8.20%)

---

## 💡 РЕКОМЕНДАЦИИ

### 🔴 Срочно удалить (19 файлов):
1. Все файлы из списка мусора в `analysis/`
2. Все дубликаты в `outputs_api_ready/`
3. Файлы `nul` везде

### 🟢 Использовать для новых данных:
1. **Пайплайн:** `bertopic_analysis.py` → `generate_final_api_data.py`
2. **Импорт:** `import_final_categorized_data.py`
3. **Модель эмбеддингов:** paraphrase-multilingual-mpnet-base-v2
4. **Параметры:** min_cluster_size=15, UMAP n_components=5

### 📝 Для генерации эмбеддингов:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
embeddings = model.encode(questions_list)
```

---

## 📍 ИТОГОВАЯ СТРУКТУРА ДИРЕКТОРИЙ

```
sobes-data/
├── analysis/
│   ├── bertopic_analysis.py          ✅ Главный ML
│   ├── generate_final_api_data.py    ✅ Генератор JSON
│   ├── outputs_api_ready/            ⚠️ 6 нужных + 12 мусорных файлов
│   ├── outputs_bertopic_final/       ✅ Финальные CSV
│   └── outputs_production/           ✅ GPT лейблы
├── datasets/                         ✅ Исходные CSV
├── initial-data/                     ✅ MD отчеты (119 файлов)
├── interviews/                       ✅ CSV по компаниям
└── scripts/
    └── final_processor.py            ✅ MD→CSV процессор
```

---

## ⚡ БЫСТРЫЙ СТАРТ

Для обработки новых данных:
```bash
# 1. Положить MD файлы в initial-data/mark-down-reports/
# 2. Запустить обработку
python sobes-data/scripts/final_processor.py
# 3. Кластеризация
python sobes-data/analysis/bertopic_analysis.py
# 4. Генерация JSON
python sobes-data/analysis/generate_final_api_data.py
# 5. Импорт в БД
python back/scripts/import_final_categorized_data.py
```

---

*Анализ проведен: 2025-08-26*
*Статус: Требуется финальная очистка 19 файлов*
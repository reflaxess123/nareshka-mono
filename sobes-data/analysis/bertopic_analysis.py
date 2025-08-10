#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BERTopic Interview Analysis - ЗАМЕНА МУСОРНОГО run_analysis.py
Анализ 8.5k вопросов интервью с использованием современных методов
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import numpy as np
from tqdm import tqdm

# BERTopic и ML
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
import plotly.graph_objects as go
import plotly.express as px

# Визуализация
import matplotlib.pyplot as plt


def normalize_company(name: str) -> str:
    """Нормализация названий компаний"""
    if not isinstance(name, str):
        return ""
    import re
    norm = name.strip()
    norm = re.sub(r"^[-–—\s]+", "", norm)
    norm = re.sub(r"\s+", " ", norm)
    return norm


def load_interview_data(input_csv: str) -> pd.DataFrame:
    """Загрузка данных интервью с обработкой ошибок"""
    try:
        df = pd.read_csv(input_csv, encoding='utf-8-sig')
        print(f"📊 Загружено {len(df)} записей из {input_csv}")
        
        # Проверяем обязательные колонки
        required_cols = {'id', 'question_text', 'company', 'date', 'interview_id'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Отсутствуют колонки: {missing}")
        
        # Нормализация
        df['company_norm'] = df['company'].apply(normalize_company)
        df['question_text_norm'] = df['question_text'].astype(str).str.strip()
        
        # Убираем пустые вопросы
        df = df[df['question_text_norm'].str.len() > 5].reset_index(drop=True)
        print(f"✅ Обработано {len(df)} валидных вопросов")
        
        return df
        
    except Exception as e:
        raise ValueError(f"Ошибка загрузки данных: {e}")


def create_bertopic_model(
    language: str = "multilingual",
    min_topic_size: int = 10,
    nr_topics: str = "auto",
    embedding_model_name: str = "paraphrase-multilingual-mpnet-base-v2",
    verbose: bool = True
) -> BERTopic:
    """
    Создание настроенной модели BERTopic для русских текстов
    """
    print("🤖 Настройка BERTopic модели...")
    print(f"   📝 Язык: {language}")
    print(f"   🎯 Минимум вопросов в теме: {min_topic_size}")
    print(f"   🧠 Модель эмбеддингов: {embedding_model_name}")
    
    # Кастомная настройка для лучшего качества
    embedding_model = SentenceTransformer(embedding_model_name)
    
    # UMAP для снижения размерности
    umap_model = UMAP(
        n_neighbors=15, 
        n_components=5, 
        min_dist=0.0, 
        metric='cosine',
        random_state=42
    )
    
    # HDBSCAN для кластеризации
    hdbscan_model = HDBSCAN(
        min_cluster_size=min_topic_size,
        min_samples=min(5, min_topic_size // 2),  # Адаптивный min_samples
        metric='euclidean',
        cluster_selection_method='eom',
        prediction_data=True  # Важно для стабильности
    )
    
    # Создание модели
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        language=language,
        calculate_probabilities=True,
        verbose=verbose
    )
    
    print("✅ Модель BERTopic готова!")
    return topic_model


def analyze_topics(
    df: pd.DataFrame, 
    topic_model: BERTopic,
    output_dir: str
) -> tuple:
    """Основной анализ тем"""
    print("\n🔍 ЗАПУСК АНАЛИЗА ТЕМАТИК...")
    
    # Подготовка текстов
    texts = df['question_text_norm'].tolist()
    
    print(f"📄 Анализируем {len(texts)} вопросов...")
    
    # Засекаем время
    start_time = time.time()
    
    # 🚀 ГЛАВНАЯ МАГИЯ - ВСЕГО ОДНА СТРОЧКА ВМЕСТО 812!
    topics, probabilities = topic_model.fit_transform(texts)
    
    elapsed = time.time() - start_time
    print(f"✅ Анализ завершен за {elapsed:.1f}с!")
    
    # Статистика
    unique_topics = len(set(topics))
    outliers = list(topics).count(-1)
    coverage = (len(topics) - outliers) / len(topics) * 100
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   🎯 Найдено тем: {unique_topics}")
    print(f"   📈 Покрытие: {coverage:.1f}% ({len(topics) - outliers}/{len(topics)})")
    print(f"   🗑️  Выбросы: {outliers}")
    
    return topics, probabilities


def export_results(
    df: pd.DataFrame, 
    topics: List[int],
    probabilities: np.ndarray,
    topic_model: BERTopic,
    output_dir: str
):
    """Экспорт результатов в том же формате что и старый скрипт"""
    print("\n💾 ЭКСПОРТ РЕЗУЛЬТАТОВ...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Основной файл с кластерами
    df_results = df.copy()
    df_results['cluster_id'] = topics
    df_results['topic_probability'] = probabilities.max(axis=1) if probabilities is not None else 0.0
    
    # Исключаем выбросы (-1) при расчете статистики
    valid_clusters = [t for t in topics if t != -1]
    coverage = len(valid_clusters) / len(topics) * 100 if topics else 0
    
    # 2. Информация о темах
    topic_info = topic_model.get_topic_info()
    
    # 3. Создаем cluster_labels в том же формате
    cluster_labels = []
    for _, row in topic_info.iterrows():
        topic_id = int(row['Topic'])
        if topic_id == -1:  # Пропускаем выбросы
            continue
            
        # Канонический вопрос - самый представительный из кластера
        topic_docs = [df_results.iloc[i]['question_text_norm'] 
                     for i, t in enumerate(topics) if t == topic_id]
        canonical_question = topic_docs[0] if topic_docs else "No representative question"
        
        # Ключевые слова как темы
        keywords = ', '.join([word for word, _ in topic_model.get_topic(topic_id)[:5]])
        
        cluster_labels.append({
            'cluster_id': topic_id,
            'canonical_question': canonical_question,
            'topics': keywords,
            'size': row['Count'],
            'topic_confidence': f'{{"main_topic": 1.0}}',
            'fingerprint': hashlib.md5(canonical_question.encode()).hexdigest()[:16]
        })
    
    # 4. Топ темы глобально
    topic_counts = pd.Series([t for t in topics if t != -1]).value_counts()
    top_topics = []
    for topic_id, count in topic_counts.head(20).items():
        keywords = ', '.join([word for word, _ in topic_model.get_topic(topic_id)[:3]])
        top_topics.append({
            'topic': keywords,
            'interviews_count': count
        })
    
    # 5. Анализ по компаниям
    company_analysis = []
    for company in df_results['company_norm'].unique():
        if pd.isna(company) or company == '':
            continue
        company_data = df_results[df_results['company_norm'] == company]
        company_topics = company_data['cluster_id'].value_counts().head(10)
        for topic_id, count in company_topics.items():
            if topic_id != -1:
                company_analysis.append({
                    'company_norm': company,
                    'cluster_id': topic_id,
                    'interviews_count': count
                })
    
    # СОХРАНЕНИЕ ФАЙЛОВ
    print("💾 Сохранение файлов...")
    
    # Основной файл с результатами
    output_file = os.path.join(output_dir, "questions_with_clusters.csv")
    df_results.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"   ✅ {output_file}")
    
    # Обогащенные вопросы 
    enriched_file = os.path.join(output_dir, "enriched_questions.csv")
    df_enriched = df_results.merge(
        pd.DataFrame(cluster_labels)[['cluster_id', 'canonical_question', 'topics']],
        on='cluster_id', 
        how='left'
    )
    df_enriched.to_csv(enriched_file, index=False, encoding='utf-8-sig')
    print(f"   ✅ {enriched_file}")
    
    # Описания кластеров
    labels_file = os.path.join(output_dir, "cluster_labels.csv")
    pd.DataFrame(cluster_labels).to_csv(labels_file, index=False, encoding='utf-8-sig')
    print(f"   ✅ {labels_file}")
    
    # Топ темы
    topics_file = os.path.join(output_dir, "top_topics_global.csv")
    pd.DataFrame(top_topics).to_csv(topics_file, index=False, encoding='utf-8-sig')
    print(f"   ✅ {topics_file}")
    
    # Анализ по компаниям
    companies_file = os.path.join(output_dir, "by_company_top_clusters.csv")
    pd.DataFrame(company_analysis).to_csv(companies_file, index=False, encoding='utf-8-sig')
    print(f"   ✅ {companies_file}")
    
    # Сохранение модели
    model_file = os.path.join(output_dir, "bertopic_model")
    topic_model.save(model_file)
    print(f"   ✅ {model_file}")
    
    print(f"\n🎉 ВСЕ РЕЗУЛЬТАТЫ СОХРАНЕНЫ В: {output_dir}")
    
    return {
        'total_questions': len(df_results),
        'valid_topics': len([t for t in topics if t != -1]),
        'coverage_percent': coverage,
        'num_topics': len(set(topics)) - (1 if -1 in topics else 0)
    }


def create_visualizations(
    topic_model: BERTopic,
    output_dir: str
):
    """Создание визуализаций"""
    print("\n📊 СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ...")
    
    try:
        # Тепловая карта тем
        fig1 = topic_model.visualize_heatmap(width=1000, height=600)
        fig1.write_html(os.path.join(output_dir, "topics_heatmap.html"))
        print(f"   ✅ topics_heatmap.html")
        
        # Интерактивная карта тем
        fig2 = topic_model.visualize_topics(width=1200, height=800)
        fig2.write_html(os.path.join(output_dir, "topics_visualization.html"))
        print(f"   ✅ topics_visualization.html")
        
        # Гистограмма тем
        fig3 = topic_model.visualize_barchart(top_k_topics=20, width=800, height=600)
        fig3.write_html(os.path.join(output_dir, "topics_barchart.html"))
        print(f"   ✅ topics_barchart.html")
        
    except Exception as e:
        print(f"⚠️  Ошибка создания визуализаций: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="🚀 BERTopic Interview Analysis - НОВОЕ ПОКОЛЕНИЕ"
    )
    parser.add_argument("--input", required=True, help="Путь к CSV файлу с вопросами")
    parser.add_argument("--output", default="outputs_bertopic", help="Папка для результатов")
    parser.add_argument("--min-topic-size", type=int, default=10, help="Минимальный размер темы")
    parser.add_argument("--language", default="multilingual", help="Язык анализа")
    parser.add_argument("--embedding-model", default="paraphrase-multilingual-mpnet-base-v2", help="Модель для эмбеддингов")
    parser.add_argument("--visualizations", action="store_true", help="Создавать визуализации")
    
    args = parser.parse_args()
    
    print("🚀" * 20)
    print("🚀 BERTopic INTERVIEW ANALYSIS")
    print("🚀 ЗАМЕНА МУСОРНОГО run_analysis.py")
    print("🚀" * 20)
    
    try:
        # 1. Загрузка данных
        df = load_interview_data(args.input)
        
        # 2. Создание модели
        topic_model = create_bertopic_model(
            language=args.language,
            min_topic_size=args.min_topic_size,
            embedding_model_name=args.embedding_model
        )
        
        # 3. Анализ
        topics, probabilities = analyze_topics(df, topic_model, args.output)
        
        # 4. Экспорт результатов
        stats = export_results(df, topics, probabilities, topic_model, args.output)
        
        # 5. Визуализации
        if args.visualizations:
            create_visualizations(topic_model, args.output)
        
        print("\n" + "🎉" * 50)
        print("🎉 АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
        print(f"🎉 Обработано: {stats['total_questions']} вопросов")
        print(f"🎉 Найдено тем: {stats['num_topics']}")
        print(f"🎉 Покрытие: {stats['coverage_percent']:.1f}%")
        print(f"🎉 Результаты в: {args.output}")
        print("🎉" * 50)
        
    except Exception as e:
        print(f"\n💥 ОШИБКА: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
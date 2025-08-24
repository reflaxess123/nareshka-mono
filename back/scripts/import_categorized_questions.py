#!/usr/bin/env python3
"""
Скрипт импорта категоризированных вопросов интервью в базу данных
"""

import json
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))

from app.core.settings import settings


def import_data():
    """Импорт категоризированных данных в БД"""

    print("=" * 60)
    print("ИМПОРТ КАТЕГОРИЗИРОВАННЫХ ВОПРОСОВ ИНТЕРВЬЮ")
    print("=" * 60)

    # Подключение к БД
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Путь к данным
        data_dir = (
            Path(__file__).parent.parent.parent
            / "sobes-data"
            / "analysis"
            / "outputs_api_ready"
        )

        # 1. Загружаем и импортируем категории
        print("\n1. Импорт категорий...")
        with open(data_dir / "categories.json", encoding="utf-8") as f:
            categories = json.load(f)

        for cat in categories:
            category_id = cat["name"].replace(" ", "_").lower()

            # Проверяем существование
            exists = session.execute(
                text('SELECT 1 FROM "InterviewCategory" WHERE id = :id'),
                {"id": category_id},
            ).first()

            if not exists:
                session.execute(
                    text("""
                        INSERT INTO "InterviewCategory" 
                        (id, name, questions_count, clusters_count, percentage)
                        VALUES (:id, :name, :questions_count, :clusters_count, :percentage)
                    """),
                    {
                        "id": category_id,
                        "name": cat["name"],
                        "questions_count": cat["questions_count"],
                        "clusters_count": cat["clusters_count"],
                        "percentage": cat["percentage"],
                    },
                )
                print(f"   + {cat['name']}: {cat['questions_count']} вопросов")

        session.commit()
        print(f"   Импортировано категорий: {len(categories)}")

        # 2. Загружаем и импортируем кластеры
        print("\n2. Импорт кластеров...")
        with open(data_dir / "clusters.json", encoding="utf-8") as f:
            clusters = json.load(f)

        for cluster in clusters:
            category_id = cluster["category"].replace(" ", "_").lower()

            # Проверяем существование
            exists = session.execute(
                text('SELECT 1 FROM "InterviewCluster" WHERE id = :id'),
                {"id": cluster["id"]},
            ).first()

            if not exists:
                session.execute(
                    text("""
                        INSERT INTO "InterviewCluster"
                        (id, name, category_id, keywords, questions_count, example_question)
                        VALUES (:id, :name, :category_id, :keywords, :questions_count, :example_question)
                    """),
                    {
                        "id": cluster["id"],
                        "name": cluster["name"][:255],  # ограничиваем длину
                        "category_id": category_id,
                        "keywords": cluster["keywords"][:10],  # топ-10 ключевых слов
                        "questions_count": cluster["questions_count"],
                        "example_question": cluster.get("example_question"),
                    },
                )

        session.commit()
        print(f"   Импортировано кластеров: {len(clusters)}")

        # 3. Загружаем и импортируем вопросы
        print("\n3. Импорт вопросов...")
        questions_df = pd.read_csv(data_dir / "questions_for_db.csv")

        imported = 0
        skipped = 0
        batch_size = 500

        for i in range(0, len(questions_df), batch_size):
            batch = questions_df.iloc[i : i + batch_size]

            for _, row in batch.iterrows():
                # Проверяем существование
                exists = session.execute(
                    text('SELECT 1 FROM "InterviewQuestion" WHERE id = :id'),
                    {"id": row["id"]},
                ).first()

                if not exists:
                    category_id = None
                    if (
                        pd.notna(row.get("final_category"))
                        and row["final_category"] != "Нет кластера"
                    ):
                        category_id = row["final_category"].replace(" ", "_").lower()

                    cluster_id = None
                    if pd.notna(row.get("cluster_id")) and row["cluster_id"] != -1:
                        cluster_id = int(row["cluster_id"])

                    session.execute(
                        text("""
                            INSERT INTO "InterviewQuestion"
                            (id, question_text, company, cluster_id, category_id, topic_name, canonical_question)
                            VALUES (:id, :question_text, :company, :cluster_id, :category_id, :topic_name, :canonical_question)
                        """),
                        {
                            "id": row["id"],
                            "question_text": row["question_text"][
                                :2000
                            ],  # ограничиваем длину
                            "company": row.get("company")
                            if pd.notna(row.get("company"))
                            else None,
                            "cluster_id": cluster_id,
                            "category_id": category_id,
                            "topic_name": row.get("topic_name")
                            if pd.notna(row.get("topic_name"))
                            else None,
                            "canonical_question": row.get("canonical_question")[:2000]
                            if pd.notna(row.get("canonical_question"))
                            else None,
                        },
                    )
                    imported += 1
                else:
                    skipped += 1

            # Коммитим батчами
            session.commit()
            print(
                f"   Обработано: {min(i+batch_size, len(questions_df))}/{len(questions_df)}"
            )

        print(f"\n   + Импортировано вопросов: {imported}")
        print(f"   - Пропущено (уже существуют): {skipped}")

        # 4. Статистика
        print("\n4. СТАТИСТИКА:")

        total_questions = session.execute(
            text('SELECT COUNT(*) FROM "InterviewQuestion"')
        ).scalar()

        categorized = session.execute(
            text(
                'SELECT COUNT(*) FROM "InterviewQuestion" WHERE category_id IS NOT NULL'
            )
        ).scalar()

        print(f"   Всего вопросов в БД: {total_questions}")
        print(
            f"   Категоризировано: {categorized} ({categorized/total_questions*100:.1f}%)"
        )

        print("\n[OK] ИМПОРТ ЗАВЕРШЕН УСПЕШНО!")

    except Exception as e:
        print(f"\n[ERROR] Ошибка при импорте: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import_data()

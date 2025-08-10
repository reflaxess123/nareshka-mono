import argparse
import os
import pandas as pd


def make_report(base: str) -> str:
    topics_q_path = os.path.join(base, "topics_by_questions_fixed.csv")
    topics_i_path = os.path.join(base, "top_topics_fixed.csv")
    clusters_path = os.path.join(base, "top_clusters_fixed.csv")
    by_company_path = os.path.join(base, "topics_by_company_fixed.csv")
    enriched_fixed_path = os.path.join(base, "enriched_questions_fixed.csv")

    t_q = pd.read_csv(topics_q_path)
    t_i = pd.read_csv(topics_i_path)
    cl = pd.read_csv(clusters_path)
    bc = pd.read_csv(by_company_path)
    try:
        enf = pd.read_csv(enriched_fixed_path)
        company_inv = (
            enf.groupby("company_norm")["interview_id"].nunique().sort_values(ascending=False)
        )
    except Exception:
        company_inv = bc.groupby("company_norm")["interviews_count"].sum().sort_values(ascending=False)

    # Top topics
    t_q_top = t_q.sort_values("questions_count", ascending=False).head(15)
    t_i_top = t_i.sort_values("interviews_count", ascending=False).head(15)

    # Top clusters (by interviews then companies)
    cl_top = cl.sort_values(["interviews_count", "company_count"], ascending=False).head(30)

    # Per-company top 3 topics by rank
    bc = bc.sort_values(["company_norm", "rank", "interviews_count"], ascending=[True, True, False])
    top3_by_company = bc.groupby("company_norm").head(3)

    lines: list[str] = []
    lines.append(f"# Итоговая аналитика (папка: {base})\n")
    lines.append("### Что в этом отчёте и как его читать\n")
    lines.append("- Темы по вопросам — ОБЪЁМ. Сколько строк/вопросов относится к теме. Помогает понять, что спрашивают МНОГО.")
    lines.append("- Темы по интервью — ОХВАТ. В скольких разных интервью тема звучала (1 раз в интервью считается 1). Помогает понять, что спрашивают ШИРОКО.")
    lines.append("- Топ вопросов (кластеры) — конкретные формулировки с метриками: интервью (сколько интервью их задавали) и компании (сколькими компаниями).")
    lines.append("- Темы по компаниям — для каждой компании показаны её 3 самые частые темы с долями и числом интервью. Доля = тема/все темы компании в интервью.\n")

    lines.append("### Глоссарий\n")
    lines.append("- Интервью — набор вопросов в рамках одной беседы (поле interview_id).")
    lines.append("- Кластер — корзина похожих формулировок; у кластера есть canonical_question (нормализованная формулировка).")
    lines.append("- Тема — категория из фиксированной таксономии (JS/TS/React/Алгоритмы/…); у вопроса может быть до 3 тем.\n")

    lines.append("### Как пользоваться (шаги)\n")
    lines.append("1) Посмотри раздел ‘Темы — по вопросам’: это приоритизация по ОБЪЁМУ.")
    lines.append("2) Сверь с ‘Темы — по интервью’: это приоритизация по ОХВАТУ.")
    lines.append("3) Зайди в ‘Топ вопросов’: увидишь конкретные формулировки, которые чаще повторяются.")
    lines.append("4) Внизу ‘Темы по компаниям’: выбери свою компанию и смотри её топ‑3 тем (с долями).\n")

    lines.append("## Темы — по числу вопросов (что спрашивают МНОГО)\n")
    for _, row in t_q_top.iterrows():
        lines.append(f"- {row['topics']}: {int(row['questions_count'])}")
    lines.append("")

    lines.append("## Темы — по охвату интервью (что спрашивают ШИРОКО)\n")
    for _, row in t_i_top.iterrows():
        lines.append(f"- {row['topics']}: {int(row['interviews_count'])}")
    lines.append("")

    lines.append("## Топ вопросов (кластеры)\n")
    lines.append("Каждая строка: [cluster_id] canonical_question — интервью: N, компании: M.\n")
    for _, row in cl_top.iterrows():
        cq = str(row['canonical_question']).strip()
        lines.append(
            f"- [{int(row['cluster_id'])}] {cq} — интервью: {int(row['interviews_count'])}, компании: {int(row['company_count'])}"
        )
    lines.append("")

    lines.append("## Темы по компаниям — топ‑3 с долями\n")
    # Печатаем только топ-15 компаний по числу интервью, чтобы отчёт был читаемым
    top_companies = list(company_inv.head(15).index)
    for company in top_companies:
        subset = top3_by_company[top3_by_company["company_norm"] == company]
        total_iv = int(company_inv.get(company, 0))
        lines.append(f"- **{company}** (интервью: {total_iv}):")
        for _, row in subset.iterrows():
            share = float(row.get("share", 0.0))
            share_pct = f"{share*100:.1f}%" if share <= 1.0 else f"{share:.1f}%"
            lines.append(
                f"  - {row['topics']} — {int(row['interviews_count'])} интер., доля: {share_pct} (rank {int(row['rank'])})"
            )
    lines.append("")

    lines.append("### Частые вопросы (FAQ)\n")
    lines.append("- Как понять, что чаще спрашивает конкретная компания? → Найди компанию в разделе ‘Темы по компаниям’ и смотри её топ‑3 тем с долями.")
    lines.append("- Как найти конкретные формулировки вопросов? → Раздел ‘Топ вопросов (кластеры)’ — там канон‑вопросы.")
    lines.append("- Чем отличаются ‘по вопросам’ и ‘по интервью’? → ОБЪЁМ vs ОХВАТ: первое — сколько строк, второе — в скольких интервью.\n")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Папка с готовыми CSV (outputs_mini_vX)")
    args = ap.parse_args()
    report_md = make_report(args.base)
    out_path = os.path.join(args.base, "REPORT.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()



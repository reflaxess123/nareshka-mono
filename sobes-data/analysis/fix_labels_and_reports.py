import argparse
import os
import re
import unicodedata
from typing import List, Dict, Any, Tuple

import pandas as pd


DEFAULT_TAXONOMY = [
    "JS: типы и приведение типов",
    "JS: замыкания и область видимости",
    "JS: this/bind/call/apply",
    "JS: прототипы и классы",
    "JS: модули (ESM/CJS)",
    "JS: методы массивов/объектов",
    "Async: event loop и микрозадачи",
    "Async: промисы/async-await",
    "Async: таймеры/AbortController/отмена",
    "TS: типы vs интерфейсы",
    "TS: generics и infer",
    "TS: utility/conditional/mapped types",
    "TS: any/unknown/never/void",
    "TS: overloads/satisfies/decorators",
    "React: основы/JSX/VDOM/reconciliation",
    "React: хуки useState/useEffect",
    "React: хуки useMemo/useCallback",
    "React: useRef/forwardRef/useLayoutEffect",
    "React: ключи/рендер/батчинг/оптимизация",
    "React: контекст/порталы/формы",
    "State: Redux и middleware",
    "State: Context/Reducer",
    "State: Effector/MobX",
    "State: Zustand/Valtio",
    "Browser: DOM/события/всплытие/погружение",
    "Browser: рендеринг/перфоманс (LCP/CLS)",
    "Browser: storage/cookies/session/local",
    "Browser: Web APIs (Workers/ServiceWorker/IDB)",
    "Net: HTTP/HTTPS/HTTP2/HTTP3",
    "Net: кэширование/ETag/CDN",
    "Security: CORS/CSRF",
    "Security: JWT/OAuth/авторизация",
    "Tooling: бандлеры (webpack/vite/rollup)",
    "Tooling: оптимизация бандла/код-сплиттинг",
    "Testing: unit/integration/e2e",
    "CI/CD и DevOps (Docker)",
    "Архитектура/SOLID/KISS/DRY/YAGNI",
    "Паттерны проектирования",
    "Node.js/SSR/Next.js",
    "API дизайн: REST/GraphQL/WebSocket",
    "HTML: семантика/доступность (ARIA)",
    "CSS: БЭМ/Flex/Grid/каскад/перфоманс",
    "Алгоритмы: структуры данных/Big-O",
    "Алгоритмы: строки/массивы",
    "Алгоритмы: деревья/графы",
    "Алгоритмы: DP/поиск/сортировки",
    "Кодинг-задачи (JS/React)",
    "Поведенческие/процессы/коммуникации",
]


def normalize_text(s: str) -> str:
    s = (s or "").lower().replace("ё", "е")
    s = unicodedata.normalize("NFKC", s)
    # Удаляем пунктуацию кроме пробелов и дефиса/нижнего подчеркивания
    s = re.sub(r"[^\w\s\-]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def any_word(text: str, tokens: List[str]) -> bool:
    # Границы слова по Unicode (\w) — безопаснее, чем простые подстроки
    return any(re.search(rf"(?<!\w){re.escape(tok)}(?!\w)", text, flags=re.UNICODE) for tok in tokens)


def heuristics_topics(text: str) -> List[str]:
    t = normalize_text(text)
    scores: Dict[str, int] = {}

    def bump(topic: str, inc: int = 1):
        if topic in DEFAULT_TAXONOMY:
            scores[topic] = scores.get(topic, 0) + inc

    # React — сначала специфичные
    if any_word(t, ["useeffect", "usestate", "хуки"]):
        bump("React: хуки useState/useEffect", 2)
    if any_word(t, ["usememo", "usecallback"]):
        bump("React: хуки useMemo/useCallback", 2)
    if any_word(t, ["useref", "forwardref", "реф"]):
        bump("React: useRef/forwardRef/useLayoutEffect", 2)
    if any_word(t, ["jsx", "vdom", "виртуальный"]):
        bump("React: основы/JSX/VDOM/reconciliation")
    if any_word(t, ["batch", "батч", "reconciliation", "concurrent", "key", "ключи"]):
        bump("React: ключи/рендер/батчинг/оптимизация")

    # Async
    if any_word(t, ["event", "loop"]) or "микрозадач" in t or "microtask" in t or "settimeout" in t:
        bump("Async: event loop и микрозадачи")
    if any_word(t, ["promise"]) or "промис" in t or "async" in t or "await" in t:
        bump("Async: промисы/async-await")
    if any_word(t, ["abortcontroller", "timer"]) or "таймер" in t:
        bump("Async: таймеры/AbortController/отмена")

    # TS
    if any_word(t, ["typescript", "интерфейс", "interface", "type", "тип"]):
        bump("TS: типы vs интерфейсы")
    if any_word(t, ["generic", "дженерик", "infer"]):
        bump("TS: generics и infer")
    if any_word(t, ["utility", "mapped", "conditional", "partial", "pick", "omit", "record"]):
        bump("TS: utility/conditional/mapped types")
    if any_word(t, ["any", "unknown", "never", "void"]):
        bump("TS: any/unknown/never/void")
    if any_word(t, ["satisfies", "decorator", "overload", "перегрузка"]):
        bump("TS: overloads/satisfies/decorators")

    # JS core
    if "замыкан" in t or "closure" in t:
        bump("JS: замыкания и область видимости", 2)
    if any_word(t, ["this", "bind", "call", "apply"]):
        bump("JS: this/bind/call/apply")
    if "прототип" in t or "prototype" in t or any_word(t, ["класс"]):
        bump("JS: прототипы и классы")
    if any_word(t, ["var", "let", "const"]) or "приведен" in t or any_word(t, ["тип"]):
        bump("JS: типы и приведение типов")
    if any_word(t, ["reduce", "map", "filter"]) or "массив" in t or "объект" in t:
        bump("JS: методы массивов/объектов")

    # State
    if any_word(t, ["redux", "slice", "middleware"]):
        bump("State: Redux и middleware")
    if any_word(t, ["context", "reducer"]):
        bump("State: Context/Reducer")
    if any_word(t, ["effector", "mobx"]):
        bump("State: Effector/MobX")
    if any_word(t, ["zustand", "valtio"]):
        bump("State: Zustand/Valtio")

    # Browser / Net / Security
    if any_word(t, ["dom", "bom"]) or "всплыти" in t or "погружен" in t:
        bump("Browser: DOM/события/всплытие/погружение")
    if any_word(t, ["lcp", "cls"]) or "перфоманс" in t or "performance" in t or "animationframe" in t or "reflow" in t or "layout" in t:
        bump("Browser: рендеринг/перфоманс (LCP/CLS)")
    if any_word(t, ["localstorage", "sessionstorage", "cookie", "storage"]):
        bump("Browser: storage/cookies/session/local")
    if any_word(t, ["serviceworker", "worker", "indexeddb", "idb"]):
        bump("Browser: Web APIs (Workers/ServiceWorker/IDB)")
    if any_word(t, ["http", "https", "http2", "http3"]):
        bump("Net: HTTP/HTTPS/HTTP2/HTTP3")
    if any_word(t, ["cors", "csrf"]):
        bump("Security: CORS/CSRF")
    if any_word(t, ["jwt", "oauth"]) or "авторизац" in t:
        bump("Security: JWT/OAuth/авторизация")

    # Tooling / Arch
    if any_word(t, ["webpack", "vite", "rollup"]) or "бандл" in t or "code split" in t:
        bump("Tooling: бандлеры (webpack/vite/rollup)")
    if any_word(t, ["solid", "kiss", "dry", "yagni"]) or "архитектур" in t or "refactor" in t:
        bump("Архитектура/SOLID/KISS/DRY/YAGNI")
    if any_word(t, ["flux"]):
        bump("Паттерны проектирования")
    if any_word(t, ["unit", "integration", "e2e", "coverage"]) or "покрыти" in t:
        bump("Testing: unit/integration/e2e")
    if any_word(t, ["ci", "cd", "docker", "pipeline"]):
        bump("CI/CD и DevOps (Docker)")
    if any_word(t, ["node", "next", "ssr"]):
        bump("Node.js/SSR/Next.js")

    # Behavioral / Process / Communication
    beh_keys = [
        "опыт", "процесс", "коммуник", "менеджер", "оффер", "резюме",
        "спринт", "ревью", "код ревью", "апрув", "аппрув", "апprove",
        "бэклог", "бэклоге", "планирован", "приоритизац", "груминг",
        "ретросп", "retro", "митинг", "встреч", "аналитик", "дизайнер",
        "стейкхолдер", "stakeholder", "devops", "деплой", "релиз",
        "онборд", "команда", "договор", "согласова", "процессы",
    ]
    if any(any_word(t, [kw]) or kw in t for kw in beh_keys):
        bump("Поведенческие/процессы/коммуникации", 2)

    # Algorithms / Coding (без общих "react"/"component")
    if any([kw in t for kw in ["big o", "сложност", "хеш", "структур", "граф", "дерев", "куч", "очеред", "стек"]]):
        bump("Алгоритмы: структуры данных/Big-O")
    if any([kw in t for kw in ["строк", "анаграм", "палиндром", "скобк", "массив"]]):
        bump("Алгоритмы: строки/массивы")
    if any([kw in t for kw in ["дерев", "граф"]]):
        bump("Алгоритмы: деревья/графы")
    if any([kw in t for kw in ["динамическ", "поиск", "сортиров"]]):
        bump("Алгоритмы: DP/поиск/сортировки")
    if any_word(t, ["реализовать", "реализуйте"]) or "написать функцию" in t or "write a function" in t or "implement" in t:
        bump("Кодинг-задачи (JS/React)")

    # Вернуть топ-3 по весам
    if not scores:
        return []
    top = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    return [k for k, _ in top]


def build_reports(enriched: pd.DataFrame, out_dir: str) -> None:
    # Top topics by unique interviews
    topics_exploded = enriched.explode("topics")
    topics_exploded = topics_exploded.dropna(subset=["topics"])
    top_topics = (
        topics_exploded
        .drop_duplicates(subset=["interview_id", "topics"])
        .groupby("topics")["interview_id"].nunique()
        .reset_index(name="interviews_count")
        .sort_values("interviews_count", ascending=False)
    )
    top_topics.to_csv(os.path.join(out_dir, "top_topics_fixed.csv"), index=False)

    # Topic share
    total_iv = topics_exploded["interview_id"].nunique()
    if total_iv > 0:
        share = top_topics.copy()
        share["interviews_share"] = share["interviews_count"] / float(total_iv)
        share.to_csv(os.path.join(out_dir, "topic_shares_fixed.csv"), index=False)

    # Top clusters (unique interviews and companies)
    top_clusters = (
        enriched
        .groupby(["cluster_id", "canonical_question"], dropna=False)
        .agg(interviews_count=("interview_id", "nunique"),
             company_count=("company_norm", "nunique"))
        .reset_index()
        .sort_values(["interviews_count", "company_count"], ascending=False)
    )
    top_clusters.to_csv(os.path.join(out_dir, "top_clusters_fixed.csv"), index=False)

    # EXTRA: Topics by questions (raw row count)
    top_topics_q = (
        topics_exploded
        .groupby("topics").size()
        .reset_index(name="questions_count")
        .sort_values("questions_count", ascending=False)
    )
    top_topics_q.to_csv(os.path.join(out_dir, "topics_by_questions_fixed.csv"), index=False)

    # EXTRA: Clusters by questions (raw row count)
    top_clusters_q = (
        enriched
        .groupby(["cluster_id", "canonical_question"], dropna=False)
        .size()
        .reset_index(name="questions_count")
        .sort_values("questions_count", ascending=False)
    )
    top_clusters_q.to_csv(os.path.join(out_dir, "top_clusters_by_questions_fixed.csv"), index=False)

    # By company: topic coverage (+share, +rank)
    by_company = (
        topics_exploded
        .drop_duplicates(subset=["company_norm", "interview_id", "topics"])
        .groupby(["company_norm", "topics"])["interview_id"].nunique()
        .reset_index(name="interviews_count")
    )
    if not by_company.empty:
        by_company["share"] = by_company.groupby("company_norm")["interviews_count"].transform(lambda s: s / float(s.sum()))
        by_company["rank"] = by_company.groupby("company_norm")["interviews_count"].rank(ascending=False, method="dense").astype(int)
        by_company = by_company.sort_values(["company_norm", "rank", "interviews_count"], ascending=[True, True, False])
    by_company.to_csv(os.path.join(out_dir, "topics_by_company_fixed.csv"), index=False)

    # By company: top clusters (canonical questions) with shares and rank
    by_company_clusters = (
        enriched
        .groupby(["company_norm", "cluster_id", "canonical_question"], dropna=False)["interview_id"]
        .nunique()
        .reset_index(name="interviews_count")
    )
    if not by_company_clusters.empty:
        by_company_clusters["share"] = by_company_clusters.groupby("company_norm")["interviews_count"].transform(lambda s: s / float(s.sum()))
        by_company_clusters["rank"] = by_company_clusters.groupby("company_norm")["interviews_count"].rank(ascending=False, method="dense").astype(int)
        by_company_clusters = by_company_clusters.sort_values(["company_norm", "rank", "interviews_count"], ascending=[True, True, False])
    by_company_clusters.to_csv(os.path.join(out_dir, "company_top_clusters_fixed.csv"), index=False)

    # Company × Topic pivot (shares) for heatmap
    if not by_company.empty:
        pivot = by_company.pivot_table(index="company_norm", columns="topics", values="interviews_count", fill_value=0, aggfunc="sum")
        # convert to shares per company
        pivot_share = pivot.div(pivot.sum(axis=1).replace(0, 1), axis=0)
        pivot_share.to_csv(os.path.join(out_dir, "company_topic_pivot.csv"))


def main():
    ap = argparse.ArgumentParser(description="Fix empty labels via heuristics and rebuild reports")
    ap.add_argument("--base", default="sobes-data/analysis/outputs_mini", help="Директория с enriched_questions.csv")
    args = ap.parse_args()

    base = args.base
    enr_path = os.path.join(base, "enriched_questions.csv")
    qwc_path = os.path.join(base, "questions_with_clusters.csv")
    if not os.path.exists(enr_path):
        raise SystemExit(f"Not found: {enr_path}")
    df = pd.read_csv(enr_path)

    # 1) Fallback для canonical_question: если пуст, берём самый частый question_text_norm в кластере
    empt_canon = df["canonical_question"].isna() | (df["canonical_question"].astype(str).str.strip() == "")
    if empt_canon.any():
        qdf = pd.read_csv(qwc_path)
        mp = (
            qdf.groupby("cluster_id")["question_text_norm"]
            .agg(lambda s: s.value_counts().idxmax() if not s.empty else "")
            .to_dict()
        )
        df.loc[empt_canon, "canonical_question"] = df.loc[empt_canon, "cluster_id"].map(mp).fillna("")

    # 2) Заполнение пустых topics с помощью эвристик (по canonical + исходному вопросу)
    def fill_topics(row: pd.Series) -> List[str]:
        current = row.get("topics")
        if isinstance(current, list) and len(current) > 0:
            return current
        candidates = []
        for field in [row.get("canonical_question", ""), row.get("question_text_norm", ""), row.get("question_text", "")]:
            candidates.extend(heuristics_topics(str(field)))
        # uniq preserve order
        uniq: List[str] = []
        for t in candidates:
            if t not in uniq:
                uniq.append(t)
        return uniq[:3]

    # Convert stringified lists back to lists if needed
    def parse_topics(val: Any) -> List[str]:
        if isinstance(val, list):
            return val
        s = str(val or "").strip()
        # Treat common placeholders as empty
        if s.lower() in {"", "nan", "none", "null"}:
            return []
        if s.startswith("[") and s.endswith("]"):
            try:
                import ast
                v = ast.literal_eval(s)
                if isinstance(v, list):
                    return [str(x) for x in v]
            except Exception:
                return []
        if s:
            return [s]
        return []

    df["topics"] = df["topics"].apply(parse_topics)
    df["topics"] = df.apply(fill_topics, axis=1)
    df["topics_str"] = df["topics"].apply(lambda xs: ", ".join(xs))

    # 3) Сохранить починенный enriched
    fixed_path = os.path.join(base, "enriched_questions_fixed.csv")
    df.to_csv(fixed_path, index=False)

    # 4) Отчёты
    build_reports(df, base)

    print("Saved:", fixed_path)
    print("Saved:", os.path.join(base, "top_topics_fixed.csv"))
    print("Saved:", os.path.join(base, "top_clusters_fixed.csv"))
    print("Saved:", os.path.join(base, "topics_by_company_fixed.csv"))


if __name__ == "__main__":
    main()



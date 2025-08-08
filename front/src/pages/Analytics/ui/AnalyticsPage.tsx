import {
  useGetCompaniesQuestionsApiV2AnalyticsCompaniesQuestionsGet,
  useGetCompanyProfilesApiV2AnalyticsCompanyProfilesGet,
  useGetCooccurrenceApiV2AnalyticsCooccurrenceGet,
  useGetHeatmapApiV2AnalyticsHeatmapGet,
  useGetQuestionsFrequenciesApiV2AnalyticsQuestionsFrequenciesGet,
  useGetTopicsApiV2AnalyticsTopicsGet,
  useGetTopQuestionsApiV2AnalyticsTopQuestionsGet,
  useGetTrendsApiV2AnalyticsTrendsGet,
} from '@/shared/api/generated/api';
import * as echarts from 'echarts';
import ReactECharts from 'echarts-for-react';
import React, { useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import styles from './AnalyticsPage.module.scss';

export const AnalyticsPage: React.FC = () => {
  // Controls
  const [heatmapNorm, setHeatmapNorm] = useState<'none' | 'row' | 'col'>('row');
  const [minCount, setMinCount] = useState<number>(1);
  const [questionQuery, setQuestionQuery] = useState<string>('');
  const [companyFilter, setCompanyFilter] = useState<string>('');
  const [limitQuestions, setLimitQuestions] = useState<number>(200);
  const [limitTopQuestions, setLimitTopQuestions] = useState<number>(50);
  const [limitPerCompany, setLimitPerCompany] = useState<number>(50);
  const [limitTopics, setLimitTopics] = useState<number>(50);

  // Generated client hooks
  const { data: topicsData, isLoading: topicsLoading } =
    useGetTopicsApiV2AnalyticsTopicsGet({ limit: limitTopics });
  const { data: heatmapData, isLoading: heatmapLoading } =
    useGetHeatmapApiV2AnalyticsHeatmapGet({ normalization: heatmapNorm });
  const { data: trendsData, isLoading: trendsLoading } =
    useGetTrendsApiV2AnalyticsTrendsGet();
  const { data: profilesData, isLoading: profilesLoading } =
    useGetCompanyProfilesApiV2AnalyticsCompanyProfilesGet({ top: 5 });
  const { data: cooccData, isLoading: cooccLoading } =
    useGetCooccurrenceApiV2AnalyticsCooccurrenceGet({ limit: 100 });
  const { data: questionsData, isLoading: questionsLoading } =
    useGetQuestionsFrequenciesApiV2AnalyticsQuestionsFrequenciesGet({
      min_count: minCount,
      limit: limitQuestions,
      question_contains: questionQuery || undefined,
    });
  const { data: topQuestionsData, isLoading: topQuestionsLoading } =
    useGetTopQuestionsApiV2AnalyticsTopQuestionsGet({
      limit: limitTopQuestions,
      min_count: minCount,
    });
  const { data: companiesQuestionsData, isLoading: companiesQuestionsLoading } =
    useGetCompaniesQuestionsApiV2AnalyticsCompaniesQuestionsGet({
      company: companyFilter || undefined,
      min_count: minCount,
      limit_per_company: limitPerCompany,
    });

  const topics = topicsData ?? [];
  const heatmap = heatmapData ?? null;
  const trends = trendsData ?? [];
  const profiles = profilesData ?? [];
  const coocc = cooccData ?? [];
  const questions = questionsData ?? [];
  const topQuestions = topQuestionsData ?? [];
  const companiesQuestions = companiesQuestionsData ?? [];
  const loading =
    topicsLoading ||
    heatmapLoading ||
    trendsLoading ||
    profilesLoading ||
    cooccLoading ||
    questionsLoading ||
    topQuestionsLoading ||
    companiesQuestionsLoading;

  const topTopicsData = useMemo(
    () =>
      topics.map((r) => ({ name: r.cluster_label, count: Number(r.count) })),
    [topics]
  );

  const heatmapOption = useMemo(() => {
    if (!heatmap) return undefined;
    return {
      tooltip: { position: 'top' },
      grid: { height: '70%', top: '10%' },
      xAxis: {
        type: 'category',
        data: heatmap.topics,
        splitArea: { show: true },
        axisLabel: { rotate: 45, fontSize: 10 },
      },
      yAxis: {
        type: 'category',
        data: heatmap.companies,
        splitArea: { show: true },
      },
      visualMap: {
        min: 0,
        max: 1,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '2%',
      },
      series: [
        {
          name: 'Intensity',
          type: 'heatmap',
          data: heatmap.values.flatMap((row, i) =>
            row.map((v, j) => [j, i, v])
          ),
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' },
          },
        },
      ],
    } as echarts.EChartsOption;
  }, [heatmap]);

  if (loading) return <div className={styles.wrapper}>Загрузка аналитики…</div>;

  return (
    <div className={styles.wrapper}>
      <h2>Аналитика вопросов собеседований</h2>

      <section className={styles.controls}>
        <div className={styles.controlsRow}>
          <div className={styles.field}>
            <label>Нормализация heatmap</label>
            <select
              value={heatmapNorm}
              onChange={(e) => setHeatmapNorm(e.target.value as any)}
            >
              <option value="row">row</option>
              <option value="col">col</option>
              <option value="none">none</option>
            </select>
          </div>
          <div className={styles.field}>
            <label>min_count</label>
            <input
              type="number"
              min={1}
              value={minCount}
              onChange={(e) => setMinCount(Number(e.target.value) || 1)}
            />
          </div>
          <div className={styles.field}>
            <label>Лимит «Все вопросы»</label>
            <input
              type="number"
              min={10}
              value={limitQuestions}
              onChange={(e) => setLimitQuestions(Number(e.target.value) || 200)}
            />
          </div>
          <div className={styles.field}>
            <label>Лимит «Топ вопросов»</label>
            <input
              type="number"
              min={10}
              value={limitTopQuestions}
              onChange={(e) =>
                setLimitTopQuestions(Number(e.target.value) || 50)
              }
            />
          </div>
          <div className={styles.field}>
            <label>Лимит «Топ категорий»</label>
            <input
              type="number"
              min={10}
              value={limitTopics}
              onChange={(e) => setLimitTopics(Number(e.target.value) || 50)}
            />
          </div>
          <div className={styles.field}>
            <label>Лимит на компанию</label>
            <input
              type="number"
              min={10}
              value={limitPerCompany}
              onChange={(e) => setLimitPerCompany(Number(e.target.value) || 50)}
            />
          </div>
        </div>
        <div className={styles.controlsRow}>
          <div className={styles.field}>
            <label>Поиск по вопросу</label>
            <input
              type="text"
              placeholder="например: замыкания, event loop"
              value={questionQuery}
              onChange={(e) => setQuestionQuery(e.target.value)}
            />
          </div>
          <div className={styles.field}>
            <label>Фильтр по компании</label>
            <input
              type="text"
              placeholder="точное имя компании"
              value={companyFilter}
              onChange={(e) => setCompanyFilter(e.target.value)}
            />
          </div>
        </div>
      </section>

      <section className={styles.block}>
        <h3>Топ тем</h3>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topTopicsData} margin={{ left: 8, right: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" hide />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" name="Количество" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className={styles.block}>
        <h3>Топ категорий (таблица)</h3>
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Категория</th>
                <th>Кол-во</th>
              </tr>
            </thead>
            <tbody>
              {topics.map((r, idx) => (
                <tr key={idx}>
                  <td>{idx + 1}</td>
                  <td>{r.cluster_label}</td>
                  <td>{r.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.block}>
        <h3>Heatmap компания × тема (row-normalized)</h3>
        <div className={styles.chart}>
          {heatmapOption && (
            <ReactECharts option={heatmapOption} style={{ height: 400 }} />
          )}
        </div>
      </section>

      <section className={styles.block}>
        <h3>Все вопросы и где встречались</h3>
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>Вопрос</th>
                <th>Всего</th>
                <th>Компании (топ)</th>
              </tr>
            </thead>
            <tbody>
              {questions.map((r, i) => (
                <tr key={i}>
                  <td style={{ maxWidth: 680 }}>{r.question_text}</td>
                  <td>{r.total_count}</td>
                  <td>
                    {(r.companies || [])
                      .slice(0, 8)
                      .map((c) => `${c.company} (${c.count})`)
                      .join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.block}>
        <h3>Все компании и какие вопросы спрашивали</h3>
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>Компания</th>
                <th>Всего</th>
                <th>Вопросы (топ по count)</th>
              </tr>
            </thead>
            <tbody>
              {companiesQuestions.map((r, i) => (
                <tr key={i}>
                  <td>{r.company}</td>
                  <td>{r.total_questions}</td>
                  <td>
                    {r.items
                      .slice(0, 10)
                      .map((it) => `${it.question_text} (${it.count})`)
                      .join('; ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.block}>
        <h3>Топ вопросов по встречаемости</h3>
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Вопрос</th>
                <th>Всего</th>
              </tr>
            </thead>
            <tbody>
              {topQuestions.map((r, idx) => (
                <tr key={idx}>
                  <td>{idx + 1}</td>
                  <td style={{ maxWidth: 680 }}>{r.question_text}</td>
                  <td>{r.total_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className={styles.block}>
        <h3>Тренды по месяцам (кол-во на тему)</h3>
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>Месяц</th>
                <th>Тема</th>
                <th>Кол-во</th>
              </tr>
            </thead>
            <tbody>
              {trends.slice(0, 100).map((r, i) => (
                <tr key={i}>
                  <td>{r.month}</td>
                  <td>{r.cluster_label}</td>
                  <td>{r.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.block}>
        <h3>Профили компаний (топ тем)</h3>
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>Компания</th>
                <th>Ранг</th>
                <th>Тема</th>
                <th>Кол-во</th>
                <th>Доля</th>
              </tr>
            </thead>
            <tbody>
              {profiles.map((r, i) => (
                <tr key={i}>
                  <td>{r.company}</td>
                  <td>{r.rank}</td>
                  <td>{r.cluster_label}</td>
                  <td>{r.count}</td>
                  <td>{r.share ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.block}>
        <h3>Ко-оккуренции тем (top 100)</h3>
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>Тема A</th>
                <th>Тема B</th>
                <th>Кол-во</th>
              </tr>
            </thead>
            <tbody>
              {coocc.map((r, i) => (
                <tr key={i}>
                  <td>{r.cluster_label_a}</td>
                  <td>{r.cluster_label_b}</td>
                  <td>{r.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default AnalyticsPage;

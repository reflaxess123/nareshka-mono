import { Button, ButtonSize, ButtonVariant } from '@/shared/components/Button';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Brain,
  CheckCircle,
  Code2,
  Map,
  Sparkles,
  Star,
  Target,
  Trophy,
  Users,
  Zap,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import styles from './Landing.module.scss';

const Landing = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/get-started');
  };

  return (
    <div className={styles.landing}>
      <section className={styles.hero}>
        <div className={styles.container}>
          <motion.div
            className={styles.heroContent}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className={styles.heroText}>
              <motion.div
                className={styles.badge}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Sparkles size={16} />
                <span>Хватит бояться собеседований!</span>
              </motion.div>

              <motion.h1
                className={styles.heroTitle}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                Пройди собеседование в{' '}
                <span className={styles.gradient}>любую IT-компанию</span>{' '}
                России
              </motion.h1>

              <motion.p
                className={styles.heroDescription}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                Начни решать реальные задачи с собеседований уже сейчас — через
                пару месяцев будешь уверенно проходить технические этапы в
                Яндексе, VK, Сбере и других топовых компаниях
              </motion.p>

              <motion.div
                className={styles.heroActions}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <Button
                  variant={ButtonVariant.PRIMARY}
                  size={ButtonSize.LG}
                  onClick={handleGetStarted}
                  className={styles.ctaButton}
                >
                  <Zap size={20} />
                  Начать бесплатно
                  <ArrowRight size={20} />
                </Button>
              </motion.div>

              <motion.div
                className={styles.socialProof}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
              >
                <div className={styles.stats}>
                  <div className={styles.stat}>
                    <Users size={16} />
                    <span>500+ успешных кандидатов</span>
                  </div>
                  <div className={styles.stat}>
                    <Code2 size={16} />
                    <span>1000+ реальных задач</span>
                  </div>
                  <div className={styles.stat}>
                    <Star size={16} />
                    <span>50+ IT-компаний</span>
                  </div>
                </div>
              </motion.div>
            </div>

            <motion.div
              className={styles.heroVisual}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4, duration: 0.8 }}
            >
              <div className={styles.brainContainer}>
                <Brain size={120} className={styles.brainIcon} />
                <div className={styles.orbitingElements}>
                  <div className={styles.orbitingElement}>
                    <Code2 size={24} />
                  </div>
                  <div className={styles.orbitingElement}>
                    <Map size={24} />
                  </div>
                  <div className={styles.orbitingElement}>
                    <Target size={24} />
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className={styles.problem}>
        <div className={styles.container}>
          <motion.div
            className={styles.problemContent}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className={styles.problemTitle}>
              Знакомо? Ты не один такой...
            </h2>
            <div className={styles.problemList}>
              <div className={styles.problemItem}>
                <span className={styles.problemEmoji}>😰</span>
                <p>
                  Боишься технических собеседований и не знаешь, с чего начать
                  подготовку?
                </p>
              </div>
              <div className={styles.problemItem}>
                <span className={styles.problemEmoji}>🤯</span>
                <p>
                  Изучаешь теорию, но на собесе не можешь решить даже простые
                  задачи?
                </p>
              </div>
              <div className={styles.problemItem}>
                <span className={styles.problemEmoji}>😵</span>
                <p>Получаешь отказы и не понимаешь, что делаешь не так?</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section className={styles.features}>
        <div className={styles.container}>
          <motion.div
            className={styles.sectionHeader}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className={styles.sectionTitle}>
              Как <span className={styles.gradient}>Nareshka</span> поможет
              тебе?
            </h2>
            <p className={styles.sectionDescription}>
              Система подготовки, основанная на реальном опыте прохождения сотен
              собеседований
            </p>
          </motion.div>

          <div className={styles.featuresGrid}>
            <motion.div
              className={styles.featureCard}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
            >
              <div className={styles.featureIcon}>
                <Target size={32} />
              </div>
              <h3 className={styles.featureTitle}>Реальные задачи с собесов</h3>
              <p className={styles.featureDescription}>
                Более 1000 задач, которые реально спрашивают в Яндексе, VK,
                Сбере и других топовых компаниях. Никакой воды — только то, что
                пригодится на собеседовании.
              </p>
            </motion.div>

            <motion.div
              className={styles.featureCard}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              <div className={styles.featureIcon}>
                <Code2 size={32} />
              </div>
              <h3 className={styles.featureTitle}>Встроенный редактор кода</h3>
              <p className={styles.featureDescription}>
                Решай задачи прямо в браузере, как на настоящем собеседовании.
                Поддержка JavaScript, TypeScript, Python и других языков.
              </p>
            </motion.div>

            <motion.div
              className={styles.featureCard}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              <div className={styles.featureIcon}>
                <Map size={32} />
              </div>
              <h3 className={styles.featureTitle}>
                Интерактивная карта навыков
              </h3>
              <p className={styles.featureDescription}>
                Визуализируй свой прогресс и понимай, какие темы нужно
                подтянуть. От основ JavaScript до системного дизайна.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      <section className={styles.socialProofSection}>
        <div className={styles.container}>
          <motion.div
            className={styles.socialProofContent}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className={styles.socialProofTitle}>
              Результаты говорят сами за себя
            </h2>

            <div className={styles.achievements}>
              <div className={styles.achievement}>
                <Trophy size={32} />
                <div className={styles.achievementText}>
                  <div className={styles.achievementNumber}>85%</div>
                  <div className={styles.achievementLabel}>
                    Успешных собеседований
                  </div>
                </div>
              </div>

              <div className={styles.achievement}>
                <Target size={32} />
                <div className={styles.achievementText}>
                  <div className={styles.achievementNumber}>3</div>
                  <div className={styles.achievementLabel}>
                    Месяца до первого оффера
                  </div>
                </div>
              </div>

              <div className={styles.achievement}>
                <Zap size={32} />
                <div className={styles.achievementText}>
                  <div className={styles.achievementNumber}>2-3x</div>
                  <div className={styles.achievementLabel}>Рост зарплаты</div>
                </div>
              </div>
            </div>

            <div className={styles.companies}>
              <p className={styles.companiesLabel}>
                Наши выпускники работают в:
              </p>
              <div className={styles.companiesList}>
                {[
                  'Яндекс',
                  'VK',
                  'Сбер',
                  'Авито',
                  'Ozon',
                  'Wildberries',
                  'Тинькофф',
                  'Mail.ru',
                ].map((company) => (
                  <span key={company} className={styles.companyTag}>
                    {company}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section className={styles.premium}>
        <div className={styles.container}>
          <motion.div
            className={styles.premiumCard}
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <div className={styles.premiumContent}>
              <div className={styles.premiumHeader}>
                <div className={styles.premiumBadge}>
                  <Sparkles size={16} />
                  <span>Nareshka+</span>
                </div>
                <h2 className={styles.premiumTitle}>
                  Получи гарантированный результат
                </h2>
                <p className={styles.premiumDescription}>
                  Премиум-план для тех, кто серьёзно настроен получить оффер в
                  топовых компаниях
                </p>
              </div>

              <div className={styles.premiumFeatures}>
                <div className={styles.premiumFeature}>
                  <CheckCircle size={20} />
                  <span>Эксклюзивные задачи от FAANG</span>
                </div>
                <div className={styles.premiumFeature}>
                  <CheckCircle size={20} />
                  <span>Разборы с экс-интервьюерами</span>
                </div>
                <div className={styles.premiumFeature}>
                  <CheckCircle size={20} />
                  <span>Персональный план подготовки</span>
                </div>
                <div className={styles.premiumFeature}>
                  <CheckCircle size={20} />
                  <span>Мок-интервью с фидбеком</span>
                </div>
              </div>

              <div className={styles.premiumAction}>
                <Button
                  variant={ButtonVariant.PRIMARY}
                  size={ButtonSize.LG}
                  className={styles.premiumButton}
                >
                  <Star size={20} />
                  Оформить Nareshka+
                </Button>
                <p className={styles.premiumNote}>
                  Гарантия возврата денег в течение 30 дней
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section className={styles.cta}>
        <div className={styles.container}>
          <motion.div
            className={styles.ctaContent}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className={styles.ctaTitle}>
              Готов перестать бояться собеседований?
            </h2>
            <p className={styles.ctaDescription}>
              Присоединяйся к сотням разработчиков, которые уже получили офферы
              в топовых IT-компаниях благодаря Nareshka
            </p>
            <Button
              variant={ButtonVariant.PRIMARY}
              size={ButtonSize.LG}
              onClick={handleGetStarted}
              className={styles.ctaButton}
            >
              <Zap size={20} />
              Начать подготовку прямо сейчас
            </Button>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Landing;

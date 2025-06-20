import { PageWrapper } from '@/shared/components/PageWrapper';
import {
  Text,
  TextAlign,
  TextSize,
  TextWeight,
} from '@/shared/components/Text';
import { useTheme } from '@/shared/context';
import { Moon, Sun } from 'lucide-react';
import styles from './Settings.module.scss';

const Settings = () => {
  const { theme, setTheme } = useTheme();

  const handleThemeToggle = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const getThemeIcon = () => {
    return theme === 'light' ? <Sun size={18} /> : <Moon size={18} />;
  };

  const getThemeText = () => {
    return theme === 'light'
      ? 'Переключить на темную тему'
      : 'Переключить на светлую тему';
  };

  return (
    <PageWrapper>
      <div className={styles.settings}>
        <Text
          text="Настройки"
          size={TextSize.XXL}
          weight={TextWeight.MEDIUM}
          align={TextAlign.CENTER}
        />

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Внешний вид</h3>

          <div className={styles.settingItem}>
            <div className={styles.settingLabel}>
              <div className={styles.settingName}>Тема</div>
              <div className={styles.settingDescription}>
                Выберите светлую или темную тему интерфейса
              </div>
            </div>
            <button className={styles.themeButton} onClick={handleThemeToggle}>
              {getThemeIcon()}
              {getThemeText()}
            </button>
          </div>
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Уведомления</h3>

          <div className={styles.settingItem}>
            <div className={styles.settingLabel}>
              <div className={styles.settingName}>Email уведомления</div>
              <div className={styles.settingDescription}>
                Получать уведомления о новых заданиях и обновлениях
              </div>
            </div>
            <div>Скоро...</div>
          </div>
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Аккаунт</h3>

          <div className={styles.settingItem}>
            <div className={styles.settingLabel}>
              <div className={styles.settingName}>Экспорт данных</div>
              <div className={styles.settingDescription}>
                Скачать все ваши данные в формате JSON
              </div>
            </div>
            <div>Скоро...</div>
          </div>
        </div>
      </div>
    </PageWrapper>
  );
};

export default Settings;

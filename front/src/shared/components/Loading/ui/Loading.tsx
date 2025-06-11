import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import styles from './Loading.module.scss';

export const Loading = () => {
  return (
    <PageWrapper onOpenLogin={undefined}>
      <div className={styles.center}>
        <div className={styles.loader}></div>
      </div>
    </PageWrapper>
  );
};

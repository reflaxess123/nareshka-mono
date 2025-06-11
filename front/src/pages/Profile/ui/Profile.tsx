import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import {
  Text,
  TextAlign,
  TextSize,
  TextWeight,
} from '@/shared/components/Text';
import styles from './Profile.module.scss';

const Profile = () => {
  return (
    <PageWrapper>
      <div className={styles.profile}>
        <Text
          text="Профиль"
          size={TextSize.XXL}
          weight={TextWeight.MEDIUM}
          align={TextAlign.CENTER}
        />
      </div>
    </PageWrapper>
  );
};

export default Profile;

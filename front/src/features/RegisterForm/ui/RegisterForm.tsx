import { LoginForm } from '@/features/LoginForm';
import { ButtonVariant } from '@/shared/components/Button/model/types';
import { Button } from '@/shared/components/Button/ui/Button';
import { Input } from '@/shared/components/Input';
import { useModal } from '@/shared/hooks';
import { useRegister } from '@/shared/hooks/useAuth';
import { useRegisterForm } from '../model/hooks';
import type { RegisterFormSchema } from '../model/schema';
import styles from './RegisterForm.module.scss';

export const RegisterForm = () => {
  const { register, handleSubmit, formState, getFieldError } =
    useRegisterForm();

  const registerMutation = useRegister();

  const loginModal = useModal('login-modal');
  const registerModal = useModal('register-modal');

  const handleOpenLogin = () => {
    loginModal.open(<LoginForm />);
    registerModal.close();
  };

  const onSubmit = (data: RegisterFormSchema) => {
    registerMutation.mutate({ email: data.username, password: data.password });
  };

  return (
    <>
      <div className={styles.registerForm}>
        <p className={styles.title}>Register form</p>

        {registerMutation.error && (
          <p className={styles.error}>{registerMutation.error.message}</p>
        )}

        {formState.errors.username && (
          <p className={styles.error}>{getFieldError('username')}</p>
        )}
        <Input
          {...register('username')}
          type="email"
          placeholder="Email"
          fullWidth
        />

        {formState.errors.password && (
          <p className={styles.error}>{getFieldError('password')}</p>
        )}
        <Input
          {...register('password')}
          type="password"
          placeholder="Password"
          fullWidth
        />

        <div className={styles.buttons}>
          <Button
            type="button"
            variant={ButtonVariant.GHOST}
            disabled={registerMutation.isPending || formState.isSubmitting}
            onClick={handleOpenLogin}
          >
            Login
          </Button>
          <Button
            type="button"
            onClick={handleSubmit(onSubmit)}
            disabled={registerMutation.isPending || formState.isSubmitting}
          >
            {registerMutation.isPending ? 'Loading...' : 'Register'}
          </Button>
        </div>
      </div>
    </>
  );
};

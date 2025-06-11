import clsx from 'clsx';
import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { ButtonSize, ButtonVariant } from '../model/types';
import styles from './Button.module.scss';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  fullWidth?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Button = ({
  children,
  variant = ButtonVariant.PRIMARY,
  size = ButtonSize.MD,
  isLoading = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  disabled,
  className,
  ...props
}: ButtonProps) => {
  return (
    <button
      className={clsx(
        styles.button,
        styles[variant],
        styles[size],
        {
          [styles.loading]: isLoading,
          [styles.fullWidth]: fullWidth,
          [styles.disabled]: disabled || isLoading,
        },
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <div className={styles.spinner} />}
      {!isLoading && leftIcon && (
        <span className={styles.leftIcon}>{leftIcon}</span>
      )}
      <span className={styles.content}>{children}</span>
      {!isLoading && rightIcon && (
        <span className={styles.rightIcon}>{rightIcon}</span>
      )}
    </button>
  );
};

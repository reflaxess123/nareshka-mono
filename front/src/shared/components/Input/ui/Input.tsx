import clsx from 'clsx';
import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';
import { InputSize } from '../model/types';
import styles from './Input.module.scss';

interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  error?: string;
  helperText?: string;
  size?: InputSize;
  fullWidth?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      size = InputSize.MD,
      fullWidth = false,
      leftIcon,
      rightIcon,
      className,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div
        className={clsx(styles.inputWrapper, { [styles.fullWidth]: fullWidth })}
      >
        {label && (
          <label htmlFor={inputId} className={styles.label}>
            {label}
          </label>
        )}

        <div
          className={clsx(styles.inputContainer, styles[size], {
            [styles.error]: error,
            [styles.hasLeftIcon]: leftIcon,
            [styles.hasRightIcon]: rightIcon,
          })}
        >
          {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}

          <input
            ref={ref}
            id={inputId}
            className={clsx(styles.input, className)}
            {...props}
          />

          {rightIcon && <span className={styles.rightIcon}>{rightIcon}</span>}
        </div>

        {(error || helperText) && (
          <div className={clsx(styles.helpText, { [styles.errorText]: error })}>
            {error || helperText}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

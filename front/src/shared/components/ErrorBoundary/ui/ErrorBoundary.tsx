import type { ReactNode } from 'react';
import { Component } from 'react';
import { Button } from '../../Button/ui/Button';
import { Text, TextAlign, TextSize, TextWeight } from '../../Text';
import styles from './ErrorBoundary.module.scss';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className={styles.errorBoundary}>
          <div className={styles.content}>
            <Text
              text="⚠️ Что-то пошло не так"
              size={TextSize.LG}
              weight={TextWeight.BOLD}
              align={TextAlign.CENTER}
              className={styles.title}
            />
            <Text
              text="Произошла неожиданная ошибка. Попробуйте обновить страницу или попробовать снова."
              align={TextAlign.CENTER}
              className={styles.message}
            />
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className={styles.details}>
                <summary>Техническая информация (только в разработке)</summary>
                <pre>{this.state.error.stack}</pre>
              </details>
            )}
            <div className={styles.actions}>
              <Button onClick={this.handleRetry}>Попробовать снова</Button>
              <Button onClick={() => window.location.reload()}>
                Обновить страницу
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

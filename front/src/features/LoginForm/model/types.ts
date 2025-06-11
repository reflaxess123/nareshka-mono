import type { FieldErrors, UseFormReturn } from 'react-hook-form';
import type { LoginFormSchema } from './schema';

export interface LoginFormState {
  isSubmitting: boolean;
  errors: FieldErrors<LoginFormSchema>;
  touched: Partial<Record<keyof LoginFormSchema, boolean>>;
}

export interface UseLoginFormReturn {
  // Данные формы
  formData: LoginFormSchema;
  formState: LoginFormState;

  // RHF методы
  register: UseFormReturn<LoginFormSchema>['register'];
  handleSubmit: (
    onValid: (data: LoginFormSchema) => void | Promise<void>
  ) => (e?: React.BaseSyntheticEvent) => Promise<void>;
  resetForm: () => void;

  // Дополнительные методы
  setValue: (field: keyof LoginFormSchema, value: string) => void;
  getFieldError: (field: keyof LoginFormSchema) => string | undefined;
}

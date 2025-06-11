import type { FieldErrors, UseFormReturn } from 'react-hook-form';
import type { RegisterFormSchema } from './schema';

export interface RegisterFormState {
  isSubmitting: boolean;
  errors: FieldErrors<RegisterFormSchema>;
  touched: Partial<Record<keyof RegisterFormSchema, boolean>>;
}

export interface UseRegisterFormReturn {
  // Данные формы
  formData: RegisterFormSchema;
  formState: RegisterFormState;

  // RHF методы
  register: UseFormReturn<RegisterFormSchema>['register'];
  handleSubmit: (
    onValid: (data: RegisterFormSchema) => void | Promise<void>
  ) => (e?: React.BaseSyntheticEvent) => Promise<void>;
  resetForm: () => void;

  // Дополнительные методы
  setValue: (field: keyof RegisterFormSchema, value: string) => void;
  getFieldError: (field: keyof RegisterFormSchema) => string | undefined;
}

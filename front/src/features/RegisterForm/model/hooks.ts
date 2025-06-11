import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { registerFormSchema, type RegisterFormSchema } from './schema';
import type { UseRegisterFormReturn } from './types';

export const useRegisterForm = (): UseRegisterFormReturn => {
  const form = useForm<RegisterFormSchema>({
    resolver: zodResolver(registerFormSchema),
  });

  return {
    formData: form.watch(),
    formState: {
      isSubmitting: form.formState.isSubmitting,
      errors: form.formState.errors,
      touched: form.formState.touchedFields,
    },

    // RHF методы
    register: form.register,
    handleSubmit: (onValid) => form.handleSubmit(onValid),
    resetForm: form.reset,

    // Дополнительные методы
    setValue: (field, value) => form.setValue(field, value),
    getFieldError: (field) => form.formState.errors[field]?.message,
  };
};

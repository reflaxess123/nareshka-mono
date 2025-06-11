import { z } from 'zod';

export const registerFormSchema = z.object({
  username: z
    .string()
    .min(1, 'Username is required')
    .email('Invalid email address'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(6, 'Password must be at least 6 characters'),
});

export type RegisterFormSchema = z.infer<typeof registerFormSchema>;

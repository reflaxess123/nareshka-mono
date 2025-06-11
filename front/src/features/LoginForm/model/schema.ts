import { z } from 'zod';

export const loginFormSchema = z.object({
  username: z.string().min(1, 'Username is required').email('Invalid email address'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(6, 'Password must be at least 6 characters'),
});

export type LoginFormSchema = z.infer<typeof loginFormSchema>;

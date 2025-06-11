import react from '@vitejs/plugin-react-swc';
import { defineConfig } from 'vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
      '@/shared': '/src/shared',
      '@/app': '/src/app',
      '@/pages': '/src/pages',
      '@/widgets': '/src/widgets',
      '@/features': '/src/features',
      '@/entities': '/src/entities',
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Только большие библиотеки выносим отдельно
          vendor: ['axios', 'date-fns', 'konva', 'socket.io-client'],
        },
      },
    },
    // Увеличиваем лимит предупреждения о размере чанков
    chunkSizeWarningLimit: 1500,
    // Включаем минификацию
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Убираем console.log в продакшене
        drop_debugger: true,
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:4000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
// asdasda

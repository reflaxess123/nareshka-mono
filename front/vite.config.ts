import react from '@vitejs/plugin-react-swc';
import { defineConfig } from 'vite';
import checker from 'vite-plugin-checker';
import { chromeMonitorPlugin } from './vite-plugin-chrome-monitor';

export default defineConfig({
  plugins: [
    react(),
    chromeMonitorPlugin(),
    checker({
      typescript: {
        tsconfigPath: './tsconfig.app.json',
        buildMode: false,
      },
      overlay: {
        initialIsOpen: false,
      },
    }),
  ],
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
      output: {},
    },
    chunkSizeWarningLimit: 1500,
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

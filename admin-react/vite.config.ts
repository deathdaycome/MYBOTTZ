import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/admin/' : '/',  // Используем '/' в разработке, '/admin/' в продакшене
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined,
        // Force new hash on each build
        entryFileNames: `assets/[name]-[hash]-${Date.now()}.js`,
        chunkFileNames: `assets/[name]-[hash]-${Date.now()}.js`,
        assetFileNames: `assets/[name]-[hash]-${Date.now()}.[ext]`
      }
    }
  },
  server: {
    proxy: {
      // Проксируем все API запросы на backend в режиме разработки
      '/admin/hosting': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/admin/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/admin/reports': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/admin/finance': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import { fileURLToPath, URL } from 'node:url'  // ← другой импорт

export default defineConfig({
  plugins: [react()],
  server: {
  allowedHosts: ['homeder.ru'],
    resolve: {
      alias: {
        'src': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
  }
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    // Proxy: en desarrollo, /api/* → http://localhost:8000/*
    // Evita problemas de CORS al hacer fetch desde el browser
    proxy: {
      '/alerts':   { target: 'http://localhost:8000', changeOrigin: true },
      '/vehicles': { target: 'http://localhost:8000', changeOrigin: true },
      '/reports':  { target: 'http://localhost:8000', changeOrigin: true },
      '/agent':    { target: 'http://localhost:8000', changeOrigin: true },
      '/voice':    { target: 'http://localhost:8000', changeOrigin: true },
      '/health':   { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})

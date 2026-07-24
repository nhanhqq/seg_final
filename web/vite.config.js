import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from 'tailwindcss'
import autoprefixer from 'autoprefixer'

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  },
  build: {
    outDir: '../static',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          lucide: ['lucide-react']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    minify: 'esbuild',
    esbuild: {
      drop: ['console', 'debugger']
    }
  },
  css: {
    postcss: {
      plugins: [
        tailwindcss,
        autoprefixer
      ]
    }
  }
})

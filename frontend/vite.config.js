import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // This is important for Docker
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true, // This helps with file watching in Docker
    },
    proxy: {
      '/api': {
        target: 'http://backend:5000', // Use the Docker service name 'backend'
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

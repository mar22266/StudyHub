import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    headers: {
      "Content-Security-Policy":
        "default-src 'self'; " +
        "script-src 'self'; " +
        "style-src 'self' 'unsafe-inline'; " +
        "img-src 'self' data:; " +
        "connect-src 'self' ws://localhost:5173; " +
        "object-src 'none'; " +
        "base-uri 'self'; " +
        "form-action 'self'; " +
        "frame-ancestors 'none'",
      "X-Frame-Options": "DENY",
    },
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api": {
        target: "http://backend:6001",
        changeOrigin: true,
      },
    },
  },
});

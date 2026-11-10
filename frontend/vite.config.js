import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_BACKEND_URL || "http://localhost:8000";

  return {
    plugins: [react()],
    server: {
      proxy: {
        "/chat": target,
        "/sessions": target,
        "/health": target,
      },
    },
    build: {
      outDir: "../backend/app/static",
      emptyOutDir: true,
    },
  };
});

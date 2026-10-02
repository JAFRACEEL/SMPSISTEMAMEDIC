import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// En DEV el navegador llama a /api en su propio origen y Vite reenvía al backend:
// sin CORS y sin URL absoluta en el código cliente.
// Dentro de Docker Compose el destino es el servicio `backend` (SMD_DEV_PROXY_TARGET).
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "SMD_");
  const destinoApi = env.SMD_DEV_PROXY_TARGET || "http://localhost:8000";
  return {
    plugins: [react(), tailwindcss()],
    server: {
      proxy: {
        "/api": { target: destinoApi },
      },
    },
  };
});

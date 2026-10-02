import { useCallback, useEffect, useState } from "react";
import { consultarSalud, ErrorHttp } from "./lib/http";
import { formatearFechaLima } from "./lib/fechas";

type Estado =
  | { tipo: "cargando" }
  | { tipo: "ok"; estado: string; consultadoUtc: string }
  | { tipo: "error"; mensaje: string };

export default function App() {
  const [estado, setEstado] = useState<Estado>({ tipo: "cargando" });

  const verificar = useCallback(async () => {
    setEstado({ tipo: "cargando" });
    try {
      const r = await consultarSalud();
      setEstado({ tipo: "ok", estado: r.status, consultadoUtc: new Date().toISOString() });
    } catch (e) {
      const mensaje = e instanceof ErrorHttp ? e.message : "Error inesperado.";
      setEstado({ tipo: "error", mensaje });
    }
  }, []);

  useEffect(() => {
    void verificar();
  }, [verificar]);

  return (
    <main className="mx-auto max-w-xl p-6">
      <h1 className="text-2xl font-bold text-slate-900">SISTEMAMEDIC - base técnica</h1>
      <section aria-labelledby="titulo-salud" className="mt-6">
        <h2 id="titulo-salud" className="text-lg font-semibold">
          Estado del servidor
        </h2>
        <div role="status" aria-live="polite" className="mt-2 text-slate-800">
          {estado.tipo === "cargando" && <p>Comprobando conexión…</p>}
          {estado.tipo === "ok" && (
            <p>
              Servidor disponible ({estado.estado}). Última comprobación:{" "}
              <time dateTime={estado.consultadoUtc}>{formatearFechaLima(estado.consultadoUtc)}</time>
            </p>
          )}
          {estado.tipo === "error" && (
            <p className="text-red-800">{estado.mensaje} Intente nuevamente.</p>
          )}
        </div>
        <button
          type="button"
          onClick={() => void verificar()}
          className="mt-3 rounded bg-blue-800 px-4 py-2 text-white focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400"
        >
          Reintentar
        </button>
      </section>
    </main>
  );
}

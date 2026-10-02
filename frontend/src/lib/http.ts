// Cliente HTTP mínimo. Sin auth, sin cookies, sin PHI en URL ni en logs.
// Toda la API vive bajo /api (contrato: GET /api/health). En DEV, Vite lo reenvía al backend.
const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "/api";
const TIEMPO_MAXIMO_MS = 8000;

export class ErrorHttp extends Error {
  constructor(
    message: string,
    public readonly estado: number | null,
  ) {
    super(message);
    this.name = "ErrorHttp";
  }
}

export async function obtenerJson<T>(ruta: string): Promise<T> {
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), TIEMPO_MAXIMO_MS);
  try {
    const respuesta = await fetch(`${BASE_URL}${ruta}`, {
      method: "GET",
      headers: { Accept: "application/json" },
      credentials: "omit",
      signal: control.signal,
    });
    if (!respuesta.ok) {
      throw new ErrorHttp("El servidor respondió con un error.", respuesta.status);
    }
    return (await respuesta.json()) as T;
  } catch (e) {
    if (e instanceof ErrorHttp) throw e;
    throw new ErrorHttp("No hay conexión con el servidor.", null);
  } finally {
    clearTimeout(temporizador);
  }
}

export interface EstadoSalud {
  status: string;
}

export const consultarSalud = (): Promise<EstadoSalud> => obtenerJson<EstadoSalud>("/health");

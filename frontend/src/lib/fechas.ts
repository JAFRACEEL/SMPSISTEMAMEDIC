// Fechas: el backend guarda UTC; la interfaz muestra America/Lima (UTC-5, sin horario de verano).
export const ZONA_HORARIA = "America/Lima";
export const IDIOMA = "es-PE";

const formateador = new Intl.DateTimeFormat(IDIOMA, {
  timeZone: ZONA_HORARIA,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

/** Convierte un instante UTC (ISO 8601 con Z/offset, o Date) a texto en hora de Lima. */
export function formatearFechaLima(utc: string | Date, conHuso = true): string {
  const fecha = utc instanceof Date ? utc : new Date(utc);
  if (Number.isNaN(fecha.getTime())) return "Fecha no válida";
  const texto = formateador.format(fecha);
  return conHuso ? `${texto} (hora de Lima)` : texto;
}

# ADR-007: Idioma, i18n y zona horaria

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE (Dirección Médica + Product Owner)
- **Fecha límite para decidir**: PENDIENTE - antes de F6
- **Fase que bloquea**: F6 (primera interfaz de uso real)
- **Fecha del borrador**: 2026-10-01

> Hallazgo M5 del Plan v1.2: el plan no define idioma ni zona horaria pese a tener campañas
> internacionales.

## 1. Contexto

El personal del Centro Médico trabaja en **español**. Las campañas traen **profesionales
visitantes internacionales** que pueden no hablarlo y que, según el ADR-003, podrían llegar a
registrar atenciones. Iquitos está en **America/Lima (UTC-5, sin horario de verano)**, pero
hay dos zonas en juego cuando alguien consulta desde fuera.

Falta el dato de Discovery: `CAMPAIGN_OPERATIONS.md` debe decir qué idiomas hablan los
visitantes y si realmente usan el sistema o solo atienden.

## 2. Zona horaria - **decidido, no hay opciones**

1. **Almacenamiento**: todas las marcas de tiempo en **UTC** (`timestamptz`).
2. **Presentación**: **America/Lima** por defecto, en toda la interfaz y en todo documento
   impreso.
3. **Sin ambigüedad**: cuando el momento importa clínica o legalmente (firma, break-glass,
   triaje, dispensación), se muestra el huso junto a la hora.
4. **Nunca** se guarda una hora local sin huso, ni se asume la zona del navegador para datos
   clínicos.
5. La conversión es de presentación: la lógica de negocio opera en UTC.

Esto no se somete a opciones porque cualquier otra elección produce errores de fecha en
registros clínicos.

## 3. Idioma - opciones

### Opción A: Solo español **(recomendada para la Oleada A)**
- Toda la interfaz, los mensajes y los documentos en español, con **tildes y ñ correctas**.
- Los visitantes que necesiten registrar lo hacen acompañados por personal local.
- **Ventajas**: sin costo de traducción ni de mantenimiento; una sola versión que probar.
- **Desventajas**: fricción real si un visitante debe usar el sistema solo.

### Opción B: Español + inglés desde el inicio
- **Ventajas**: cubre a la mayoría de visitantes internacionales.
- **Desventajas**: duplica el texto a mantener y a probar; la terminología clínica traducida
  mal es **peligrosa**; retrasa la Oleada A.

### Opción C: Arquitectura preparada para i18n, un solo idioma activo **(recomendada como complemento de A)**
- Los textos no se incrustan en el código: viven en un catálogo de mensajes desde el día uno.
- Se publica solo español; añadir inglés después es traducir, no refactorizar.
- **Ventajas**: coste casi nulo ahora, opción abierta después.
- **Desventajas**: una pequeña disciplina adicional en el frontend.

## 4. Recomendación

**A + C**: se publica solo en español, pero con los textos externalizados desde el inicio.
Si Discovery demuestra que los visitantes usan el sistema sin acompañamiento, se activa el
inglés en una oleada posterior, sin rehacer nada.

## 5. Decisiones adicionales que el ADR fija

1. **Codificación**: UTF-8 en toda la cadena (base, API, frontend, PDF, impresión).
   Las tildes y la **ñ** deben verse correctamente también en los documentos impresos y en los
   nombres de pacientes. Se prueba explícitamente.
2. **Ordenación y búsqueda**: comparación insensible a tildes y mayúsculas para buscar
   pacientes (`Núñez` encuentra `nunez`). Es un requisito de identidad, no cosmético.
3. **Formato de fecha en la interfaz**: `DD/MM/AAAA`. **En documentos y registros del
   proyecto**: `AAAA-MM-DD` (hallazgo F1 del Plan v1.2, formato inconsistente).
4. **Números y moneda**: formato peruano; moneda PEN. PENDIENTE confirmar si alguna campaña
   maneja otra moneda.
5. **Nombres extranjeros**: el modelo admite nombres sin apellido paterno/materno separados y
   caracteres no latinos. Se prueba con datos sintéticos.

## 6. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | ¿Los visitantes internacionales usan el sistema directamente? | Dirección Médica (tras Discovery) | Antes de F6 |
| 2 | ¿Se requiere inglés en la Oleada A? | Product Owner | Antes de F6 |
| 3 | ¿Alguna lengua originaria relevante en la población atendida? | Dirección Médica | Antes de F6 |
| 4 | ¿Alguna campaña maneja moneda distinta de PEN? | Administración | Antes de la oleada de caja |

## 7. Cómo se revierte

Con la opción C, añadir un idioma después es barato. Lo caro e irreversible es incrustar
textos en el código: por eso la externalización se exige **desde la primera pantalla de F6**.

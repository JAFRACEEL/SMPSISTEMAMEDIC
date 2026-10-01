# Registro de fuentes - SISTEMAMEDIC

> **BORRADOR - requiere aprobación.**
> Este registro guarda **la evidencia** de cada verificación normativa: qué documento se leyó,
> dónde, en qué versión y quién lo leyó. `NORMATIVE_MATRIX.md` resume; aquí está el respaldo.

## Reglas

1. Una entrada se completa **al leer la fuente primaria**, no antes.
2. "Verificado por" exige **nombre y rol de una persona**. Nunca "el equipo", "revisión
   documental" ni una IA. (Hallazgo A7 del Plan v1.2.)
3. Se registra la **vigencia**: una norma puede estar derogada o modificada.
4. Se guarda copia del documento (PDF) en `docs/regulatory/fuentes/` cuando la licencia lo
   permita, con el nombre `Rxx-<slug>-<AAAA-MM-DD>.pdf`.
5. Formato de fecha único: `AAAA-MM-DD` (hallazgo F1 del Plan v1.2).

## Registro

| Ref | Documento exacto (título y número) | URL consultada | Fecha de publicación | ¿Vigente? | Artículos relevantes | Copia local | Verificado por (nombre y rol) | Fecha de verificación |
|---|---|---|---|---|---|---|---|---|
| R1 | Ley 29733 | | | | | | | |
| R2 | DS 016-2024-JUS | | | | | | | |
| R3 | DS 016-2024-JUS art. 34 | | | | art. 34 | | | |
| R4 | RM 214-2018/MINSA - NTS 139 | | | | | | | |
| R5 | NTS 139 - retención de HCE | | | | | | | |
| R6 | RM 462-2023/MINSA | | | | | | | |
| R7 | Ley 27269 y reglamento | | | | | | | |
| R8 | RM 164-2025/MINSA | | | | | | | |
| R9 | RM 188-2026/MINSA | | | | | | | |
| R10 | RM 673-2025/MINSA | | | | | | | |
| R11 | Guía FHIR Perú v0.1 | | | | | | | |
| R12 | Ley 26842 | | | | | | | |
| R13 | Normativa RENIEC | | | | | | | |
| R14 | Normativa SUSALUD / RENIPRESS | | | | | | | |
| R15 | CIE-10 versión MINSA | | | | | | | |
| R16 | Normativa SUNAT CPE | | | | | | | |
| R17 | R.S. SUNAT 000075-2026 | | | | | | | |

## Consultas a asesor legal

Preguntas abiertas que una norma sola no resuelve. Cada una necesita respuesta escrita.

| # | Pregunta | Dirigida a | Respuesta | Fecha |
|---|---|---|---|---|
| Q1 | ¿Cuál es el plazo real de notificación de un incidente y a quién se notifica? ¿Aplican las 48 h del art. 34 del DS 016-2024-JUS a esta IPRESS? | Asesor legal / privacidad | PENDIENTE | |
| Q2 | ¿Esta IPRESS debe registrar banco(s) de datos personales ante la ANPD? ¿Cuántos y con qué denominación? | Asesor legal | PENDIENTE | |
| Q3 | ¿Se requiere EIPD para este sistema? ¿Con qué metodología? | Asesor legal | PENDIENTE | |
| Q4 | Plazos de retención, archivo y destrucción de la HCE según NTS 139, y qué se hace con lo que no se migra | Asesor legal + Dirección Médica | PENDIENTE | |
| Q5 | Requisitos técnicos concretos de la firma de documentos clínicos (RM 462-2023): tipo de certificado, formato, sello de tiempo | Asesor legal + resp. técnico | PENDIENTE | |
| Q6 | Campañas internacionales: base jurídica para el tratamiento por profesionales extranjeros y para cualquier transferencia internacional | Asesor legal | PENDIENTE | |
| Q7 | Menores y pacientes sin documento: requisitos de identificación y de consentimiento del representante | Asesor legal + Dirección Médica | PENDIENTE | |
| Q8 | RUC y régimen del Centro Médico: ¿obliga a CPE? ¿desde cuándo? | Administración + contador | PENDIENTE | |
| Q9 | ¿Existe obligación de reporte o interoperabilidad con SIHCE para esta IPRESS y en qué plazo? | Asesor legal + Dirección Médica | PENDIENTE | |
| Q10 | Contratos de encargado de tratamiento necesarios (hosting, digitalización, respaldos) | Asesor legal | PENDIENTE | |

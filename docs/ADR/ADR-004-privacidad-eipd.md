# ADR-004: Privacidad y EIPD

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE (requiere asesor legal / responsable de privacidad)
- **Fecha límite para decidir**: PENDIENTE - antes de F3
- **Fase que bloquea**: F3 y, en cascada, todo lo demás
- **Fecha del borrador**: 2026-10-01

> Se usa el término **EIPD** (evaluación de impacto en la protección de datos personales).
> **No** se usa "DPIA".

## 1. Contexto

El sistema trata **datos de salud**, categoría sensible bajo la Ley 29733 y el DS 016-2024-JUS.
Hay un agravante específico: la comunidad atendida es **pequeña**, por lo que la
reidentificación a partir de datos "anonimizados formalmente" es probable (hallazgo A4 del
Plan v1.2). Además hay campañas internacionales, menores y pacientes sin documento.

Estado normativo: **todo POR VERIFICAR** (`docs/regulatory/NORMATIVE_MATRIX.md`).

## 2. Decisiones propuestas

### D1. Solo datos sintéticos con IA **(firme, ya aplicada)**
En DEV, CI, STAGING y en cualquier herramienta de IA se usan **100 % datos sintéticos**.
La anonimización de datos reales la hacen **personas en entorno aislado** y su resultado
**no se expone** a Claude Code.
Corrige el §18 del Plan v1.2, que permitía datos "anonimizados formalmente aprobados".
Ya implementada en `docs/TEST_DATA_POLICY.md` y en `secrets_guard.py`.

### D2. EIPD
| Pregunta | Estado |
|---|---|
| ¿Es obligatoria para este tratamiento? | **PENDIENTE** - decide asesor legal (Q3) |
| Metodología | PENDIENTE |
| Alcance propuesto | Sistema completo, con foco en HCE, campañas internacionales y migración de históricos |
| Responsable | PENDIENTE |
| Fecha límite | **Antes de F3**: condiciona los demás ADR |

Recomendación técnica: **hacerla aunque no fuera obligatoria**. El riesgo de reidentificación
en una comunidad pequeña la justifica por sí solo.

### D3. Minimización por rol
La respuesta del backend contiene **solo** los campos que el rol puede ver. Nunca se envía
todo y se oculta en el cliente. Es un requisito verificable con una prueba sobre el cuerpo
de la respuesta.

### D4. Sin PHI en logs
Logs, URL, mensajes de error, trazas, analítica y telemetría contienen únicamente IDs
técnicos y `correlation_id`. Se prueba con una aserción sobre la salida capturada.

### D5. Banco(s) de datos y registro ante la ANPD
PENDIENTE - decide asesor legal (Q2): cuántos bancos, con qué denominación, y si deben
registrarse.

### D6. Encargados de tratamiento
Ningún tercero (hosting, digitalización, respaldos, soporte) accede a datos de salud sin
**contrato de encargado** firmado, con finalidad, instrucciones, confidencialidad, medidas de
seguridad, subencargados y destino de los datos al terminar. PENDIENTE - lista y contratos (Q10).

### D7. Transferencias internacionales
Por defecto, **no hay**. Si el ADR-001 elige nube fuera de Perú, o si una campaña exige
enviar datos al organizador, se documenta la base jurídica **antes** de contratar o enviar.
Lo que sale hacia un organizador es **agregado y anonimizado por una persona**.

### D8. Derechos ARCO
Canal, plazos y procedimiento: PENDIENTE. Registro en `data_subject_requests`.
El alcance del derecho de supresión sobre una HCE con retención obligatoria debe precisarlo
el asesor legal.

### D9. Retención
Remite al **ADR-003 §5**. Sin esos plazos, F3 no cierra.

### D10. Menores y campañas
Representante registrado con vínculo y evidencia. Consentimiento del representante;
PENDIENTE precisar edad y supuestos (Q7). En campañas, consentimiento específico y separado
para el uso de imágenes.

## 3. Consecuencias

- La EIPD y las respuestas Q1-Q10 son **prerrequisito de F3**. No es papeleo: condicionan el
  modelo de datos, la retención y la arquitectura.
- Los contratos de encargado tienen plazo de negociación: deben iniciarse ya.
- D1 tiene un costo real: construir un generador de datos sintéticos que reproduzca la
  complejidad real (sin documento, menores, duplicados, campañas) en vez de usar un volcado.
  Es un costo que se asume conscientemente.

## 4. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | ¿EIPD obligatoria? ¿Con qué metodología? | Asesor legal | Antes de F3 |
| 2 | ¿Cuántos bancos de datos y se registran? | Asesor legal | Antes de F3 |
| 3 | Designación escrita del responsable de privacidad | Dirección Médica | Antes de F3 |
| 4 | Plazo real de notificación de incidentes y destinatarios | Asesor legal | Antes de F3 |
| 5 | Bases jurídicas por tratamiento | Asesor legal | Antes de F3 |
| 6 | Contratos de encargado necesarios | Asesor legal | Antes de F4 |
| 7 | Canal y plazos ARCO | Asesor legal + Dirección | Antes de F6 |

## 5. Cómo se revierte

Una base jurídica mal elegida o una EIPD omitida se descubren tarde, normalmente en una
inspección o un incidente, y para entonces ya hay datos reales tratados. **No es reversible:
es rehacer.**

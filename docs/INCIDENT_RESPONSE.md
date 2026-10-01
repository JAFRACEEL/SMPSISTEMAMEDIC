# Respuesta a incidentes - SISTEMAMEDIC

> **BORRADOR - requiere aprobación.** Gate H3.
> Procedimiento de 7 pasos del Plan v1.2 §22.
> **El plazo de 48 h está POR VALIDAR con asesor legal.** No se afirma como firme.

## Qué es un incidente aquí

Cualquier evento que comprometa la **confidencialidad, integridad o disponibilidad** de
datos de salud o del sistema. Incluye, como mínimo:

- Acceso no autorizado a historias clínicas (interno o externo).
- Pérdida, borrado o alteración de información clínica.
- Exposición de un secreto (clave, token, certificado).
- **Datos reales de pacientes en el repositorio, en un prompt o en una herramienta de IA.**
- Pérdida o robo de un equipo con acceso al sistema.
- Caída prolongada que impide atender.
- Uso indebido de break-glass.

## Los 7 pasos

### 1. Detectar y registrar
- Quien detecta **anota la hora exacta** (UTC y America/Lima) y qué observó.
- Avisa de inmediato al **responsable técnico** y al **responsable de privacidad**.
- No borra nada, no "arregla" por su cuenta, no apaga el equipo sin indicación: se pierde evidencia.
- Se abre un registro en la bitácora de incidentes (tabla al final).

### 2. Contener
- Revocar sesiones y credenciales afectadas.
- Suspender la cuenta implicada (incluidas cuentas de visitantes).
- Aislar el equipo o el servicio comprometido.
- Si el riesgo es de alteración de la HCE: **bloquear escrituras** antes que mantener el servicio.
- Preservar logs y `audit_events` (copiar, nunca mover).

### 3. Evaluar el alcance
Responder por escrito:
- ¿Qué datos? ¿De cuántas personas? ¿Incluye datos de salud (sensibles)?
- ¿Desde cuándo? ¿Siguen expuestos?
- ¿Hubo exfiltración o solo acceso?
- ¿Se alteró o se perdió información clínica?
- ¿Hay riesgo para la salud o la seguridad de alguna persona?

### 4. Notificar internamente
Sin demora, y en todo caso **el mismo día**:
- Dirección Médica.
- Responsable de privacidad.
- Responsable técnico.
- Administración, si hay impacto económico o contractual.

### 5. Notificar externamente (si corresponde)

> **PLAZO POR VALIDAR CON ASESOR.** El Plan v1.2 §22 afirma 48 h como regla firme, pero la
> referencia R3 (DS 016-2024-JUS art. 34) está marcada "a validar". Hallazgo A8. Mientras no
> haya respuesta escrita del asesor (pregunta Q1 de `SOURCES_REGISTER.md`), se asume el
> **plazo más corto posible** y se actúa de inmediato.

| Destinatario | ¿Aplica? | Plazo | Estado |
|---|---|---|---|
| Autoridad de protección de datos (ANPD) | PENDIENTE | **POR VALIDAR** (¿48 h?) | PENDIENTE Q1 |
| Titulares afectados | PENDIENTE | **POR VALIDAR** | PENDIENTE Q1 |
| SUSALUD / MINSA | PENDIENTE | **POR VALIDAR** | PENDIENTE |
| Encargados de tratamiento implicados | Sí | Inmediato | - |

La notificación la decide y la firma una **persona** (responsable de privacidad con Dirección
Médica), nunca una IA.

### 6. Erradicar y recuperar
- Corregir la causa raíz, no solo el síntoma.
- Rotar **todos** los secretos que pudieron verse, aunque no haya certeza.
- Restaurar desde un respaldo **verificado**, con conciliación de conteos.
- Confirmar que el sistema vuelve a un estado íntegro antes de reabrir el acceso.
- Revisar `audit_events` para confirmar que no quedó acceso residual.

### 7. Lecciones aprendidas
En un plazo máximo de **PENDIENTE - define Dirección Médica** días:
- Informe escrito: qué pasó, por qué, qué se hizo, cuánto duró, a quién afectó.
- **Test de regresión** que detecte la misma falla (obligatorio).
- Actualización de controles, runbooks y capacitación.
- Revisión de si el incidente debió haberse prevenido en un gate anterior.

## Roles

| Rol | Quién | Contacto |
|---|---|---|
| Coordinador del incidente | PENDIENTE - completa Dirección Médica | PENDIENTE |
| Responsable técnico | PENDIENTE | PENDIENTE |
| Responsable de privacidad | PENDIENTE | PENDIENTE |
| Vocería (si hay impacto público) | PENDIENTE | PENDIENTE |
| Asesor legal | PENDIENTE | PENDIENTE |

**Suplente nombrado para cada rol**: PENDIENTE. Un incidente a las 2 de la mañana no espera
a que una sola persona conteste.

## Caso especial: datos reales en una herramienta de IA

Es un incidente de confidencialidad. Pasos adicionales:
1. Identificar exactamente qué se pegó y en qué sesión.
2. Eliminar el contenido del repositorio **y del historial de Git** si llegó allí.
3. Evaluar el alcance como en el paso 3; los datos enviados a un tercero pueden haberse
   almacenado aunque se borren del lado del usuario.
4. Notificar según el paso 5.
5. Reforzar `docs/TEST_DATA_POLICY.md` y revisar por qué el `secrets_guard.py` no lo detuvo.

## Bitácora de incidentes

| # | Fecha y hora (UTC) | Detectado por | Tipo | Alcance | Contención | Notificado a | Cerrado el | Informe |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

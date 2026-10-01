---
name: clinical-workflows
description: Máquinas de estado oficiales de SISTEMAMEDIC (cita, laboratorio, encounter, receta, campaña, cuenta visitante) con sus transiciones válidas y reglas de irreversibilidad. Úsala al diseñar, implementar, revisar o probar cualquier flujo clínico.
---

# Máquinas de estado clínicas - SISTEMAMEDIC

Regla general: **un estado solo cambia por una transición declarada aquí**. Cualquier otra
transición es un defecto **P0 o P1**. Toda transición registra actor, momento (UTC) y, cuando
se indica, motivo obligatorio.

## 1. Cita (`appointments`)

```
scheduled -> confirmed -> checked_in -> waiting -> triage -> in_care -> completed
```

Terminales: `cancelled`, `no_show`, `rescheduled`.

| Desde | Hacia | Condición |
|---|---|---|
| scheduled | confirmed, cancelled, rescheduled, no_show | - |
| confirmed | checked_in, cancelled, rescheduled, no_show | - |
| checked_in | waiting, cancelled | paciente presente |
| waiting | triage, cancelled | - |
| triage | in_care, waiting | triaje registrado |
| in_care | completed | atención registrada |
| completed | (ninguna) | terminal |

Reglas:
- `rescheduled` **debe apuntar a la nueva cita** (`rescheduled_to_id`). Sin eso, no es válida.
- `no_show` solo tras la hora programada más la tolerancia configurada.
- `cancelled` exige motivo y actor.
- Una cita completada no se reabre: se crea una nueva.
- **Concurrencia**: dos reservas del mismo cupo → solo una gana (restricción en base de datos).

## 2. Laboratorio (`lab_orders`)

```
ordered -> sample_pending -> sample_collected -> in_process -> result_entered -> validated -> delivered
```

Excepciones: `sample_rejected`, `cancelled`. Posterior a `validated`: `amended`.

| Desde | Hacia | Condición |
|---|---|---|
| ordered | sample_pending, cancelled | - |
| sample_pending | sample_collected, cancelled | - |
| sample_collected | in_process, sample_rejected | - |
| sample_rejected | sample_pending | nueva toma, con motivo |
| in_process | result_entered, sample_rejected | - |
| result_entered | validated | valida un profesional habilitado |
| validated | delivered, amended | - |
| delivered | amended | - |

Reglas:
- Un resultado `validated` **no se edita**: se emite `amended` con autor, fecha y motivo,
  conservando la versión anterior íntegra.
- `result_entered` y `validated` deben ser personas distintas cuando el rol lo permita.

## 3. Encuentro / HCE (`encounters`)

```
opened -> in_progress -> ready_to_sign -> signed (closed)
```

Posterior a `signed`: `addendum` (no es un estado del encuentro, es un registro adjunto).

| Desde | Hacia | Condición |
|---|---|---|
| opened | in_progress, cancelled | cancelar solo si no hay contenido clínico |
| in_progress | ready_to_sign | contenido mínimo completo |
| ready_to_sign | in_progress, signed | firma del profesional responsable |
| signed | (ninguna) | **terminal e inmutable** |

Reglas:
- **`signed` es inmutable.** Ninguna corrección modifica el contenido firmado.
- Corrección = `addenda` nuevo, con autor, fecha, motivo y referencia al original.
- Toda versión previa se conserva en `record_versions`.
- Un encuentro de **campaña** es un `Encounter` normal con `campaign_id`; **nunca** una
  historia paralela.

## 4. Receta (`prescriptions`)

```
draft -> signed -> partially_dispensed -> dispensed
```

Terminales adicionales: `cancelled`, `expired`.

| Desde | Hacia | Condición |
|---|---|---|
| draft | signed, cancelled | - |
| signed | partially_dispensed, dispensed, cancelled, expired | - |
| partially_dispensed | dispensed, expired, cancelled | - |
| dispensed | (ninguna) | terminal |

Reglas:
- **Un borrador no se dispensa jamás.** Es el error más probable y es **P0**.
- `expired` se calcula por la vigencia configurada, no se marca a mano.
- Cada dispensación descuenta stock de forma atómica; **nunca stock negativo**.
- Cancelar una receta firmada exige motivo y queda auditado.

## 5. Campaña (`campaigns`)

```
draft -> planning -> registration_open -> confirmed -> in_progress -> completed
```

Terminal adicional: `cancelled`.

Reglas:
- La campaña **no crea pacientes ni historias paralelos**: usa la identidad y la HCE existentes.
- Los profesionales visitantes se asocian a la campaña con cuentas temporales (sección 6).
- Al pasar a `completed` las cuentas visitantes asociadas se suspenden automáticamente.

## 6. Cuenta de profesional visitante (`visitor_accounts`)

```
invited -> verified -> active -> suspended | expired -> closed
```

Reglas:
- **Vencimiento obligatorio** en la creación; lo aplica el **backend**, no la interfaz.
- `active` exige MFA configurado (TOTP o FIDO2).
- `suspended` es reversible con autorización; `expired` y `closed` no lo son.
- Tras `expired` o `closed`, cualquier petición autenticada falla en el backend.

## 7. Qué probar siempre

Por cada máquina de estados:
1. Cada transición válida funciona.
2. **Cada transición inválida se rechaza** (no basta con no ofrecerla en la interfaz).
3. Los estados terminales son terminales.
4. La irreversibilidad se cumple: firmado, validado y dispensado no se editan.
5. Concurrencia: dos actores sobre el mismo registro.
6. Corte a mitad de transición: el estado queda consistente.
7. Cada transición sensible dejó rastro en `audit_events`.

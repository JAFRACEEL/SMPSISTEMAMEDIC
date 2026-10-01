# ADR-005: Break-glass (acceso de emergencia)

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE (Dirección Médica + revisor técnico independiente)
- **Fecha límite para decidir**: PENDIENTE - antes de F5
- **Fase que bloquea**: F5 (auth, RBAC, break-glass)
- **Fecha del borrador**: 2026-10-01

## 1. Contexto

El mínimo privilegio es correcto el 99 % del tiempo y peligroso en una emergencia: si un
médico no puede ver los antecedentes de un paciente que llega inconsciente, el control de
acceso mata. El break-glass resuelve esa tensión: **se permite el acceso, pero caro**
(con motivo, por tiempo limitado, con alerta y con revisión).

Sin break-glass pasa lo predecible: el personal comparte cuentas, y entonces no hay control
de acceso en absoluto.

## 2. Criterios

| # | Criterio | Peso |
|---|---|---|
| 1 | No bloquea una emergencia real | Alto |
| 2 | Deja rastro completo e inalterable | Alto |
| 3 | Disuade del uso rutinario | Alto |
| 4 | Es rápido de activar (segundos, no minutos) | Alto |
| 5 | Alguien lo revisa de verdad | Alto |

## 3. Opciones

### Opción A: Autorización previa de un supervisor
- **Ventajas**: control estricto.
- **Desventajas**: **no funciona de noche ni en fin de semana**. Si el supervisor no contesta,
  el paciente espera. **Descartada** para emergencias.

### Opción B: Autodeclaración con motivo + alerta + revisión posterior **(recomendada)**
- El usuario activa el acceso él mismo, escribiendo un motivo obligatorio.
- El acceso vence solo, en minutos.
- Se emite alerta inmediata.
- Una persona lo revisa después, obligatoriamente.
- **Ventajas**: nunca bloquea una emergencia; el rastro y la revisión son el verdadero control.
- **Desventajas**: el abuso se detecta después, no antes. Aceptable: en salud, el daño de
  bloquear suele superar al de un acceso indebido detectado y sancionado.

### Opción C: Mixta - autodeclaración para urgencias, autorización previa para el resto
- Añade complejidad; la frontera entre "urgencia" y "resto" la decide quien tiene prisa.
  PENDIENTE evaluar si Dirección Médica lo prefiere.

## 4. Decisiones que el ADR fija (si se aprueba B)

Los **cinco requisitos** son obligatorios; faltar uno es un hallazgo **P0**:

1. **Motivo escrito obligatorio**, texto libre, mínimo PENDIENTE caracteres. **No** una lista
   de opciones: una lista se clickea sin pensar.
2. **Tiempo limitado**: PENDIENTE - propuesta **15 minutos**, renovable con nuevo motivo.
   Lo aplica el **backend**, no la interfaz.
3. **Alerta inmediata** a Dirección Médica y al responsable de seguridad. Canal: PENDIENTE.
4. **Registro** en `break_glass_events` (actor, paciente, motivo, inicio, vencimiento) y en
   `audit_events` (cada acceso realizado durante la ventana).
5. **Revisión posterior obligatoria**: alguien nombrado revisa cada evento en un plazo máximo
   de PENDIENTE y deja constancia (`revisado_por`, `revisado_el`, veredicto).

Además:

6. **Reautenticación** al activar el break-glass (no basta la sesión abierta).
7. **Alcance acotado**: el break-glass da acceso a **un paciente**, no a toda la base.
8. **Visible**: mientras la ventana está activa, la interfaz lo muestra de forma inequívoca.
9. **Métrica**: número de activaciones por usuario y por mes. Un pico es señal de que los
   permisos normales están mal definidos, no necesariamente de abuso.

## 5. Qué NO es break-glass

- No es una forma de dar permisos que alguien necesita a diario. Si un rol lo usa todas las
  semanas, **el permiso está mal asignado**: se corrige el RBAC.
- No sirve para exportaciones masivas ni para administración.
- No lo pueden usar cuentas de profesionales visitantes sin autorización explícita
  (PENDIENTE decidir).

## 6. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | ¿Opción B o C? | Dirección Médica | Antes de F5 |
| 2 | Duración de la ventana | Dirección Médica + revisor indep. | Antes de F5 |
| 3 | ¿Qué roles pueden activarlo? ¿Los visitantes? | Dirección Médica | Antes de F5 |
| 4 | Canal de alerta y quién la recibe (con suplente) | Dirección Médica | Antes de F5 |
| 5 | Quién revisa los eventos y en qué plazo | Dirección Médica | Antes de F5 |
| 6 | Consecuencia de un uso injustificado | Dirección Médica + RR. HH. | Antes de F5 |

## 7. Cómo se revierte

Ajustar la duración, el alcance o el canal de alerta es barato en cualquier momento.
Lo que no se puede reconstruir después es el **rastro** de los accesos que ocurrieron sin él:
por eso el registro debe existir desde el primer día de F5.

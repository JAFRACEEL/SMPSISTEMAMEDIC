# Gobierno del proyecto - SISTEMAMEDIC

> **BORRADOR - requiere aprobación.** Gate H1.
> Las personas no están designadas: cada `PENDIENTE - completa [rol]` debe resolverlo una persona.

## 1. Roles

| Rol | Quién | Responsabilidad principal | Dedicación estimada |
|---|---|---|---|
| Dirección Médica | PENDIENTE - completa Dirección Médica | Decide lo clínico; aprueba H6, H7 y go-live | PENDIENTE |
| Product Owner | PENDIENTE - completa Dirección Médica | Prioriza alcance, resuelve dudas funcionales, controla el alcance | PENDIENTE |
| Responsable técnico | PENDIENTE - completa Dirección Médica | Construye y coordina a los agentes; **no puede ser el único** | PENDIENTE |
| Revisor técnico independiente | PENDIENTE - contratar antes de F3 | Revisa auth, RBAC, break-glass, auditoría e inmutabilidad | PENDIENTE |
| Responsable de privacidad / asesor legal | PENDIENTE - contratar antes de F3 | Valida Ley 29733, DS 016-2024-JUS, EIPD, plazos de notificación | PENDIENTE |
| Administración / contabilidad | PENDIENTE - completa Dirección | Define RUC, régimen, facturación, SUNAT/CPE | PENDIENTE |
| Champions por área | PENDIENTE (recepción, triaje, médico, laboratorio, farmacia, caja) | Validan en UAT y capacitan a sus pares | PENDIENTE |
| Pentester externo | PENDIENTE - contratar antes de F9A | Prueba de intrusión y reverificación | PENDIENTE |

**Regla de dependencia**: ningún rol crítico puede recaer en una sola persona sin suplente
nombrado. Ver `docs/CUSTODY_REGISTER.md`.

## 2. RACI por gate

R = responsable de ejecutar · A = aprueba · C = consultado · I = informado

| Gate | Dirección Médica | Product Owner | Resp. técnico | Revisor indep. | Privacidad/legal | Administración | Champions | Pentester |
|---|---|---|---|---|---|---|---|---|
| H1 F0+F1 técnica | A | C | R | I | C | I | I | - |
| H2 Discovery F2 | A | R | C | I | C | C | C | - |
| H3 ADR F3 | A | C | R | **A** | **A** | C | I | - |
| H4 F4+F4b | C | I | R | C | I | I | I | - |
| H5 F5 auth/RBAC | C | I | R | **A** | C | I | I | - |
| H6 F6 identidad/agenda | A | R | C | I | C | I | **A** (UAT) | - |
| H7 F7 HCE/firma | **A** | C | R | **A** | C | I | C | - |
| H8 F8A RC | A | C | R | C | I | I | C | - |
| H9 F9A pentest | A | I | R | C | C | I | I | **R** |
| H10 F10A migración | A | C | C | C | C | C | C | - |
| H11 F11A paralelo | **A** | C | C | I | C | C | R | - |
| H12 F12A go-live | **A** | A | C | I | C | C | C | - |
| Oleadas B-E | A | R | C | C | C | C | **A** (UAT) | C |

## 3. Mecanismo de aprobación

1. **Único registro válido: `docs/APPROVALS.md`.** Una fila aprobada exige
   estado `APROBADO`, aprobador (nombre y rol), fecha `AAAA-MM-DD` y evidencia.
2. **Solo una persona escribe ese archivo.** Está denegado por `permissions.deny` y por el
   hook `path_guard.py` para todos los agentes y para la sesión principal.
3. **Ninguna salida de una IA cuenta como aprobación**, por detallada que sea.
4. Si un gate no está aprobado, la fase siguiente **no se construye**. El agente informa qué
   falta, quién debe aprobarlo, y se detiene.
5. Los ADR se aprueban en `docs/ADR/` y se replican en la tabla de ADR de `APPROVALS.md`.

## 4. Cadencia y decisiones

| Ritual | Frecuencia | Participan | Salida |
|---|---|---|---|
| Revisión de avance | PENDIENTE - completa Product Owner | PO, resp. técnico | `docs/PROGRESS.md` actualizado |
| Comité de gate | Al cerrar cada fase | Según RACI | Fila en `APPROVALS.md` |
| Revisión de riesgos | PENDIENTE | Dirección, PO, resp. técnico | Registro de riesgos actualizado |
| Revisión de custodia | Trimestral | Dirección, resp. técnico | `CUSTODY_REGISTER.md` |

**Escalamiento**: duda funcional → Product Owner; duda clínica → Dirección Médica;
duda legal o de privacidad → asesor; duda técnica de seguridad → revisor independiente.

## 5. Control de alcance

- Todo cambio de alcance pasa por el Product Owner y queda escrito en `docs/MVP_SCOPE.md`.
- Un `LATER` no se mueve a `MUST` sin quitar otro `MUST` o mover la fecha.
- Las fases de construcción no empiezan sin su gate previo aprobado.

## 6. Qué NO hace la IA

- No aprueba gates ni ADR.
- No accede a datos reales, credenciales, staging ni PROD.
- No ejecuta migraciones reales, operación en paralelo ni go-live.
- No diagnostica, prescribe ni decide clínicamente.
- No sustituye validación clínica, legal, tributaria ni de protección de datos.

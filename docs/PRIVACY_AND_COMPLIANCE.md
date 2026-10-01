# Privacidad y cumplimiento - SISTEMAMEDIC

> **BORRADOR - requiere aprobación.** Gate H3.
> Esqueleto. Cada `PENDIENTE` lo completa el rol indicado; lo normativo requiere
> **asesor legal**. Nada aquí es asesoría jurídica.

Marco: Ley 29733, DS 016-2024-JUS, NTS 139 (RM 214-2018/MINSA), Ley 26842.
Estado de verificación: ver `docs/regulatory/NORMATIVE_MATRIX.md` (**todo POR VERIFICAR**).

## 1. Banco(s) de datos personales

| Campo | Valor |
|---|---|
| ¿Debe registrarse ante la ANPD? | PENDIENTE - completa asesor legal (Q2) |
| Denominación del banco de datos | PENDIENTE |
| Finalidad | PENDIENTE |
| Categorías de titulares | Pacientes, representantes de menores, personal, profesionales visitantes |
| Categorías de datos | Identificación, contacto, **datos de salud (sensibles)**, cobertura, imágenes |
| Flujo de datos | PENDIENTE - completa resp. técnico tras Discovery |
| Plazo de conservación | PENDIENTE - depende de NTS 139 (Q4) |

## 2. Responsable y encargados

| Rol | Quién | Pendiente |
|---|---|---|
| Responsable del tratamiento | Centro Médico, Parroquia San Martín de Porres | Confirmar la persona jurídica exacta y su RUC |
| Responsable operativo de privacidad | PENDIENTE - designa Dirección Médica | Designación escrita |
| Encargados de tratamiento | Hosting, digitalización, respaldos, soporte | **Contrato de encargado** por cada uno (Q10) |

Regla: **ningún encargado accede a datos de salud sin contrato firmado** que cubra
finalidad, instrucciones, confidencialidad, seguridad, subencargados y devolución o
destrucción al terminar.

## 3. Deber de informar

| Elemento | Estado |
|---|---|
| Aviso de privacidad (texto) | PENDIENTE - redacta asesor legal, revisa Dirección Médica |
| Versionado del aviso | Implementado en el modelo (`privacy_notices`) |
| Momento de entrega | En el primer registro del paciente y ante cada cambio de versión |
| Lenguaje | Español claro; **PENDIENTE** decidir si se requiere otra lengua (ADR-007) |
| Soporte | Papel y pantalla; se registra el canal |

## 4. Bases jurídicas y consentimientos

| Tratamiento | Base jurídica propuesta | Estado |
|---|---|---|
| Atención de salud y HCE | PENDIENTE - validar con asesor | POR VALIDAR |
| Facturación y cobranza | PENDIENTE | POR VALIDAR |
| Campañas de salud | PENDIENTE | POR VALIDAR |
| Uso de imágenes (fotografía clínica, difusión) | **Consentimiento específico** | POR VALIDAR |
| Reportes a autoridad sanitaria | PENDIENTE | POR VALIDAR |
| Investigación o docencia | **No contemplado en la Oleada A** | - |

Implementación: `consents` registra tipo, versión del aviso, fecha, canal, actor y revocación.

## 5. Derechos del titular (ARCO)

| Elemento | Estado |
|---|---|
| Canal de recepción de solicitudes | PENDIENTE - define Dirección Médica |
| Plazos de respuesta | PENDIENTE - confirma asesor legal |
| Registro de solicitudes | `data_subject_requests` (tipo, fecha, plazo, estado, resolución) |
| Verificación de identidad del solicitante | PENDIENTE - procedimiento |
| Límite del derecho de supresión sobre la HCE | **PENDIENTE** - la HCE tiene retención obligatoria; el asesor debe precisar el alcance |

## 6. Retención, archivo y destrucción de la HCE

**Hallazgo A6 del Plan v1.2: esto es un entregable obligatorio de F3, hoy ausente.**

| Elemento | Estado |
|---|---|
| Plazo de conservación de la HCE | PENDIENTE - NTS 139 (Q4) **POR VALIDAR** |
| Plazo para historias de pacientes fallecidos | PENDIENTE |
| Archivo intermedio (qué sale de línea y cuándo) | PENDIENTE |
| Procedimiento de destrucción y su constancia | PENDIENTE |
| Qué ocurre con el papel no digitalizado | PENDIENTE - ver `DATA_MIGRATION_PLAN.md` |
| Retención de la auditoría (`audit_events`) | PENDIENTE - decide ADR-006 |
| Retención de respaldos | PENDIENTE - decide ADR-001 |

## 7. Medidas de seguridad

Detalle en `.claude/skills/healthcare-security/SKILL.md` y en los ADR. Resumen:

- Autorización en backend (RBAC + ABAC), mínimo privilegio, separación de ámbitos.
- MFA obligatorio para administradores y médicos; cuentas personales.
- Break-glass con motivo, vencimiento, alerta y revisión posterior.
- Auditoría de accesos y cambios con **integridad verificable** (ADR-006).
- Cifrado en tránsito y en reposo; respaldos cifrados.
- **Sin PHI en logs.**
- **Solo datos sintéticos** en DEV, CI, STAGING y en cualquier IA.

## 8. Transferencias internacionales

| Caso | Estado |
|---|---|
| Hosting fuera de Perú | PENDIENTE - depende del ADR-001; si ocurre, requiere base jurídica documentada |
| Profesionales visitantes extranjeros accediendo desde el exterior | PENDIENTE (Q6); por defecto **el acceso desde fuera de la red está denegado** |
| Envío de datos a organizadores de campañas internacionales | PENDIENTE - solo agregados y anonimizados por una persona, nunca con IA |

## 9. EIPD (evaluación de impacto en la protección de datos)

> Se usa **EIPD**, no "DPIA".

| Elemento | Estado |
|---|---|
| ¿Es obligatoria? | PENDIENTE - decide asesor legal (Q3) |
| Metodología | PENDIENTE |
| Alcance | Sistema completo, con foco en HCE, campañas y migración de históricos |
| Responsable | PENDIENTE |
| Fecha límite | **Antes de F3**, porque condiciona los ADR |
| Riesgo específico ya identificado | Comunidad pequeña → **alta probabilidad de reidentificación** de datos "anonimizados" (hallazgo A4) |

## 10. Menores

- Representante legal registrado (`representatives`) con vínculo y evidencia.
- Consentimiento otorgado por el representante; **PENDIENTE** precisar la edad y los supuestos
  de consentimiento del propio menor (Q7).
- El menor no se registra con el documento del representante como propio.

## 11. Campañas internacionales

- Misma HCE, `Encounter` con `campaign_id`. No existe una base de datos de campaña aparte.
- Cuentas de profesionales visitantes: temporales, con vencimiento, MFA y mínimo privilegio.
- Consentimiento y aviso de privacidad entregados igual que a cualquier paciente.
- Cualquier dato que salga hacia el organizador: **agregado y anonimizado por una persona**,
  nunca por una IA, y con base jurídica documentada.

## 12. Pendientes que bloquean F3

1. Respuesta a Q1-Q10 de `docs/regulatory/SOURCES_REGISTER.md`.
2. Designación escrita del responsable de privacidad.
3. Decisión sobre la EIPD.
4. Política de retención de la HCE.
5. Verificación de R1-R5 y R12 en fuente primaria.

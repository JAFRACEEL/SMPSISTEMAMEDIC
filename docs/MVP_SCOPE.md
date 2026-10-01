# Alcance del MVP - Oleada A - SISTEMAMEDIC

> **BORRADOR - requiere aprobación.** Gate H1; el alcance definitivo depende de Discovery (H2).

## 1. Qué cubre la Oleada A

El circuito completo de una atención de consulta externa, de principio a fin, para que el
Centro Médico pueda operar con el sistema sin volver al papel a mitad del flujo.

Recepción → identificación → consentimiento → cita o atención directa → check-in →
cola → triaje → consulta (HCE) → diagnóstico CIE-10 → receta y órdenes → firma y cierre.

**No cubre**: laboratorio completo, farmacia con inventario, caja y facturación, reportes a
MINSA, interoperabilidad SIHCE. Esos son las oleadas B-E.

## 2. Alcance por módulo

### 2.1 Identidad y pacientes

| Prioridad | Requisito |
|---|---|
| **MUST** | Identificador interno siempre presente, opaco, generado por el sistema |
| **MUST** | `patient_identifiers` 0..n: DNI, CE, pasaporte, CPP, otro, con país emisor |
| **MUST** | Registro **sin ningún documento** (no bloquea la atención) |
| **MUST** | Flujo **NN / emergencia** con alias generado y cola de identificación pendiente |
| **MUST** | Menores con representante legal registrado y vínculo verificable |
| **MUST** | Búsqueda por documento y por apellidos + fecha de nacimiento |
| **MUST** | Detección de posible duplicado al registrar |
| **MUST** | **Merge auditado** con motivo y evidencia; marca `identity_uncertain` |
| SHOULD | Normalización de nombres (tildes, orden de apellidos) para la búsqueda |
| SHOULD | Foto del paciente para identificación visual |
| LATER | Validación en línea contra RENIEC |
| LATER | Reversión automatizada de un merge |

### 2.2 Consentimientos y privacidad

| Prioridad | Requisito |
|---|---|
| **MUST** | Aviso de privacidad versionado (`privacy_notices`) |
| **MUST** | Registro de consentimiento con tipo, versión del aviso, fecha, canal y actor |
| **MUST** | Revocación de consentimiento registrada |
| SHOULD | Registro de solicitudes ARCO (`data_subject_requests`) con plazos |
| SHOULD | Consentimiento específico para campañas y para uso de imágenes |
| LATER | Portal de autogestión del paciente |

### 2.3 Agenda y citas

| Prioridad | Requisito |
|---|---|
| **MUST** | Agenda por profesional y por servicio, con cupos |
| **MUST** | Crear, confirmar, reprogramar (`rescheduled_to_id`) y cancelar con motivo |
| **MUST** | `no_show` automático tras la tolerancia configurada |
| **MUST** | **Control de concurrencia**: dos reservas del mismo cupo, solo una gana |
| **MUST** | Atención sin cita previa (espontánea y emergencia) |
| SHOULD | Sobrecupo controlado con autorización |
| SHOULD | Vista de agenda del día imprimible (contingencia por corte) |
| LATER | Recordatorio automático al paciente |

### 2.4 Check-in y cola

| Prioridad | Requisito |
|---|---|
| **MUST** | Check-in en recepción (`checked_in` → `waiting`) |
| **MUST** | Cola visible por servicio, con prioridad por triaje |
| **MUST** | Llamado del paciente y registro de quién lo atiende |
| SHOULD | Pantalla de sala de espera sin PHI (solo número o iniciales) |
| LATER | Tiempos de espera históricos y analítica |

### 2.5 Triaje

| Prioridad | Requisito |
|---|---|
| **MUST** | Signos vitales y motivo de consulta |
| **MUST** | Clasificación de prioridad que reordena la cola |
| **MUST** | Registro de quién triajó y cuándo |
| SHOULD | Alertas por valores fuera de rango |
| LATER | Escala de triaje normalizada con validación clínica externa |

### 2.6 HCE - encuentro clínico

| Prioridad | Requisito |
|---|---|
| **MUST** | `Encounter` único y longitudinal; campaña = `campaign_id`, no historia aparte |
| **MUST** | Anamnesis, examen físico, plan |
| **MUST** | Alergias (`allergies`) visibles de forma destacada |
| **MUST** | Lista de problemas (`problem_list`) activa/resuelta |
| **MUST** | Antecedentes |
| SHOULD | Plantillas por tipo de consulta |
| LATER | Dictado por voz |

### 2.7 Diagnósticos

| Prioridad | Requisito |
|---|---|
| **MUST** | CIE-10 **versionado**: el diagnóstico guarda la versión del catálogo usada |
| **MUST** | Diagnóstico presuntivo y definitivo, con orden |
| **MUST** | Búsqueda del código por texto en español |
| LATER | Sugerencia de código asistida (sin decidir por el médico) |

### 2.8 Recetas y órdenes básicas

| Prioridad | Requisito |
|---|---|
| **MUST** | Receta en estados `draft → signed → …`; **un borrador no se dispensa jamás** |
| **MUST** | Impresión de receta legible con los datos obligatorios |
| **MUST** | Orden básica (laboratorio, imagen, procedimiento) en estado `ordered` |
| SHOULD | Catálogo de medicamentos con presentación y dosis habituales |
| SHOULD | Alerta de alergia al prescribir |
| LATER | Interacciones medicamentosas |
| LATER | Dispensación en farmacia (oleada posterior) |

### 2.9 Firma y cierre

| Prioridad | Requisito |
|---|---|
| **MUST** | `ready_to_sign → signed`; lo firmado es **inmutable** |
| **MUST** | **Addendum** con autor, fecha y motivo obligatorio |
| **MUST** | Versionado íntegro en `record_versions` |
| **MUST** | Firma conforme a RM 462-2023 (**POR VERIFICAR** el detalle técnico exigido) |
| **MUST** | Documento clínico firmado con hash (`signed_documents`) |
| SHOULD | Visor del documento firmado tal como se firmó |

### 2.10 Transversal (habilitado en F4-F5, usado por todo lo anterior)

| Prioridad | Requisito |
|---|---|
| **MUST** | Autenticación con MFA (TOTP/FIDO2) para administradores y médicos |
| **MUST** | RBAC por servicio, aplicado en el backend |
| **MUST** | Break-glass con motivo, vencimiento, alerta y revisión |
| **MUST** | Cuentas de visitantes con vencimiento aplicado en backend |
| **MUST** | Auditoría de accesos y cambios, con integridad verificable |
| **MUST** | Logs sin PHI |
| **MUST** | Respaldo y **restore probado** dentro del RTO |
| **MUST** | Modo degradado documentado y practicado (corte de energía/conectividad) |

## 3. Regla de control de alcance

1. Un requisito **LATER** no pasa a **MUST** sin que el Product Owner quite otro **MUST**
   o mueva la fecha. Se registra aquí con fecha y motivo.
2. Un **SHOULD** entra solo si todos los **MUST** de la oleada están cerrados.
3. Todo cambio de alcance se escribe en la tabla siguiente **antes** de implementarse.
4. Lo que descubra Discovery (F2) puede cambiar este documento; los cambios se consolidan en
   la síntesis previa a H2.

### Registro de cambios de alcance

| Fecha | Requisito | De → A | Qué se quitó o movió | Aprobado por |
|---|---|---|---|---|
| | | | | |

## 4. Criterio de éxito de la Oleada A

Una atención completa, de recepción a cierre firmado, realizada por el personal real en UAT
con datos sintéticos, sin recurrir al papel y sin un solo hallazgo P0 o P1 abierto.

---
name: healthcare-security
description: Controles de seguridad y privacidad obligatorios de SISTEMAMEDIC - RBAC/ABAC en backend, IDOR, MFA, sesiones en PC compartida, break-glass, cuentas visitantes, auditoría íntegra, logs sin PHI y gates S1-S13. Úsala al implementar o revisar cualquier acceso a datos clínicos.
---

# Seguridad y privacidad - SISTEMAMEDIC

## 1. Autorización

- **Siempre en el backend**, en cada endpoint y en cada consulta. Ocultar un botón no es
  seguridad y no cuenta como control.
- **RBAC** por rol funcional (recepción, enfermería/triaje, médico, laboratorio, farmacia,
  caja, administración, dirección, visitante) **+ ABAC** por atributo: servicio, sede,
  campaña, vínculo con la atención, vigencia de la cuenta.
- **Separación de ámbitos**: filiación, clínica, caja y administración son permisos distintos.
  Recepción no lee notas clínicas; caja no lee diagnósticos.
- **Mínimo privilegio** y **denegación por defecto**: lo no concedido explícitamente, se niega.

### IDOR - el fallo más probable
Toda consulta por identificador debe filtrar **también** por el ámbito autorizado:

```
# MAL
paciente = db.get(Patient, patient_id)

# BIEN
paciente = repo.get_for_actor(patient_id, actor=current_user)  # filtra por ámbito
```

Prueba obligatoria: el usuario A pide por ID un recurso de B y recibe 403/404, nunca el dato.

## 2. Identidad, MFA y sesiones

- **MFA obligatorio desde F5** para administradores y médicos. **TOTP o FIDO2/passkey.**
  **SMS no es método principal.**
- **Cuentas personales.** Prohibidas las cuentas compartidas por puesto o por turno.
- **PC compartida** (recepción, consultorio):
  - Bloqueo rápido visible y atajo de teclado.
  - Cierre de sesión por inactividad corto y configurable.
  - **Reautenticación** para acciones sensibles: firmar, exportar, break-glass, cambiar permisos,
    fusionar pacientes.
  - Nada de "recordar usuario" ni de sesiones persistentes en el navegador.
- **Restricción de acceso desde el exterior**: el acceso fuera de la red de la IPRESS se
  limita (lista de red, VPN o segundo factor reforzado) según el ADR-001; por defecto, denegado.

## 3. Break-glass

Acceso de emergencia a información a la que el usuario normalmente no accede.

Requisitos, todos obligatorios:
1. **Motivo escrito** del usuario (texto libre, no una lista de opciones).
2. **Tiempo limitado** (minutos, no horas), aplicado por el backend.
3. **Alerta inmediata** a Dirección Médica y al responsable de seguridad.
4. **Evento registrado** en `break_glass_events` y en `audit_events`.
5. **Revisión posterior** obligatoria, con constancia de quién revisó y cuándo.

Un break-glass sin alguno de los cinco es un hallazgo **P0**.

## 4. Cuentas de profesionales visitantes

- **Temporales con fecha de vencimiento** aplicada en el backend.
- MFA obligatorio antes de activar.
- Mínimo privilegio: solo los pacientes de su campaña y solo durante su vigencia.
- Al cerrar la campaña, las cuentas se suspenden automáticamente.
- Registro profesional verificado y anotado antes de activar.

## 5. Auditoría

- Se registra: **acceso** a información clínica, **cambio** sensible, autenticación,
  elevación de privilegio, break-glass, exportación, merge de pacientes, cambio de permisos.
- Campos: actor, acción, tipo y **ID técnico** del recurso, momento UTC, correlación, resultado,
  origen (IP/estación).
- **Integridad verificable**: append-only o hash encadenado (lo decide el ADR-006). El esquema
  debe permitir ambas. Nadie, ni el administrador de base de datos, borra sin dejar rastro.
- La auditoría se conserva según la política de retención y se respalda con el resto.

## 6. Privacidad

- **Sin PHI en logs**, URL, mensajes de error, trazas, analítica ni telemetría. Solo IDs
  técnicos y `correlation_id`. Esto se **prueba** con una aserción sobre la salida de log.
- **Minimización por rol** en la respuesta del backend, no filtrando en el cliente.
- **Exportaciones**: limitadas por rol, auditadas, con motivo y marca de agua o registro del
  destinatario.
- **Base jurídica y consentimiento** registrados, con la versión del aviso de privacidad.
- **Derechos ARCO**: flujo y plazos registrados en `data_subject_requests`.
- **Solo datos sintéticos** en DEV, CI, STAGING y en cualquier IA (`docs/TEST_DATA_POLICY.md`).
- Cifrado **en tránsito** (TLS) y **en reposo** (base y respaldos).

## 7. Procedimiento de incidente (Plan v1.2 §22)

1. **Detectar** y registrar la hora.
2. **Contener**: cortar el acceso, revocar credenciales, aislar.
3. **Evaluar** alcance: qué datos, de cuántas personas, qué sensibilidad.
4. **Notificar** internamente: Dirección Médica, responsable de privacidad, responsable técnico.
5. **Notificar** a la autoridad y a los afectados si corresponde.
   **Plazo de 48 h: POR VALIDAR con asesor legal** (DS 016-2024-JUS art. 34).
6. **Erradicar y recuperar**: corregir la causa, restaurar desde respaldo verificado.
7. **Lecciones aprendidas**: informe, test de regresión y actualización de controles.

Detalle operativo en `docs/INCIDENT_RESPONSE.md`.

## 8. Gates de seguridad S1-S13

Verificación que debe superarse antes de cerrar una fase:

| Gate | Control |
|---|---|
| S1 | Autorización en backend en todos los endpoints nuevos |
| S2 | Pruebas negativas por rol, completas |
| S3 | Pruebas de IDOR, completas |
| S4 | MFA exigido a los roles que corresponde |
| S5 | Sesión: inactividad, bloqueo y reautenticación sensible |
| S6 | Break-glass con los cinco requisitos |
| S7 | Cuentas visitantes con vencimiento aplicado en backend |
| S8 | Auditoría completa y con integridad verificable |
| S9 | Sin PHI en logs, probado |
| S10 | Sin secretos en código ni en el historial |
| S11 | Dependencias escaneadas, sin vulnerabilidad crítica abierta |
| S12 | TLS, cabeceras, CORS y límites de tasa configurados |
| S13 | Respaldo y **restore probado** dentro del RTO |

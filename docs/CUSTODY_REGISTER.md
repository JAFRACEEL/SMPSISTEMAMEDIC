# Registro de custodia de accesos institucionales - SISTEMAMEDIC

Estado: **PLANTILLA VACÍA - completa Responsable técnico + Dirección Médica**

## Regla de custodia (innegociable)

1. Todo recurso crítico tiene **un propietario institucional** (el Centro Médico / la Parroquia San Martín de Porres), no una persona.
2. Todo recurso crítico tiene **mínimo dos administradores** (Admin 1 y Admin 2) con acceso efectivo probado.
3. Nada queda registrado a nombre personal de una sola persona (ni cuentas, ni dominio, ni certificados, ni facturación).
4. Todo recurso con MFA documenta su **método de recuperación** (códigos de respaldo, segundo factor físico) y dónde se custodian.
5. Revisión del registro al menos **trimestral** y ante cualquier baja o cambio de personal.

## Registro

| Recurso | Propietario institucional | Admin 1 | Admin 2 | Recuperación MFA | Fecha |
|---|---|---|---|---|---|
| Repositorio de código (Git) | | | | | |
| Plataforma de CI/CD | | | | | |
| Dominio de internet | | | | | |
| DNS | | | | | |
| Cuenta de proveedor cloud / hosting | | | | | |
| Servidor on-premise (acceso físico y administrativo) | | | | | |
| Base de datos PROD (credenciales administrativas) | | | | | |
| Gestor de secretos (vault) | | | | | |
| Almacenamiento de backups | | | | | |
| Certificados TLS | | | | | |
| Certificado de firma digital (RM 462-2023) | | | | | |
| Cuenta de correo institucional / notificaciones | | | | | |
| Cuenta SUNAT / CPE (si aplica según RUC) | | | | | |
| Registro de llaves MFA físicas (FIDO2) | | | | | |
| Cuenta del proveedor de internet | | | | | |

## Procedimiento de alta y baja

- **Alta**: registrar aquí antes de entregar el acceso; probar el acceso del Admin 2 el mismo día.
- **Baja**: revocar en menos de 24 h, rotar credenciales compartidas y anotar la fecha en este registro.
- **Verificación de recuperación**: probar la recuperación MFA al menos una vez al año y dejar constancia.

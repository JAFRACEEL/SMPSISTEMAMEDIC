# ADR-009: Entornos staging y PROD (aprovisionamiento, TLS, dominio, vault)

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE (Dirección Médica + responsable técnico)
- **Fecha límite para decidir**: PENDIENTE - staging antes de F4b; PROD antes de F11A
- **Fase que bloquea**: F4b, F8A, F9A, F11A, F12A
- **Fecha del borrador**: 2026-10-01

> **Hallazgo A1 del Plan v1.2**: el plan **no aprovisiona staging ni PROD**, pero F8A y F9A
> exigen staging (UAT y pentest) y F11A/F12A exigen PROD con TLS, dominio, vault y monitoreo.
> Este ADR cubre el hueco; la fase **F4b** se añade para construir staging.

## 1. Entornos previstos

| Entorno | Para qué | Datos | ¿Claude Code? | Cuándo existe |
|---|---|---|---|---|
| **DEV** (local) | Desarrollo | **Solo sintéticos** | Sí | Ya (F4) |
| **CI** | Pipeline automático | **Solo sintéticos** | Sí (lee resultados) | F4 |
| **STAGING** | UAT, pentest, ensayo de migración | **Solo sintéticos** | Sí, sobre código; **sin credenciales** | **F4b** |
| **PROD** | Operación real | Datos reales | **No. Nunca.** | Antes de F11A |

**Regla firme**: Claude Code no tiene credenciales de staging ni de PROD, y no las pide.
El despliegue lo ejecuta CI/CD con **aprobación humana** registrada en `docs/APPROVALS.md`.

## 2. STAGING - requisitos mínimos

| # | Requisito | Estado |
|---|---|---|
| 1 | Infraestructura equivalente a PROD en forma, menor en tamaño | PENDIENTE |
| 2 | **Solo datos sintéticos**, generados por script | Firme |
| 3 | TLS válido (no autofirmado si el pentester debe probar la cadena) | PENDIENTE |
| 4 | Dominio o subdominio propio | PENDIENTE |
| 5 | Acceso restringido (red o autenticación adicional) | PENDIENTE |
| 6 | Se puede borrar y recrear desde IaC | PENDIENTE |
| 7 | Respaldo y restore probados aquí antes que en PROD | PENDIENTE |
| 8 | Monitoreo básico | PENDIENTE |

Lo construye `devops-release-engineer` como **IaC o guía en borrador**; **lo aprovisiona una
persona** (gate H4).

## 3. PROD - requisitos mínimos

| # | Requisito | Estado |
|---|---|---|
| 1 | Infraestructura según ADR-001 | PENDIENTE |
| 2 | **TLS** con certificado válido y renovación automática | PENDIENTE |
| 3 | **Dominio institucional**, registrado a nombre de la institución | PENDIENTE |
| 4 | **Vault / gestor de secretos**: ningún secreto en archivos ni en el repositorio | PENDIENTE |
| 5 | Cifrado en reposo (base y adjuntos) | PENDIENTE |
| 6 | **Respaldo automatizado y restore probado** dentro del RTO | PENDIENTE |
| 7 | Monitoreo y alertas, con alguien que las recibe (y suplente) | PENDIENTE |
| 8 | Logs **sin PHI**, con retención definida | PENDIENTE |
| 9 | Cabeceras de seguridad, CORS y límites de tasa | PENDIENTE |
| 10 | Acceso administrativo con **MFA** y **dos administradores** | PENDIENTE |
| 11 | Despliegue solo por CI/CD con aprobación humana | Firme |
| 12 | Procedimiento de **rollback** probado | PENDIENTE |
| 13 | Separación física o lógica de staging | PENDIENTE |
| 14 | Registrado en `docs/CUSTODY_REGISTER.md` antes de usarse | Firme |

## 4. Gestión de secretos

| Decisión | Propuesta | Estado |
|---|---|---|
| Dónde viven los secretos | Gestor de secretos del proveedor o solución autogestionada | PENDIENTE |
| Quién puede leerlos | Dos administradores nombrados, con MFA | PENDIENTE |
| Rotación | PENDIENTE - propuesta: anual y ante cualquier sospecha | PENDIENTE |
| Qué hay en el repositorio | **Solo nombres** (`.env.example`). Nunca valores | Firme |
| Qué hace CI | Lee del vault; **nunca imprime** un secreto en el log | Firme |

## 5. Secuencia propuesta

1. **F4**: DEV y CI funcionando; IaC de staging escrita (sin aplicar).
2. **F4b**: una persona aprovisiona **STAGING**; se prueba restore allí. → Gate **H4**.
3. **F8A**: UAT y performance en staging con datos sintéticos.
4. **F9A**: pentest externo contra staging; remediación y reverificación.
5. **Antes de F11A**: una persona aprovisiona **PROD** con los 14 requisitos; se registra en
   `CUSTODY_REGISTER.md`; se prueba el rollback.
6. **F11A**: operación en paralelo. **F12A**: go-live. Ambas **humanas**.

## 6. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | Proveedor y dimensionamiento de staging | Resp. técnico + Administración | Antes de F4b |
| 2 | Dominio institucional y quién lo registra | Administración | Antes de F4b |
| 3 | Qué gestor de secretos | Resp. técnico + revisor indep. | Antes de F4b |
| 4 | Quiénes son los **dos** administradores de PROD | Dirección Médica | Antes de F11A |
| 5 | Quién recibe las alertas de monitoreo (y su suplente) | Dirección Médica | Antes de F11A |
| 6 | Presupuesto recurrente de ambos entornos | Administración | Antes de F4b |

## 7. Cómo se revierte

Staging es desechable por definición: se recrea. PROD no: una vez que hay datos reales,
cambiar de proveedor o de dominio es una migración con ventana, riesgo y aprobación.
**Las decisiones de PROD deben estar tomadas antes de F11A, no durante.**

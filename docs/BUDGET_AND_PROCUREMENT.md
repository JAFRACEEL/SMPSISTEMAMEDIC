# Presupuesto y compras - SISTEMAMEDIC

> **BORRADOR - requiere aprobación.** Gate H1.
> Los costos están **vacíos a propósito**: no se inventan cifras. Los completa Administración
> con cotizaciones reales.

## 1. RUTA CRÍTICA (lo que bloquea fases si llega tarde)

Ordenado por urgencia. Si uno de estos se retrasa, la fase indicada **no empieza**.

| # | Rubro | Debe estar listo ANTES de | Plazo típico de contratación | Fecha límite | Estado |
|---|---|---|---|---|---|
| 1 | **Asesoría legal / privacidad** | F3 (ADR) | PENDIENTE | PENDIENTE | NO INICIADO |
| 2 | **Revisor técnico independiente** | F3 (ADR) | PENDIENTE | PENDIENTE | NO INICIADO |
| 3 | **Hosting / servidor** | F4 | PENDIENTE | PENDIENTE | NO INICIADO |
| 4 | **UPS, energía y red** | F4 | PENDIENTE | PENDIENTE | NO INICIADO |
| 5 | **PC e impresoras** | F4 | PENDIENTE | PENDIENTE | NO INICIADO |
| 6 | **MFA físico (llaves FIDO2)** | F5 | PENDIENTE | PENDIENTE | NO INICIADO |
| 7 | **Certificado de firma digital** | F7 | PENDIENTE (puede ser largo) | PENDIENTE | NO INICIADO |
| 8 | **Pentest externo** | F9A | PENDIENTE (agenda escasa) | PENDIENTE | NO INICIADO |

**Hitos de contratación** (hallazgo M6 de `PLAN_REVIEW_v1.2.md`): los rubros 1 y 2 se contratan
**antes de F3**; los rubros 6 y 7, **antes de F5 y F7** respectivamente; el rubro 8,
**antes de F9A**. Cada uno necesita fecha límite real, no "cuando se pueda".

## 2. Rubros completos (Plan v1.2 §5.1)

| Rubro | Decisión | Responsable | Plazo de entrega | Fecha límite | Costo estimado |
|---|---|---|---|---|---|
| Asesoría legal y de protección de datos | PENDIENTE | Dirección Médica | PENDIENTE | PENDIENTE | |
| Revisor técnico independiente | PENDIENTE | Dirección Médica | PENDIENTE | PENDIENTE | |
| Pentest externo | PENDIENTE | Resp. técnico | PENDIENTE | PENDIENTE | |
| Hosting / servidor (nube u on-premise) | PENDIENTE (ADR-001) | Resp. técnico | PENDIENTE | PENDIENTE | |
| Dominio de internet | PENDIENTE | Administración | PENDIENTE | PENDIENTE | |
| Certificado TLS | PENDIENTE | Resp. técnico | PENDIENTE | PENDIENTE | |
| UPS / respaldo de energía | PENDIENTE | Administración | PENDIENTE | PENDIENTE | |
| Conectividad / enlace de internet y respaldo | PENDIENTE | Administración | PENDIENTE | PENDIENTE | |
| Red interna (cableado, switch, Wi-Fi) | PENDIENTE | Administración | PENDIENTE | PENDIENTE | |
| PC de recepción, triaje y consultorios | PENDIENTE | Administración | PENDIENTE | PENDIENTE | |
| Impresoras (recetas, comprobantes, etiquetas) | PENDIENTE | Administración | PENDIENTE | PENDIENTE | |
| Escáner (digitalización de historias) | PENDIENTE | Administración | PENDIENTE | PENDIENTE | |
| Almacenamiento de respaldos (fuera de sitio) | PENDIENTE | Resp. técnico | PENDIENTE | PENDIENTE | |
| Certificado de firma digital (RM 462-2023) | PENDIENTE | Dirección Médica | PENDIENTE | PENDIENTE | |
| Llaves MFA físicas FIDO2 | PENDIENTE | Resp. técnico | PENDIENTE | PENDIENTE | |
| Gestor de secretos (vault) | PENDIENTE (ADR-009) | Resp. técnico | PENDIENTE | PENDIENTE | |
| Plataforma de CI/CD | PENDIENTE | Resp. técnico | PENDIENTE | PENDIENTE | |
| Capacitación del personal | PENDIENTE | Product Owner | PENDIENTE | PENDIENTE | |
| Digitalización de historias en papel | PENDIENTE | Administración | PENDIENTE | PENDIENTE | |
| Contingencia (recomendado 20-30 %) | PENDIENTE | Dirección Médica | - | - | |

## 3. Decisiones que condicionan el gasto

1. **Hosting**: nube vs. servidor en el Centro Médico. Decide el **ADR-001** junto con RPO/RTO
   y el modo degradado. En Iquitos, un servidor local sin UPS y sin enlace redundante **no**
   cumple continuidad; la nube sin enlace estable tampoco. Puede requerir una solución mixta.
2. **RUC y régimen tributario** del Centro Médico: determina si aplica SUNAT/CPE y qué
   software de facturación hace falta. **La fecha 01/06/2026 no es una regla del sector salud**;
   hay que verificar la obligación concreta según el RUC (ver `NORMATIVE_MATRIX.md`, R16-R17).
3. **Firma digital**: el certificado tiene un plazo de emisión que suele subestimarse y es
   prerrequisito de F7.
4. **Dos maintainers**: cualquier contrato y cualquier cuenta debe quedar a nombre
   institucional con dos administradores (`CUSTODY_REGISTER.md`).

## 4. Reglas de compra

- Nada se contrata a nombre personal.
- Toda cuenta de proveedor queda registrada en `docs/CUSTODY_REGISTER.md` antes de usarse.
- Los servicios con datos de salud requieren **contrato de encargado de tratamiento**
  (Ley 29733, DS 016-2024-JUS) revisado por el asesor legal.
- Si hay transferencia internacional de datos (nube fuera de Perú), se documenta la base
  jurídica en `docs/PRIVACY_AND_COMPLIANCE.md` antes de contratar.

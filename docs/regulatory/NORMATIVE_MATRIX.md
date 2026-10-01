# Matriz normativa - SISTEMAMEDIC

> **BORRADOR - requiere aprobación.** Gate H3.
> **Todas las entradas están POR VERIFICAR.** Ninguna pasa a `Verificada` sin que una persona
> la lea en la fuente primaria y firme con **nombre, rol y fecha**.
> Hallazgo A7 del Plan v1.2: "Verificado por: Revisión documental del proyecto" **no identifica
> a nadie** y no es válido.

## Cómo se usa

| Columna | Regla |
|---|---|
| **Aplica** | `Sí` / `No` / `Por validar`. Si es `Por validar`, no se construye sobre ella |
| **Estado** | `POR VERIFICAR` → `Verificada` solo con verificador y fecha |
| **URL oficial** | Fuente primaria (El Peruano, MINSA, SUNAT, ANPD). No blogs ni resúmenes |
| **Verificado por** | Nombre y rol de la persona. Nunca "el equipo" ni "la IA" |
| **Fecha** | `AAAA-MM-DD` de la verificación |

Las URL de la columna son **candidatas de partida** y deben confirmarse al verificar.

## Matriz R1-R17 (Plan v1.2 §3)

| Ref | Norma | Objeto | Aplica | Estado | URL oficial (candidata) | Verificado por | Fecha |
|---|---|---|---|---|---|---|---|
| R1 | Ley 29733 - Ley de Protección de Datos Personales | Tratamiento de datos de salud como dato sensible | Sí | POR VERIFICAR | https://www.gob.pe/institucion/minjus/normas-legales | | |
| R2 | DS 016-2024-JUS - Reglamento de la Ley 29733 | Medidas de seguridad, EIPD, encargados, incidentes | Sí | POR VERIFICAR | https://busquedas.elperuano.pe/ | | |
| R3 | DS 016-2024-JUS art. 34 - Notificación de incidentes | Plazo (¿48 h?) y destinatarios | **Por validar** | POR VERIFICAR | https://busquedas.elperuano.pe/ | | |
| R4 | NTS 139-MINSA/2018 (RM 214-2018/MINSA) | Gestión de la historia clínica | Sí | POR VERIFICAR | https://www.gob.pe/institucion/minsa/normas-legales | | |
| R5 | NTS 139 - retención, archivo y destrucción de HCE | Plazos de conservación | Sí | POR VERIFICAR | https://www.gob.pe/institucion/minsa/normas-legales | | |
| R6 | RM 462-2023/MINSA | Firma digital en documentos clínicos | Sí | POR VERIFICAR | https://www.gob.pe/institucion/minsa/normas-legales | | |
| R7 | Ley 27269 y reglamento - Firma digital y certificados | Validez legal de la firma | Por validar | POR VERIFICAR | https://www.gob.pe/indecopi | | |
| R8 | RM 164-2025/MINSA - SIHCE | Sistema de información de HCE | Por validar | POR VERIFICAR | https://www.gob.pe/institucion/minsa/normas-legales | | |
| R9 | RM 188-2026/MINSA - SIHCE | Actualización | Por validar | POR VERIFICAR | https://www.gob.pe/institucion/minsa/normas-legales | | |
| R10 | RM 673-2025/MINSA - SIHCE | Actualización | Por validar | POR VERIFICAR | https://www.gob.pe/institucion/minsa/normas-legales | | |
| R11 | Guía de implementación FHIR Perú v0.1 | Perfiles de interoperabilidad | Por validar | POR VERIFICAR | PENDIENTE - localizar fuente oficial | | |
| R12 | Ley 26842 - Ley General de Salud | Derechos del paciente, consentimiento informado | Sí | POR VERIFICAR | https://www.gob.pe/institucion/minsa/normas-legales | | |
| R13 | Normativa RENIEC de identificación | Identidad, menores, personas sin documento | Por validar | POR VERIFICAR | https://www.gob.pe/reniec | | |
| R14 | Normativa SUSALUD / RENIPRESS | Registro y categorización de la IPRESS | Por validar | POR VERIFICAR | https://www.gob.pe/susalud | | |
| R15 | CIE-10, versión adoptada por MINSA | Codificación de diagnósticos | Sí | POR VERIFICAR | https://www.gob.pe/institucion/minsa | | |
| R16 | Normativa SUNAT de comprobantes de pago electrónicos | Facturación según RUC y régimen | Por validar | POR VERIFICAR | https://www.sunat.gob.pe/legislacion/ | | |
| R17 | R.S. SUNAT 000075-2026 | Obligación y fecha de CPE | Por validar | POR VERIFICAR | https://www.sunat.gob.pe/legislacion/ | | |

## Advertencias en firme

1. **La regla de 48 h (R3) no se afirma como firme en ningún documento.** Se escribe
   "POR VALIDAR con asesor" en `INCIDENT_RESPONSE.md`, en `healthcare-security` y aquí.
   (Hallazgo A8 del Plan v1.2.)
2. **La fecha 01/06/2026 de SUNAT no es una regla del sector salud.** Antes de derivar
   cualquier obligación hay que determinar el **RUC y el régimen tributario** del Centro
   Médico (Administración).
3. **Se usa el término EIPD**, no "DPIA".
4. **R2, R3, R6-R11 y R13-R17 deben reverificarse antes de F3** con fuente primaria
   (hallazgo A7).
5. **No verificado por el revisor IA** (hallazgo F2 del Plan): RM 462-2023, RM 164-2025,
   RM 188-2026, RM 673-2025, guía FHIR Perú v0.1 y R.S. SUNAT 000075-2026. Requieren
   confirmación humana en fuente primaria, incluida su **vigencia** a la fecha de verificación.

## Consecuencia por fase

| Fase | Normas que deben estar `Verificada` antes de empezar |
|---|---|
| F3 (ADR) | R1, R2, R3, R4, R5, R12 |
| F5 (auth/MFA) | R1, R2 |
| F7 (HCE y firma) | R4, R5, R6, R7, R15 |
| Oleada de caja/facturación | R16, R17 + RUC y régimen definidos |
| Interoperabilidad | R8, R9, R10, R11, R14 |

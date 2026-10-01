---
name: ipress-peru
description: Contexto IPRESS y HCE en Perú y matriz normativa de SISTEMAMEDIC (Ley 29733, DS 016-2024-JUS, NTS 139, RM 462-2023, SIHCE, SUNAT). Úsala al diseñar cualquier función que toque historia clínica, datos personales, firma, facturación o reporte al MINSA.
---

# IPRESS Perú - contexto y matriz normativa

## 1. Qué es esta IPRESS

Centro Médico de la Parroquia San Martín de Porres, Iquitos (Loreto). Institución Prestadora
de Servicios de Salud de baja complejidad, con consulta externa, triaje, laboratorio básico,
farmacia y **campañas de salud** con profesionales visitantes nacionales e internacionales.

Condiciones que cambian el diseño respecto de una clínica urbana:

- Cortes de energía frecuentes y conectividad irregular → modo degradado obligatorio.
- Población con **documentación incompleta**: sin DNI, menores sin inscripción, extranjeros
  con CE o pasaporte, personas de comunidades ribereñas.
- Comunidad pequeña → **la reidentificación de datos "anonimizados" es probable**.
- Personal escaso y polivalente → el mínimo privilegio debe convivir con la realidad operativa.

## 2. Reglas duras de esta skill

1. **Ninguna afirmación normativa sin fuente oficial, verificador (nombre y rol) y fecha.**
   Mientras falte, se escribe `POR VERIFICAR`. No se cita de memoria ni se parafrasea un
   artículo sin haberlo leído en la fuente.
2. El término correcto en el marco peruano es **EIPD** (evaluación de impacto en la
   protección de datos personales). **No** se usa "DPIA".
3. La regla de **48 h** para notificar incidentes (DS 016-2024-JUS, art. 34) y **a quién** se
   notifica están **POR VALIDAR con asesor legal**. No se afirma como firme en ningún documento.
4. La fecha **01/06/2026** asociada a SUNAT **no es una regla del sector salud**. Antes de
   derivar cualquier obligación hay que determinar el **RUC y el régimen** del Centro Médico.
5. Una norma pasa a `Verificada` solo cuando una persona la revisó en la fuente primaria y
   firmó con nombre, rol y fecha en `docs/regulatory/NORMATIVE_MATRIX.md`.

## 3. Matriz normativa precargada (R1-R17, Plan v1.2 §3)

Todas nacen **POR VERIFICAR**. `docs/regulatory/NORMATIVE_MATRIX.md` es la versión viva;
esta tabla es el punto de partida.

| Ref | Norma | Objeto | Aplica | Estado |
|---|---|---|---|---|
| R1 | Ley 29733 - Protección de Datos Personales | Tratamiento de datos de salud (dato sensible) | Sí | POR VERIFICAR |
| R2 | DS 016-2024-JUS - Reglamento de la Ley 29733 | Medidas, EIPD, incidentes, encargados | Sí | POR VERIFICAR |
| R3 | DS 016-2024-JUS art. 34 - Notificación de incidentes | Plazo y destinatarios | Por validar | POR VERIFICAR |
| R4 | NTS 139-MINSA/2018 (RM 214-2018/MINSA) | Gestión de la historia clínica | Sí | POR VERIFICAR |
| R5 | NTS 139 - retención y archivo de HCE | Plazos de conservación y destrucción | Sí | POR VERIFICAR |
| R6 | RM 462-2023/MINSA | Firma digital en documentos clínicos | Sí | POR VERIFICAR |
| R7 | Ley 27269 y su reglamento - Firma digital | Validez legal de la firma | Por validar | POR VERIFICAR |
| R8 | RM 164-2025/MINSA - SIHCE | Interoperabilidad de HCE | Por validar | POR VERIFICAR |
| R9 | RM 188-2026/MINSA - SIHCE | Actualización SIHCE | Por validar | POR VERIFICAR |
| R10 | RM 673-2025/MINSA - SIHCE | Actualización SIHCE | Por validar | POR VERIFICAR |
| R11 | Guía de implementación FHIR Perú v0.1 | Perfiles de interoperabilidad | Por validar | POR VERIFICAR |
| R12 | Ley 26842 - Ley General de Salud | Derechos del paciente, consentimiento | Sí | POR VERIFICAR |
| R13 | Normativa de RENIEC / identificación | Validación de identidad y menores | Por validar | POR VERIFICAR |
| R14 | Normativa SUSALUD de registro de IPRESS (RENIPRESS) | Registro y categorización | Por validar | POR VERIFICAR |
| R15 | CIE-10 (versión vigente adoptada por MINSA) | Codificación de diagnósticos | Sí | POR VERIFICAR |
| R16 | Normativa SUNAT de comprobantes de pago electrónicos | Facturación según RUC y régimen | Por validar | POR VERIFICAR |
| R17 | R.S. SUNAT 000075-2026 | Obligación y fecha de CPE | Por validar | POR VERIFICAR |

**URL oficial, verificador y fecha**: columnas obligatorias en
`docs/regulatory/NORMATIVE_MATRIX.md`. Esta skill no las duplica para evitar copias
desactualizadas.

## 4. Consecuencias de diseño que ya son firmes

Independientes de la verificación normativa pendiente, porque derivan de principios básicos:

- **Historia clínica longitudinal única** por persona. La campaña no crea una historia aparte.
- **Identidad sin DNI obligatorio**: identificador interno siempre, documentos 0..n.
- **Lo firmado no se altera**: addendum y versión, con autor, fecha y motivo.
- **Consentimiento y deber de informar** registrados y fechados, con su versión de aviso de
  privacidad (`privacy_notices`).
- **Derechos ARCO**: existe un flujo y un registro (`data_subject_requests`).
- **Dato de salud = dato sensible**: minimización por rol, auditoría de acceso, cifrado en
  tránsito y en reposo.
- **Menores**: representante registrado y vínculo verificable.
- **Campañas internacionales**: cuenta temporal con vencimiento; transferencia internacional
  de datos solo con base jurídica documentada.

## 5. Antes de cerrar cualquier documento normativo

Comprueba las cuatro cosas:

1. ¿Cada afirmación tiene fuente oficial con URL?
2. ¿Cada fuente tiene verificador (nombre y rol) y fecha `AAAA-MM-DD`?
3. ¿Lo no verificado dice `POR VERIFICAR` de forma visible?
4. ¿Se usó "EIPD" y no "DPIA"?

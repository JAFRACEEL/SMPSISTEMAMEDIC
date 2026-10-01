# Operación de campañas - SISTEMAMEDIC

> **BORRADOR - PLANTILLA DE DISCOVERY (F2). No contiene hallazgos.** Gate H2.
> Las campañas (incluidas las internacionales) son un caso central, no una excepción.

## Guion de entrevista

1. ¿Cuántas campañas hacen al año? ¿De qué tipo?
2. ¿Quién las organiza? ¿Hay una institución externa?
3. ¿Cuántos pacientes atienden en una campaña típica? ¿En cuántos días?
4. ¿Quiénes participan? ¿Vienen profesionales de fuera? ¿De otros países?
5. ¿Cómo se registra hoy a los pacientes de campaña? ¿Entran al mismo archivo?
6. ¿Qué pasa si un paciente de campaña vuelve meses después a consulta normal?
7. ¿Los visitantes necesitan ver historias previas? ¿Las ven hoy?
8. ¿Qué información se entrega al organizador al terminar?
9. ¿Qué pasa con las fotografías y los testimonios?
10. ¿Qué idioma hablan los visitantes? ¿Necesitan la interfaz en otro idioma?
11. ¿Cómo se acredita a un profesional visitante? ¿Se verifica su registro profesional?
12. ¿Qué pasa cuando la campaña termina? ¿Alguien revoca accesos?
13. ¿Hay atención en comunidades fuera del local? ¿Con qué conectividad?

## Tablas a completar

### T1. Campañas históricas

| # | Año | Tipo de campaña | Organizador | Días | Pacientes atendidos | Profesionales visitantes | ¿De qué países? | Cómo se registró |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

### T2. Profesionales visitantes

| Elemento | Respuesta |
|---|---|
| ¿Cómo se acredita su título y registro profesional? | |
| ¿Quién lo verifica y lo documenta? | |
| ¿Cuánto tiempo permanecen? | |
| ¿Necesitan ver historias anteriores del paciente? | |
| ¿Necesitan firmar documentos clínicos? | |
| ¿Quién los supervisa? | |
| ¿Quién revoca su acceso al terminar? | |
| ¿Hablan español? ¿Qué otros idiomas? | |

### T3. Flujo de atención en campaña

| # | Paso | Quién lo hace | Dónde | Soporte actual | Diferencia con la consulta normal |
|---|---|---|---|---|---|
| | | | | | |

### T4. Atención fuera del local (comunidades)

| Elemento | Respuesta |
|---|---|
| ¿Ocurre? ¿Con qué frecuencia? | |
| ¿Hay energía eléctrica? | |
| ¿Hay conectividad? | |
| ¿Cómo se registra hoy? | |
| ¿Cómo se incorpora después al archivo central? | |

### T5. Datos que salen hacia el organizador

| # | Qué se entrega | A quién | Formato | ¿Incluye datos personales? | Base jurídica | ¿Hay contrato? |
|---|---|---|---|---|---|---|
| | | | | | | |

## Reglas que ya son firmes

- **Una sola HCE.** La atención de campaña es un `Encounter` con `campaign_id` opcional.
  **Nunca** una base de datos ni una historia paralela. Si el paciente vuelve meses después,
  su atención de campaña está ahí, en la misma historia.
- **Cuentas de visitantes temporales**: vencimiento aplicado en el backend, MFA obligatorio,
  mínimo privilegio, acceso limitado a los pacientes de su campaña.
- Al cerrar la campaña (`completed`), las cuentas asociadas se **suspenden automáticamente**.
- **Consentimiento y aviso de privacidad** iguales que para cualquier paciente, más
  consentimiento específico para el uso de imágenes.
- Cualquier dato que salga hacia el organizador: **agregado y anonimizado por una persona**,
  nunca por una IA, con base jurídica documentada. Si hay transferencia internacional, se
  documenta en `PRIVACY_AND_COMPLIANCE.md` §8.
- **Idioma e i18n**: lo decide el **ADR-007**. No se asume que todos leen español.
- **Modo degradado**: la atención en comunidad sin conectividad necesita un procedimiento
  explícito y una vía de incorporación posterior sin duplicar pacientes.

## Riesgos específicos de campaña

| # | Riesgo | Por qué | Mitigación propuesta |
|---|---|---|---|
| 1 | Duplicación masiva de pacientes | Registro rápido, mucha gente, poco tiempo | Búsqueda obligatoria antes de crear; cola de identidad incierta |
| 2 | Accesos que quedan abiertos | Nadie revoca al terminar | Vencimiento automático, no manual |
| 3 | Fuga por exportación al organizador | Presión por entregar resultados | Solo agregados, aprobados por Dirección Médica |
| 4 | Fotografías sin consentimiento | Uso para difusión | Consentimiento específico y separado |
| 5 | Registro en papel que nunca se incorpora | Falta de conectividad | Procedimiento de incorporación con plazo y responsable |

## Huecos detectados

| # | Qué falta saber | Por qué importa | A quién preguntar | Bloquea a |
|---|---|---|---|---|
| | | | | |

# ADR-001: Hosting, RPO/RTO y modo degradado

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE
- **Fecha de aprobación**: PENDIENTE
- **Fecha límite para decidir**: PENDIENTE - antes de F4
- **Fase que bloquea**: F4, F4b y toda la continuidad operativa
- **Fecha del borrador**: 2026-10-01

## 1. Contexto

El Centro Médico opera en **Iquitos**: cortes de energía frecuentes y conectividad irregular.
La decisión de dónde vive el sistema determina qué pasa cuando falla la luz o el internet a
media consulta, y condiciona compras con plazo largo (UPS, enlace, servidor).

**No se puede decidir sin `docs/INFRASTRUCTURE_SURVEY.md` completo** (frecuencia y duración
de cortes, estabilidad del enlace, equipos existentes, soporte disponible).

Además, el Plan v1.2 **no aprovisiona staging ni PROD** (hallazgo A1), pero F8A/F9A exigen
staging y F11A/F12A exigen PROD. Ver ADR-009.

## 2. Criterios de decisión

| # | Criterio | Peso | Por qué |
|---|---|---|---|
| 1 | Continuidad ante corte de energía | Alto | La atención no puede detenerse |
| 2 | Continuidad ante caída de internet | Alto | El enlace es el punto más débil |
| 3 | Costo total a 3 años | Alto | Presupuesto limitado |
| 4 | Dependencia de una sola persona | Alto | Riesgo identificado del proyecto |
| 5 | Cumplimiento y transferencia internacional | Alto | Datos de salud; Ley 29733 |
| 6 | Tiempo de recuperación real | Alto | RTO |
| 7 | Facilidad de respaldo y restore probado | Medio | Gate S13 |

## 3. Opciones

### Opción A: Nube (proveedor gestionado)
- **Ventajas**: respaldo y alta disponibilidad gestionados; sin sala técnica; sin inversión
  inicial grande; parches del proveedor.
- **Desventajas**: **si cae el internet, no hay sistema**; costo recurrente en dólares;
  posible **transferencia internacional** de datos de salud; depende del enlace de Iquitos.
- **Riesgos**: inaceptable sin enlace redundante.

### Opción B: Servidor en el Centro Médico (on-premise)
- **Ventajas**: funciona sin internet; datos en el país y en el local; latencia mínima.
- **Desventajas**: exige **UPS dimensionado**, sala adecuada, respaldos fuera de sitio y
  alguien que lo administre; riesgo físico (humedad, robo, inundación); riesgo de depender de
  una sola persona.
- **Riesgos**: sin UPS y sin respaldo fuera de sitio, un corte largo o un incidente físico
  pierde la información.

### Opción C: Mixto - servidor local + réplica y respaldo en la nube **(recomendada)**
- **Ventajas**: la atención continúa sin internet; los respaldos salen del local; permite
  cumplir RTO y RPO exigentes; el riesgo físico deja de ser catastrófico.
- **Desventajas**: más piezas que mantener; costo de ambos; exige runbooks claros.
- **Riesgos**: complejidad operativa si no hay dos administradores.

### Opción D: Nube + modo degradado offline en el cliente
- **Ventajas**: infraestructura simple.
- **Desventajas**: el modo offline de una HCE es **complejo y peligroso** (conflictos de
  sincronización sobre información clínica). No se recomienda para la Oleada A.

## 4. Comparación

| Criterio | A nube | B local | C mixto | D nube+offline |
|---|---|---|---|---|
| Corte de energía | Depende del equipo cliente | UPS obligatorio | UPS obligatorio | Depende |
| Caída de internet | **Falla total** | Sigue funcionando | Sigue funcionando | Parcial |
| Costo inicial | Bajo | Alto | Alto | Bajo |
| Costo recurrente | Alto | Medio | Alto | Alto |
| Riesgo de transferencia internacional | Alto | Nulo | Medio | Alto |
| Complejidad operativa | Baja | Media | Alta | **Muy alta** |
| Riesgo clínico | Medio | Medio | Bajo | **Alto** |

## 5. Recomendación del equipo técnico

**Opción C (mixto)**, condicionada a que el relevamiento confirme que los cortes de energía e
internet son tan frecuentes como se asume. Si el enlace resultara estable y con respaldo, la
opción A simplificaría la operación y reduciría la dependencia de personas.

**No se recomienda la opción D** para la Oleada A: la sincronización offline de información
clínica introduce riesgo clínico desproporcionado.

## 6. RPO y RTO - **los decide Dirección Médica**

| Parámetro | Pregunta a Dirección Médica | Propuesta técnica de partida |
|---|---|---|
| **RPO** (cuánta información se acepta perder) | ¿Es tolerable perder el trabajo de la última hora? | PENDIENTE - propuesta: ≤ 15 min |
| **RTO** (cuánto puede estar caído) | ¿Cuánto puede el Centro Médico atender en papel? | PENDIENTE - propuesta: ≤ 4 h |

Ambos se **miden**: el script de restore reporta el tiempo real y se compara con el RTO
(gate S13). Un RTO que no se ha probado no es un RTO.

## 7. Modo degradado (obligatorio, cualquiera sea la opción)

| Escenario | Qué debe seguir funcionando | Procedimiento |
|---|---|---|
| Corte de energía corto (< autonomía del UPS) | Todo | Cierre ordenado si se agota el UPS |
| Corte largo | Atención en papel | Formatos impresos listos; incorporación posterior sin duplicar pacientes |
| Caída de internet (opción A) | Nada en línea | **Riesgo principal de la opción A** |
| Caída de internet (opciones B/C) | Todo el sistema local | Los respaldos se reintentan al volver |
| Caída del servidor | Nada | Restore según RTO; agenda del día impresa |

Los formatos de contingencia y la incorporación posterior son parte de la Oleada A, no un extra.

## 8. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | RPO aceptable | Dirección Médica | Antes de F4 |
| 2 | RTO aceptable | Dirección Médica | Antes de F4 |
| 3 | Opción A, B o C | Dirección Médica + resp. técnico | Antes de F4 |
| 4 | Presupuesto de UPS, enlace y servidor | Administración | Antes de F4 |
| 5 | Si hay nube: ¿acepta transferencia internacional y con qué base jurídica? | Asesor legal | Antes de F4 |
| 6 | ¿Quién es el segundo administrador? | Dirección Médica | Antes de F4 |

## 9. Cómo se revierte

Pasar de local a nube (o al revés) después de F11A implica migrar datos reales en producción:
caro y riesgoso. **La decisión es reversible barata solo antes de F4.**

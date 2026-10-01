---
name: data-migration
description: Cómo decidir y planificar la migración de datos históricos de SISTEMAMEDIC (migrar, indexar, digitalizar o conservar en papel), deduplicación, conciliación por conteos y hash, y la regla de que un humano ejecuta en entorno aislado. Úsala al planificar o revisar migración de datos reales.
---

# Migración de datos históricos - SISTEMAMEDIC

## 1. Regla no negociable

**Claude Code solo ve esquemas, conteos agregados y datos sintéticos.**
La migración de datos reales la **ejecuta una persona autorizada en un entorno aislado**,
sin Claude Code ni ninguna otra herramienta de IA conectada.

Motivo: en una comunidad pequeña como la atendida por esta IPRESS, la reidentificación a
partir de datos "anonimizados formalmente" es probable (hallazgo A4 del Plan v1.2).

## 2. Decisión por conjunto de datos

Cada conjunto recibe **una** de estas cuatro decisiones, justificada y con responsable:

| Decisión | Cuándo aplica | Qué se entrega |
|---|---|---|
| **Migrar** | Dato estructurado necesario en la operación diaria | Script de carga, conciliación y pruebas |
| **Indexar** | Expediente en papel que debe localizarse rápido | Solo metadatos en el sistema; el papel se conserva y se ubica |
| **Digitalizar** | Documento que debe consultarse en pantalla | Escaneo con checksum, adjunto al paciente, con control de calidad |
| **Conservar en papel** | Valor histórico o legal, uso infrecuente | Archivo físico con su política de retención y su inventario |

No existe la opción "migrar todo por si acaso": cada dato migrado es un riesgo de privacidad
y un coste de calidad.

## 3. Deduplicación

- **Criterios de coincidencia** explícitos y ordenados:
  1. Mismo documento (tipo + valor + país emisor) → coincidencia fuerte.
  2. Nombre normalizado (sin tildes, mayúsculas, orden de apellidos) + fecha de nacimiento →
     coincidencia media, requiere **revisión humana**.
  3. Solo nombre parecido → **no es coincidencia**.
- **Umbral de revisión humana** definido y registrado; nada se fusiona automáticamente por
  coincidencia media o débil.
- Ante duda razonable: **no se fusiona**. Se marca `identity_uncertain = true`.
- Todo merge queda **auditado** (actor, momento, motivo, evidencia) y es **reversible**.

## 4. Conciliación

Una migración solo se acepta si la conciliación da **cero diferencias**:

1. **Conteos** por tabla y por periodo (año, mes) entre origen y destino.
2. **Hash de control** sobre un conjunto de campos clave por registro, agregado por lote.
3. **Muestreo manual**: una persona revisa una muestra aleatoria contra el origen.
4. **Registros rechazados**: lista completa con el motivo; ninguno se descarta en silencio.

Diferencia distinta de cero = **migración rechazada** y revertida al punto de retorno.

## 5. Stock de farmacia

**El stock nunca se migra desde un saldo teórico.** Se carga **después de un inventario
físico** realizado y firmado por el responsable de farmacia, con fecha y hora de corte.
Cualquier otra vía produce un inventario falso desde el primer día.

## 6. Orden de ejecución

1. Catálogos (CIE-10, procedimientos, pagadores).
2. Identidades (pacientes, documentos, representantes).
3. Coberturas.
4. Clínico (encuentros, diagnósticos, problemas, alergias).
5. Adjuntos digitalizados (con checksum).
6. Stock (solo tras inventario físico).

Cada paso tiene **punto de retorno**, respaldo previo verificado y conciliación antes de pasar
al siguiente.

## 7. Protección de datos

La migración es un **tratamiento de datos personales de salud**. Documenta:

- Base jurídica del tratamiento.
- Encargados que intervienen (digitalización, hosting) y su contrato.
- Medidas de seguridad durante el traslado (cifrado, custodia del medio, registro de accesos).
- Qué ocurre con los soportes temporales al terminar (destrucción certificada).
- Retención y archivo de lo que **no** se migra, según NTS 139 (**POR VALIDAR**).

## 8. Entregable para la persona que ejecuta

El plan debe permitir ejecutar sin improvisar:

1. Prerrequisitos (respaldo, ventana, accesos, inventario firmado).
2. Comandos exactos, en orden, con lo que debe verse tras cada uno.
3. Consultas de conciliación con el resultado esperado.
4. Criterio de aborto y procedimiento de reversión.
5. Qué registrar al terminar y dónde (`docs/DATA_MIGRATION_PLAN.md` y `docs/APPROVALS.md`).
6. A quién avisar si algo no coincide.

## 9. Señales de alarma

- Alguien propone pasar un volcado real "solo para probar".
- Un script de migración con datos de ejemplo que parecen reales.
- Conciliación "aproximada" o con diferencias "explicables".
- Fusión automática de pacientes por nombre parecido.
- Carga de stock sin inventario físico firmado.

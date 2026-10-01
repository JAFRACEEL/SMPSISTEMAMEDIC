# ADR-003: HCE - firma, addendum, versionado y retención

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE (requiere Dirección Médica **y** asesor legal)
- **Fecha de aprobación**: PENDIENTE
- **Fecha límite para decidir**: PENDIENTE - antes de F7
- **Fase que bloquea**: F7 (HCE, firma, recetas, cierre)
- **Fecha del borrador**: 2026-10-01

## 1. Contexto

La historia clínica es un documento con valor legal. Una vez firmada y cerrada, **no puede
alterarse**: las correcciones se hacen por addendum, con autor, fecha y motivo. Además hay
una **política de retención, archivo y destrucción** que hoy no existe en el plan y que es
entregable obligatorio de F3 (hallazgo A6 del Plan v1.2).

Marco: NTS 139 (RM 214-2018/MINSA), RM 462-2023/MINSA sobre firma, Ley 26842.
**Todo POR VERIFICAR** (`docs/regulatory/NORMATIVE_MATRIX.md`).

## 2. Criterios

| # | Criterio | Peso |
|---|---|---|
| 1 | Lo firmado es inalterable y demostrable | Alto |
| 2 | Las correcciones son posibles y trazables | Alto |
| 3 | Cumple RM 462-2023 | Alto |
| 4 | El médico puede firmar rápido, sin fricción innecesaria | Medio |
| 5 | Funciona en corte de conectividad | Medio |
| 6 | Costo del certificado y su renovación | Medio |

## 3. Opciones para la firma

### Opción A: Firma electrónica simple (usuario autenticado + sello del sistema)
- **Ventajas**: sin costo de certificado; sin fricción.
- **Desventajas**: **probablemente no cumple RM 462-2023** (POR VERIFICAR). Valor probatorio
  menor.

### Opción B: Firma digital con certificado del profesional **(recomendada, sujeta a verificación)**
- Certificado digital nominal por médico, emitido por entidad acreditada.
- **Ventajas**: valor legal pleno; identifica al profesional.
- **Desventajas**: costo por profesional; plazo de emisión largo (**ruta crítica**, antes de
  F7); gestión de renovaciones; problema con profesionales visitantes extranjeros.

### Opción C: Firma institucional (certificado del Centro Médico) + identificación interna del autor
- **Ventajas**: un solo certificado; cubre a visitantes.
- **Desventajas**: no identifica al profesional con valor legal pleno. PENDIENTE - verificar
  si es admisible.

### Opción D: Híbrida - B para el personal estable, C para visitantes
- Pragmática. **PENDIENTE - verificar admisibilidad legal** antes de proponerla en firme.

## 4. Decisiones que el ADR fija (independientes de la opción de firma)

1. **Inmutabilidad**: `encounters` en estado `signed` **no admite `UPDATE`** de contenido
   clínico. Se aplica en el backend y, si el motor lo permite, también en la base de datos.
2. **Addendum**: `addenda` con autor, fecha UTC, **motivo obligatorio** (texto libre, no
   lista) y referencia al documento original. El addendum también se firma.
3. **Versionado**: `record_versions` conserva íntegra cada versión previa de los registros
   versionables, con su hash.
4. **Documento firmado**: `signed_documents` guarda la **representación tal como se firmó**
   (no se regenera desde la base) y su hash SHA-256.
5. **Firma**: `clinical_signatures` guarda quién, cuándo, con qué certificado, con qué
   algoritmo y sobre qué hash. PENDIENTE - confirmar si se exige **sello de tiempo** (Q5).
6. **Nada se borra**: no existe ruta de borrado físico de información clínica. La baja es
   lógica, con actor y motivo.
7. **Corte durante la firma**: la firma es una operación atómica; si falla, el encuentro
   queda en `ready_to_sign`, nunca en un estado intermedio.

## 5. Retención, archivo y destrucción - **PENDIENTE, bloquea F3**

| Elemento | Valor | Estado |
|---|---|---|
| Plazo de conservación de la HCE activa | PENDIENTE | **POR VALIDAR** (NTS 139, Q4) |
| Plazo para pacientes fallecidos | PENDIENTE | POR VALIDAR |
| Criterio de paso a archivo intermedio | PENDIENTE | POR VALIDAR |
| Procedimiento y constancia de destrucción | PENDIENTE | POR VALIDAR |
| Retención de `audit_events` | PENDIENTE | Coordinar con ADR-006 |
| Retención de respaldos | PENDIENTE | Coordinar con ADR-001 |
| Qué pasa con el papel no digitalizado | PENDIENTE | Coordinar con `DATA_MIGRATION_PLAN.md` |

**Sin estos valores no se puede cerrar F3.** No se inventan plazos.

## 6. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | Requisitos técnicos exactos de la firma según RM 462-2023 (tipo de certificado, formato, sello de tiempo) | Asesor legal + resp. técnico | Antes de F7 |
| 2 | ¿Opción A, B, C o D? | Dirección Médica + asesor legal | Antes de F7 |
| 3 | ¿Cómo firman los profesionales visitantes extranjeros? | Asesor legal | Antes de F7 |
| 4 | Plazos de retención y destrucción | Asesor legal + Dirección Médica | **Antes de F3** |
| 5 | ¿Qué roles pueden emitir un addendum y con qué límite de tiempo? | Dirección Médica | Antes de F7 |
| 6 | Presupuesto y proveedor del certificado | Administración | **Ya** (plazo largo) |

## 7. Cómo se revierte

Cambiar el mecanismo de firma después de haber firmado historias reales obliga a conservar
dos esquemas de validación en paralelo, para siempre. **Decidir antes de F7 o asumir deuda
permanente.**

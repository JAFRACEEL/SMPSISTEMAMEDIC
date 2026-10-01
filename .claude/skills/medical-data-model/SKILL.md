---
name: medical-data-model
description: Modelo de datos canónico de SISTEMAMEDIC: identidad múltiple con identificador interno, NN/emergencia, menores con representante y las entidades del Plan v1.2 §15. Úsala al diseñar tablas, migraciones, esquemas Pydantic o cualquier consulta sobre pacientes.
---

# Modelo de datos clínico - SISTEMAMEDIC

## 1. Regla estructural

**Prohibida una tabla contenedora tipo `clinical_record`.** La información clínica se modela
con entidades específicas y relacionadas. Un "cajón" genérico impide auditar, versionar y
aplicar permisos por tipo de dato.

## 2. Identidad del paciente

### Identificador interno
Cada paciente tiene **siempre** un identificador interno opaco (`patients.id`, UUID), generado
por el sistema. Es la única clave que puede faltar nunca. Nunca se muestra como "número de DNI"
ni se deriva de datos personales.

### Documentos (0..n)
`patient_identifiers`: un paciente puede tener cero, uno o varios documentos.

| Campo | Notas |
|---|---|
| `patient_id` | FK |
| `type` | `DNI`, `CE`, `PASAPORTE`, `CPP`, `OTRO` |
| `value` | texto; normalizado (sin espacios, mayúsculas) |
| `issuing_country` | ISO 3166-1 alfa-2 |
| `valid_from`, `valid_to` | vigencia, nullable |
| `is_primary` | a lo sumo uno activo por paciente |
| `verified_by`, `verified_at` | quién verificó el documento físico |

Unicidad: **parcial**, `(type, value, issuing_country)` único entre registros activos.
No global, porque un documento puede reemitirse o corregirse.

### NN y emergencia
Un paciente puede crearse **sin ningún documento**:
- `patients.is_unidentified = true`, con un alias generado (`NN-AAAAMMDD-####`).
- Datos mínimos: sexo estimado, edad estimada, lugar y momento de ingreso.
- La atención **no se bloquea** por falta de filiación.
- Queda en una cola de **identificación pendiente** para completar después.

### Merge auditado
Cuando se descubre que dos registros son la misma persona:
- Se elige un registro superviviente; el otro queda `merged_into_id` y **no se borra**.
- Se registra actor, momento, motivo y la evidencia usada.
- **Reversible**: el plan de merge documenta cómo deshacerlo.
- Ante duda razonable **no se fusiona**: se marca `identity_uncertain = true`.

### Menores y representantes
`representatives`: vínculo (`madre`, `padre`, `tutor`, `otro`), documento del representante,
fecha de inicio y fin del vínculo, y evidencia. Un menor **no** se registra con el documento
del representante como propio.

## 3. Entidades (Plan v1.2 §15)

**Identidad y derechos**
- `patients` - persona atendida; identificador interno, datos de filiación, banderas NN y
  `identity_uncertain`, `merged_into_id`.
- `patient_identifiers` - documentos 0..n (arriba).
- `representatives` - representantes legales de menores e incapaces.
- `consents` - consentimientos otorgados, con tipo, versión del aviso, fecha, canal y revocación.
- `privacy_notices` - versiones del aviso de privacidad; `consents` apunta a una versión.
- `data_subject_requests` - derechos ARCO: tipo, fecha, plazo, estado, resolución.

**Clínico**
- `allergies` - alérgeno, tipo de reacción, severidad, estado (activa/resuelta), origen.
- `problem_list` - problemas activos y resueltos, con CIE-10 y fechas.
- `encounters` - atención; `campaign_id` opcional; estado según `clinical-workflows`.
- `diagnoses` - diagnósticos del encuentro, con CIE-10, tipo (presuntivo/definitivo) y orden.
- `clinical_signatures` - firma del profesional: quién, cuándo, con qué certificado, sobre qué
  documento y con qué algoritmo (RM 462-2023).
- `signed_documents` - documento clínico firmado, con su hash y su representación conservada.
- `addenda` - corrección posterior a la firma: autor, fecha, **motivo obligatorio**, referencia.
- `record_versions` - versiones previas íntegras de cualquier registro versionado.

**Catálogos**
- `icd10_codes` - **versionado**: código, descripción, versión de la tabla, vigencia. Un
  diagnóstico guarda la versión con la que se codificó.
- `procedure_catalog` - procedimientos y servicios, con su precio vigente y su vigencia.

**Financiero**
- `payers` - pagadores (particular, SIS, EPS, convenio, campaña).
- `coverages` - cobertura del paciente por pagador, con vigencia y porcentaje.

**Seguridad**
- `mfa_factors` - factores por usuario: tipo (`TOTP`, `FIDO2`), estado, alta, último uso.
- `break_glass_events` - acceso de emergencia: actor, paciente, motivo obligatorio, inicio,
  vencimiento, revisado por, revisado el.
- `audit_events` - append-only: actor, acción, tipo y **ID técnico** del recurso, momento UTC,
  correlación, resultado. **Sin PHI.** Integridad verificable (ADR-006).

**Adjuntos**
- `attachments` - archivo asociado a paciente o encuentro, con **checksum** (SHA-256), tipo MIME,
  tamaño, quién lo subió y cuándo. El contenido vive donde decida el ADR-008, nunca en la fila.

## 4. Reglas transversales

- Todas las marcas de tiempo son `timestamptz` en **UTC**. La zona America/Lima es presentación.
- Nada clínico se borra físicamente. Bajas lógicas con actor y motivo.
- Claves foráneas explícitas; `ON DELETE RESTRICT` en lo clínico.
- Índices mínimos: `patient_identifiers(type, value)`, `patients(apellidos, fecha_nacimiento)`,
  `encounters(patient_id, started_at)`, `appointments(scheduled_at)`,
  `audit_events(occurred_at)`, `audit_events(actor_id, occurred_at)`.
- Ningún nombre de columna, índice o comentario contiene PHI de ejemplo.
- Los datos de prueba son **sintéticos y generados por script** (`docs/TEST_DATA_POLICY.md`).

## 5. Preguntas que debes hacerte antes de añadir una tabla

1. ¿Puede expresarse con una entidad existente sin convertirla en un cajón genérico?
2. ¿Qué rol puede leerla y cuál escribirla? ¿Está esa regla en el backend?
3. ¿Contiene PHI? Si sí: ¿se audita el acceso? ¿se minimiza por rol?
4. ¿Es versionable o inmutable tras firmar? ¿Dónde vive la versión anterior?
5. ¿Qué pasa con ella en una migración y en un restore? ¿Cómo se concilia?

# ADR-002: Identidad del paciente (identificadores múltiples, NN, merge)

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE
- **Fecha de aprobación**: PENDIENTE
- **Fecha límite para decidir**: PENDIENTE - antes de F6
- **Fase que bloquea**: F6 (identidad, consentimientos, agenda) y la migración de históricos
- **Fecha del borrador**: 2026-10-01

## 1. Contexto

Parte de la población atendida **no tiene DNI**: menores sin inscribir, personas de
comunidades ribereñas, extranjeros con CE o pasaporte, pacientes en emergencia sin
acompañante. Un sistema que exija DNI para registrar **bloquea la atención**, y el personal
responde inventando documentos falsos, que es peor.

A la vez, si cualquiera puede crear un paciente sin control, se multiplican los duplicados y
la historia longitudinal deja de existir.

## 2. Criterios

| # | Criterio | Peso |
|---|---|---|
| 1 | La atención nunca se bloquea por falta de documento | Alto |
| 2 | Una sola historia longitudinal por persona | Alto |
| 3 | Los duplicados se detectan y se resuelven con rastro | Alto |
| 4 | Nunca se fusionan dos personas distintas | Alto |
| 5 | Soporta documentos extranjeros y cambios de documento | Medio |
| 6 | El registro en campaña es rápido | Medio |

## 3. Opciones

### Opción A: DNI como clave principal, con excepciones
- **Ventajas**: simple; coincide con la costumbre.
- **Desventajas**: rompe con cada excepción; obliga a inventar documentos; no soporta cambio
  de documento ni extranjeros. **Descartada.**

### Opción B: Identificador interno + `patient_identifiers` 0..n **(recomendada)**
- Identificador interno opaco (UUID) **siempre** presente, generado por el sistema.
- Cero o más documentos por paciente, con tipo, valor, país emisor y vigencia.
- Unicidad **parcial** sobre `(type, value, issuing_country)` entre registros activos.
- Flujo NN/emergencia con alias generado y cola de identificación pendiente.
- Merge auditado y reversible; marca `identity_uncertain` cuando hay duda.
- **Ventajas**: cubre todos los casos reales; permite corregir sin perder historia.
- **Desventajas**: el personal debe aprender a buscar antes de crear; requiere una cola de
  identidades pendientes que alguien atienda.

### Opción C: Identificador interno sin unicidad de documentos
- **Ventajas**: aún más flexible.
- **Desventajas**: no detecta el duplicado evidente. **Descartada.**

## 4. Decisiones concretas que el ADR fija (si se aprueba B)

1. **Identificador interno**: UUID v4 opaco, nunca derivado de datos personales, nunca
   presentado como "número de documento". Se muestra un **código corto legible** derivado solo
   para comunicación verbal.
2. **Tipos de documento admitidos**: `DNI`, `CE`, `PASAPORTE`, `CPP`, `OTRO`.
   PENDIENTE - validar la lista con asesor legal (Q7 de `SOURCES_REGISTER.md`).
3. **Alias NN**: formato `NN-AAAAMMDD-####`. No reutilizable. Datos mínimos: sexo estimado,
   edad estimada, lugar y momento de ingreso, y quién registró.
4. **Búsqueda obligatoria antes de crear**: la interfaz exige buscar y mostrar coincidencias
   antes de habilitar el alta. No es una sugerencia.
5. **Criterios de coincidencia**:
   - Documento exacto → coincidencia **fuerte** (bloquea el alta duplicada).
   - Nombre normalizado + fecha de nacimiento → coincidencia **media** (avisa, exige confirmar).
   - Solo nombre parecido → **no** es coincidencia.
6. **Merge**: lo autoriza un rol específico (PENDIENTE definir cuál), exige **motivo y
   evidencia**, registra actor y momento, conserva el registro no superviviente con
   `merged_into_id` y es **reversible** según procedimiento documentado.
7. **Duda razonable → no se fusiona**: se marca `identity_uncertain = true` y queda en cola.
8. **Menores**: representante registrado en `representatives` con vínculo y evidencia. El menor
   **no** usa el documento del representante como propio.
9. **Cambio o corrección de documento**: se añade un identificador nuevo y se cierra la
   vigencia del anterior. **Nunca se sobrescribe** el valor anterior.

## 5. Consecuencias

- La búsqueda debe ser rápida y tolerante (tildes, ñ, orden de apellidos, errores comunes).
  Es un requisito de rendimiento, no estético: si es lenta, el personal creará duplicados.
- Hace falta un rol y un procedimiento para atender la **cola de identidades pendientes**.
- La migración de históricos hereda estos criterios (`data-migration`).
- Sin validación en línea contra RENIEC (LATER), la verificación del documento es visual y
  se registra quién la hizo.

## 6. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | ¿Qué rol puede fusionar pacientes? | Dirección Médica | Antes de F6 |
| 2 | ¿Quién atiende la cola de identidades pendientes y con qué plazo? | Dirección Médica | Antes de F6 |
| 3 | ¿Lista definitiva de tipos de documento? | Asesor legal + Dirección | Antes de F6 |
| 4 | Requisitos de identificación de menores y de consentimiento del representante | Asesor legal | Antes de F6 |
| 5 | ¿Se acepta registrar sin verificar el documento físico? ¿Con qué marca? | Dirección Médica | Antes de F6 |

## 7. Cómo se revierte

El modelo de identidad es la base de todo lo clínico. Cambiarlo después de F7 implica migrar
historias reales: **prácticamente irreversible**. Debe decidirse bien antes de F6.

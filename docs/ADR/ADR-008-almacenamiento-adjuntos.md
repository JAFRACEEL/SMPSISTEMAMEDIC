# ADR-008: Almacenamiento de adjuntos

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE (responsable técnico + revisor independiente)
- **Fecha límite para decidir**: PENDIENTE - antes de F4
- **Fase que bloquea**: F4 (scaffold e infraestructura)
- **Fecha del borrador**: 2026-10-01

## 1. Contexto

El sistema almacenará fotografías clínicas, historias digitalizadas, resultados escaneados y
documentos firmados. Son **datos de salud** y algunos pesan megabytes. La decisión depende
del ADR-001 (nube, local o mixto) y condiciona respaldos, restore y RTO.

## 2. Criterios

| # | Criterio | Peso |
|---|---|---|
| 1 | Los adjuntos entran en el respaldo y en el restore probado | Alto |
| 2 | Acceso controlado por el backend, nunca por URL adivinable | Alto |
| 3 | Integridad comprobable (checksum) | Alto |
| 4 | Funciona en modo degradado según ADR-001 | Alto |
| 5 | Costo de almacenamiento a 5 años | Medio |
| 6 | Simplicidad operativa | Alto |

## 3. Opciones

### Opción A: Dentro de PostgreSQL (`bytea` o large objects)
- **Ventajas**: un solo respaldo; transaccional; sin rutas que gestionar.
- **Desventajas**: la base crece mucho y el **restore se vuelve lento** (impacta el RTO);
  el respaldo diario se hace pesado.

### Opción B: Sistema de archivos local + metadatos en la base **(recomendada si ADR-001 = local o mixto)**
- Archivo en disco con nombre derivado del `id` y del hash; fila en `attachments`.
- **Ventajas**: base pequeña y restore rápido; simple; funciona sin internet.
- **Desventajas**: dos cosas que respaldar y que mantener consistentes; hay que **probar el
  restore de ambas juntas**.

### Opción C: Almacenamiento de objetos (S3 o compatible) + metadatos en la base
- **Ventajas**: escalable, versionado y durabilidad del proveedor.
- **Desventajas**: **sin internet no hay adjuntos**; posible transferencia internacional;
  costo recurrente.

### Opción D: B + réplica a objetos (mixto)
- Local para operar, copia remota para durabilidad.
- **Ventajas**: cubre continuidad y durabilidad.
- **Desventajas**: más piezas; requiere los dos administradores del `CUSTODY_REGISTER.md`.

## 4. Recomendación

**Coherente con el ADR-001**: si el hosting es local o mixto, **opción D** (B con réplica).
Si el hosting es exclusivamente nube, **opción C**.
**No se recomienda A**: el impacto en el tiempo de restore compromete el RTO.

## 5. Decisiones que el ADR fija (cualquiera sea la opción)

1. **Metadatos siempre en `attachments`**: paciente o encuentro, tipo MIME, tamaño,
   **checksum SHA-256**, quién lo subió, cuándo, origen. El contenido nunca va en la fila.
2. **Acceso siempre por el backend**, con autorización por rol y ámbito. **Nunca** una URL
   pública ni adivinable. Si se usan URL firmadas, con vencimiento corto y auditadas.
3. **Toda descarga se audita** (`audit_events`), igual que un acceso clínico.
4. **Verificación de integridad**: el checksum se comprueba al descargar; una discrepancia es
   un incidente, no un error que se ignora.
5. **Validación en la subida**: tipo MIME permitido (lista blanca), tamaño máximo,
   análisis antivirus si está disponible. Nunca se confía en la extensión.
6. **Sin PHI en el nombre del archivo ni en la ruta**: se usa el `id`, no "Juan_Perez_rx.jpg".
7. **Cifrado en reposo**.
8. **Respaldo conjunto**: el procedimiento de restore restaura base **y** adjuntos, y la
   prueba del gate S13 verifica que un adjunto restaurado abre y su checksum coincide.
9. **Retención**: la misma que el registro clínico al que pertenece (ADR-003 §5).

## 6. Consecuencias

- El tiempo de restore medido en F4 debe incluir los adjuntos; si no, el RTO es ficticio.
- La digitalización masiva de historias (ver `DATA_MIGRATION_PLAN.md`) puede generar un
  volumen muy superior al de la operación diaria: hay que **estimarlo** en Discovery
  (`DATA_INVENTORY.md` T2) antes de dimensionar.
- Si se elige C o D con proveedor fuera de Perú, aplica el ADR-004 §D7 (transferencia
  internacional) y hace falta contrato de encargado.

## 7. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | Opción B, C o D (tras decidir ADR-001) | Resp. técnico + Dirección | Antes de F4 |
| 2 | Volumen estimado de digitalización | Administración (Discovery) | Antes de F4 |
| 3 | Si hay proveedor externo: contrato de encargado | Asesor legal | Antes de F4 |
| 4 | Presupuesto de almacenamiento a 5 años | Administración | Antes de F4 |

## 8. Cómo se revierte

Mover adjuntos entre backends es mecánico mientras el volumen sea bajo. Después de digitalizar
decenas de miles de páginas, deja de serlo. **Decidir antes de la digitalización masiva.**

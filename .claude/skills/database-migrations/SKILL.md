---
name: database-migrations
description: Reglas de migración de esquema con Alembic en SISTEMAMEDIC - no destructivas por defecto, respaldo y restore probado antes de cambios mayores, rollback real y aprobación humana para operaciones destructivas. Úsala al crear o revisar cualquier migración.
---

# Migraciones de esquema - SISTEMAMEDIC

Herramienta: **Alembic** sobre SQLAlchemy y PostgreSQL.

## 1. Principio

**No destructivas por defecto.** Una migración nunca debe poder perder información clínica.
Si un cambio puede perder datos, no se ejecuta sin aprobación humana escrita.

## 2. Clasificación

| Tipo | Ejemplos | Requiere |
|---|---|---|
| **Segura** | Añadir tabla; añadir columna anulable; añadir índice `CONCURRENTLY`; añadir restricción `NOT VALID` y validarla después | Revisión normal |
| **Sensible** | Backfill masivo; cambiar nulabilidad; renombrar; cambiar tipo compatible | Respaldo previo + restore probado |
| **Destructiva** | `DROP TABLE`, `DROP COLUMN`, `TRUNCATE`, `DELETE` masivo, cambio de tipo con pérdida | **Aprobación humana en `docs/APPROVALS.md`** |

Una migración destructiva sin su fila aprobada es un hallazgo **P0**.

## 3. Patrón de cambio en varias etapas (expand / migrate / contract)

Para cambiar una columna sin interrumpir ni perder:

1. **Expand**: añadir la columna nueva, **anulable**, sin tocar la vieja. Desplegar.
2. **Migrate**: escribir en ambas desde la aplicación; backfill por lotes con reintento.
3. **Verificar**: conteos y hash de control coinciden entre columna vieja y nueva.
4. **Contract**: solo tras verificar y con aprobación, dejar de escribir en la vieja y, en una
   migración posterior y separada, retirarla.

Nunca se hacen los cuatro pasos en una sola migración.

## 4. Requisitos de cada archivo de migración

- `revision` y `down_revision` correctos; una sola cabeza (`alembic heads` lo confirma).
- **`downgrade` real y probado en local.** `pass` en `downgrade` no es aceptable salvo que
  la operación sea aditiva pura y se documente por qué.
- Backfill **por lotes** (no una sentencia que bloquee la tabla entera) con progreso.
- Índices en tablas grandes: `CREATE INDEX CONCURRENTLY` fuera de transacción.
- Sin datos reales ni semillas con PHI dentro de la migración.
- Comentario de cabecera en español: qué cambia, por qué, y a qué feature pertenece.

## 5. Antes de un cambio mayor

Lista obligatoria:

1. **Respaldo** tomado y su ubicación registrada.
2. **Restore probado** en un entorno local a partir de ese respaldo, con datos sintéticos.
3. **Tiempo de restore medido** y comparado con el RTO del ADR-001. Si lo supera, se escala.
4. Conteos antes/después definidos y automatizados.
5. Plan de reversión escrito, con el punto de retorno.
6. Ventana acordada con Dirección Médica si afecta la operación.

## 6. Quién ejecuta qué

- **Claude Code / `database-architect`**: escribe la migración y la prueba **solo en local con
  datos sintéticos**. No tiene credenciales de staging ni de PROD.
- **CI/CD**: ejecuta las migraciones en staging y PROD, siempre tras aprobación humana
  registrada.
- **Migración de datos reales históricos**: la ejecuta **una persona autorizada en entorno
  aislado**, sin Claude Code (ver skill `data-migration`).

## 7. Verificación posterior

- `alembic current` coincide con la revisión esperada.
- Conteos y restricciones verificadas (`NOT VALID` → `VALIDATE CONSTRAINT`).
- Consultas críticas siguen usando índice (plan de ejecución revisado).
- La suite de pruebas pasa contra el esquema nuevo.
- `docs/DATABASE_SCHEMA.md` actualizado en el mismo cambio.

## 8. Señales de alarma

Detente y escala si ves cualquiera de estas:

- Una migración que hace `DROP` "porque la columna ya no se usa".
- Un `downgrade` vacío en un cambio no aditivo.
- Dos cabezas de Alembic tras una fusión de ramas.
- Un backfill en una sola sentencia sobre una tabla clínica.
- Una migración que inserta datos que parecen reales.
- Una migración que se ejecutaría sin respaldo verificado.

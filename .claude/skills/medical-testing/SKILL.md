---
name: medical-testing
description: Catálogo de pruebas obligatorias de SISTEMAMEDIC - concurrencia de citas y stock, duplicados e identidad incierta, NN y merge, menores, permisos positivos y negativos, IDOR, inmutabilidad, transiciones inválidas, break-glass, vencimiento de visitantes, regresión, resiliencia y migración. Úsala al escribir o revisar pruebas.
---

# Catálogo de pruebas - SISTEMAMEDIC

Regla: **una feature sin prueba negativa no está probada.** Y **todo bug corregido añade un
test de regresión** que referencia el hallazgo.

Todos los datos son **sintéticos**, generados por script con semilla fija
(`docs/TEST_DATA_POLICY.md`). Ningún DNI, nombre o historia real, ni "de ejemplo".

## 1. Concurrencia

| Caso | Esperado |
|---|---|
| Dos reservas del mismo cupo de cita en paralelo | Solo una confirma; la otra recibe conflicto claro |
| Dos dispensaciones simultáneas del último stock | Una gana; **nunca stock negativo** |
| Dos firmas del mismo encuentro | Una firma; la segunda falla por estado |
| Dos merges cruzados de los mismos pacientes | Serializado; sin ciclo `merged_into_id` |

Técnica: ejecutar en hilos o tareas reales, no simular. Verificar en base, no en la respuesta.

## 2. Identidad

- Alta de paciente **sin ningún documento** → se crea con identificador interno.
- Alta **NN de emergencia** → alias generado, atención no bloqueada, cola de identificación.
- Menor **con representante** → vínculo registrado; el menor no usa el documento del adulto.
- Documento extranjero (CE, pasaporte, CPP) con país emisor.
- Dos pacientes con el mismo nombre y distinta fecha de nacimiento → **no** se fusionan.
- Dos registros de la misma persona → **merge** con actor, motivo y rastro; el no superviviente
  conserva su fila con `merged_into_id`.
- Duda razonable → `identity_uncertain = true` y **no** se fusiona.
- Reversión del merge según el plan documentado.

## 3. Permisos

Por **cada** endpoint y **cada** rol:

- **Positivo**: el rol autorizado obtiene 2xx y los campos que le corresponden.
- **Negativo**: cada rol no autorizado obtiene 403 (o 404 si revelar la existencia ya filtra).
- **Minimización**: la respuesta del rol limitado **no incluye** los campos restringidos
  (comprobar el cuerpo, no la interfaz).
- **IDOR**: usuario A solicita por ID el recurso de B → falla.
- **Escalada**: usuario sin privilegio intenta la acción administrativa → falla.
- Sin token, token vencido, token de cuenta `expired` → falla.

## 4. Inmutabilidad e integridad clínica

- `Encounter` firmado: `PATCH`/`PUT` → falla; el contenido en base no cambia.
- Addendum tras la firma: se crea, referencia el original, exige **motivo**.
- Resultado de laboratorio `validated`: edición → falla; `amended` conserva la versión previa.
- Receta en `draft`: intento de dispensar → **falla** (caso P0 clásico).
- `record_versions` conserva el contenido anterior **byte a byte** comparable.
- Borrado físico de registro clínico → no existe la ruta; si existe, es P0.

## 5. Transiciones inválidas

Por cada máquina de estados de la skill `clinical-workflows`, probar **al menos una**
transición inválida por estado y verificar que el backend la rechaza, aunque la interfaz no
la ofrezca. `rescheduled` sin `rescheduled_to_id` debe fallar.

## 6. Break-glass y cuentas visitantes

- Break-glass sin motivo → falla.
- Break-glass concedido → vence solo; tras el vencimiento el acceso falla.
- Break-glass genera evento en `break_glass_events` y en `audit_events`, y dispara alerta.
- Cuenta visitante `expired` → cualquier petición autenticada falla **en el backend**.
- Cierre de campaña → cuentas visitantes asociadas quedan suspendidas.

## 7. Auditoría y logs

- Cada acceso a información clínica deja un `audit_event` con actor, acción, ID del recurso.
- **Sin PHI en logs**: aserción sobre la salida capturada (ni nombres, ni documentos,
  ni diagnósticos, ni texto libre clínico).
- Intento de alterar un `audit_event` → falla o rompe la verificación de integridad.

## 8. Resiliencia

- Caída a mitad de transacción (excepción forzada) → estado consistente, sin registro huérfano.
- Pérdida de conexión del frontend durante un formulario largo → el usuario no pierde el
  trabajo en silencio y ve el estado real.
- Reintento de una operación idempotente → no duplica.

## 9. Migración

- **Conteos**: filas en origen = filas en destino, por tabla y por periodo.
- **Hash** de control de un conjunto de campos clave: debe coincidir.
- Deduplicación: los casos límite preparados se resuelven como dice el plan.
- Un error de conciliación distinto de cero **rechaza** la migración.
- Restore de respaldo: conteos y hash coinciden, y el tiempo medido se compara con el RTO.

## 10. Regresión

- Un test por bug corregido, con el identificador del hallazgo en el nombre o el docstring.
- La suite de regresión corre en CI en cada cambio.

## 11. Qué pegar al informar

Siempre la **salida real** de la ejecución (`pasadas/total`), nunca una afirmación sin
evidencia. Si algo no se pudo automatizar, decir cuál y por qué, y pasarlo a prueba humana.

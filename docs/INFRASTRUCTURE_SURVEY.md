# Relevamiento de infraestructura - SISTEMAMEDIC

> **BORRADOR - PLANTILLA DE DISCOVERY (F2). No contiene hallazgos.** Gate H2.
> Insumo directo del **ADR-001** (hosting, RPO/RTO, modo degradado) y de
> `BUDGET_AND_PROCUREMENT.md`.
> **No se escriben credenciales, IP públicas ni claves Wi-Fi en este documento.**

## Guion de entrevista / inspección

1. ¿Cuántas computadoras hay y dónde? ¿Qué edad tienen?
2. ¿Qué sistema operativo? ¿Están actualizadas? ¿Tienen antivirus?
3. ¿Hay servidor? ¿Dónde está físicamente? ¿Quién entra a ese espacio?
4. ¿Cómo es el internet? ¿Qué proveedor, qué velocidad, qué tan estable?
5. ¿Con qué frecuencia se va la luz? ¿Cuánto dura típicamente?
6. ¿Hay UPS o generador? ¿Funcionan? ¿Cuándo se probaron por última vez?
7. ¿Cómo es la red interna? ¿Cableada, Wi-Fi, ambas? ¿Hay red de invitados separada?
8. ¿Hay impresoras? ¿Dónde? ¿Qué imprimen?
9. ¿Quién da soporte técnico hoy? ¿Es interno o externo?
10. ¿Hay respaldos de algo? ¿Dónde se guardan? ¿Se han probado?
11. ¿Las computadoras tienen contraseña? ¿Se comparte?
12. ¿Hay cámaras, control de acceso o alarma?

## Tablas a completar

### T1. Equipos

| # | Equipo | Ubicación | Tipo | Antigüedad | SO y versión | RAM / disco | Estado | ¿Compartido? |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

### T2. Servidor y sala técnica

| Elemento | Respuesta |
|---|---|
| ¿Existe un servidor? | |
| Especificaciones | |
| Ubicación física | |
| ¿Espacio con llave? ¿Quién tiene llave? | |
| Ventilación / aire acondicionado | |
| Riesgo de humedad o inundación | |
| ¿Hay rack? | |

### T3. Energía

| Elemento | Respuesta |
|---|---|
| Frecuencia de cortes (por semana/mes) | |
| Duración típica | |
| Duración del corte más largo recordado | |
| ¿Hay UPS? Capacidad y autonomía | |
| ¿Hay generador? ¿Automático o manual? | |
| ¿Cuándo se probó por última vez? | |
| ¿Qué equipos están protegidos? | |

### T4. Conectividad

| Elemento | Respuesta |
|---|---|
| Proveedor principal | |
| Velocidad contratada / real | |
| Estabilidad (caídas por semana) | |
| ¿Hay enlace de respaldo? | |
| ¿Datos móviles como contingencia? | |
| Latencia hacia servicios en la nube | |

### T5. Red interna

| Elemento | Respuesta |
|---|---|
| ¿Cableada, Wi-Fi o ambas? | |
| Equipos de red (marca, edad) | |
| ¿Red de invitados separada? | |
| ¿Segmentación por área? | |
| ¿Quién administra el router? | |
| ¿Contraseña de administración por defecto? | |

### T6. Impresoras y periféricos

| # | Equipo | Ubicación | Uso | Estado | ¿En red? |
|---|---|---|---|---|---|
| | | | | | |

### T7. Respaldos actuales

| # | Qué se respalda | Cómo | Dónde se guarda | Frecuencia | ¿Cifrado? | ¿Se ha probado un restore? |
|---|---|---|---|---|---|---|
| | | | | | | |

### T8. Soporte técnico

| Elemento | Respuesta |
|---|---|
| ¿Quién da soporte hoy? | |
| ¿Interno o externo? | |
| Tiempo de respuesta típico | |
| ¿Hay contrato? | |
| ¿Quién conoce las contraseñas de administración? | |

### T9. Seguridad física

| Elemento | Respuesta |
|---|---|
| Control de acceso al local | |
| Acceso al archivo de historias | |
| Cámaras | |
| Alarma | |
| ¿Hay pantallas visibles al público? | |

## Qué decide esto

| Pregunta del ADR-001 | Depende de |
|---|---|
| ¿Nube, on-premise o mixto? | T3, T4, T8 |
| **RPO** (cuánta información se puede perder) | Dirección Médica + T7 |
| **RTO** (cuánto puede estar caído) | Dirección Médica + T3 |
| Modo degradado | T3, T4 y `AS_IS_WORKFLOWS.md` T4 |
| Inversión en UPS, red y equipos | T1, T3, T4, T5 |

**Advertencia firme**: en Iquitos, un servidor local sin UPS ni enlace redundante no cumple
continuidad, y una solución solo en la nube sin enlace estable tampoco. La decisión no puede
tomarse sin estas tablas completas.

## Huecos detectados

| # | Qué falta saber | Por qué importa | A quién preguntar | Bloquea a |
|---|---|---|---|---|
| | | | | |

# Roles de usuario - SISTEMAMEDIC

> **BORRADOR - PLANTILLA DE DISCOVERY (F2). No contiene hallazgos.** Gate H2.
> Insumo directo de la matriz RBAC de F5. Sin nombres de personas si se prefiere; basta el rol.

## Guion de entrevista

1. ¿Quiénes trabajan aquí y qué hace cada uno? Incluya al personal a tiempo parcial.
2. ¿Quién cubre a quién cuando falta alguien? ¿Qué hace entonces que normalmente no hace?
3. ¿Qué información necesita ver cada persona para hacer su trabajo? ¿Y cuál **no** debería ver?
4. ¿Hay computadoras compartidas? ¿Quiénes las usan y cómo?
5. ¿Comparten usuario o contraseña hoy? (pregunta directa, sin juicio)
6. ¿Quién puede anular, corregir o borrar algo? ¿Qué pasa si se equivocan?
7. ¿Quién necesita acceso de emergencia a una historia que normalmente no le toca?
8. ¿Cómo se da de alta y de baja a una persona? ¿Quién lo autoriza?
9. ¿Qué pasa con los profesionales visitantes de campaña? ¿Cuánto tiempo están?
10. ¿Alguien necesita acceder desde fuera del Centro Médico? ¿Quién y para qué?

## Tablas a completar

### T1. Roles

| # | Rol | Cuántas personas | Tareas principales | Qué debe VER | Qué NO debe ver | ¿Puede firmar? | ¿Requiere MFA? |
|---|---|---|---|---|---|---|---|
| 1 | Recepción / admisión | | | | | No | PENDIENTE |
| 2 | Enfermería / triaje | | | | | PENDIENTE | PENDIENTE |
| 3 | Médico | | | | | **Sí** | **Sí** |
| 4 | Laboratorio | | | | | PENDIENTE | PENDIENTE |
| 5 | Farmacia | | | | | No | PENDIENTE |
| 6 | Caja / administración | | | | | No | PENDIENTE |
| 7 | Dirección Médica | | | | | PENDIENTE | **Sí** |
| 8 | Administrador del sistema | | | | | No | **Sí** |
| 9 | Profesional visitante (campaña) | | | | | PENDIENTE | **Sí** |
| 10 | (otros) | | | | | | |

### T2. Suplencias

| # | Rol | Lo cubre | Qué permisos adicionales necesita | ¿Temporal? |
|---|---|---|---|---|
| | | | | |

### T3. Estaciones de trabajo

| # | Ubicación | ¿Compartida? | Quiénes la usan | ¿Hay datos visibles al público? | Riesgo |
|---|---|---|---|---|---|
| | | | | | |

### T4. Acciones sensibles y quién las hace

| # | Acción | Rol que la hace hoy | ¿Requiere autorización? | ¿Queda registro hoy? |
|---|---|---|---|---|
| 1 | Corregir una atención ya cerrada | | | |
| 2 | Anular una cita o cobro | | | |
| 3 | Fusionar dos pacientes | | | |
| 4 | Ver una historia sin ser quien atiende (break-glass) | | | |
| 5 | Exportar o imprimir en lote | | | |
| 6 | Dar de alta a un usuario | | | |
| 7 | Cambiar permisos | | | |
| 8 | Ajustar stock | | | |

### T5. Altas y bajas

| Elemento | Respuesta |
|---|---|
| ¿Quién autoriza un alta de usuario? | |
| ¿Cuánto tarda hoy? | |
| ¿Quién revoca al salir alguien? | |
| ¿En cuánto tiempo? | |
| ¿Hay revisión periódica de usuarios activos? | |

### T6. Acceso desde el exterior

| # | Rol | ¿Necesita acceso remoto? | Para qué | Frecuencia | Desde dónde |
|---|---|---|---|---|---|
| | | | | | |

## Reglas que ya son firmes (no dependen de Discovery)

- **Cuentas personales**, nunca compartidas.
- **MFA obligatorio desde F5** para administradores y médicos (TOTP o FIDO2; SMS no principal).
- Cuentas de visitantes **temporales con vencimiento** aplicado en el backend.
- **Autorización en el backend**; ocultar un botón no cuenta.
- **Mínimo privilegio** y separación de filiación, clínica, caja y administración.
- **Break-glass** con motivo, tiempo limitado, alerta y revisión posterior.
- Por defecto, el **acceso desde fuera de la red está denegado** (ADR-001).

## Huecos detectados

| # | Qué falta saber | Por qué importa | A quién preguntar | Bloquea a |
|---|---|---|---|---|
| | | | | |

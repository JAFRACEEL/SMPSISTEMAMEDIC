---
name: release-readiness
description: Checklist de preparación para entregar una oleada de SISTEMAMEDIC (Plan v1.2 §26), ciclo abreviado B-E (§14.1), pentest, operación en paralelo, rollback y evidencias. Úsala antes de declarar lista una fase o una oleada.
---

# Preparación de entrega - SISTEMAMEDIC

## 1. Checklist por oleada (Plan v1.2 §26)

Nada se marca sin **evidencia** (ruta de archivo, commit, acta o captura sintética).

**Producto**
- [ ] Todos los criterios de aceptación de la oleada tienen evidencia.
- [ ] Cero hallazgos **P0** y cero **P1** abiertos (`final-reviewer`).
- [ ] Definition of Done de 11 dimensiones cumplida por cada feature.

**Pruebas**
- [ ] Suite completa en verde en CI, con la salida adjunta.
- [ ] E2E sintético del flujo completo de la oleada.
- [ ] Pruebas negativas, IDOR y concurrencia, con resultados.
- [ ] Performance con dataset sintético del tamaño esperado + concurrencia.
- [ ] Suite de regresión incluye un test por cada bug corregido.

**Seguridad y privacidad**
- [ ] Gates S1-S13 de la skill `healthcare-security` verificados.
- [ ] Escaneo de dependencias sin vulnerabilidad crítica abierta.
- [ ] Escaneo de secretos limpio sobre el diff **y el historial**.
- [ ] Revisión independiente de auth, RBAC, break-glass, auditoría e inmutabilidad.
- [ ] **Pentest externo** realizado y remediación cerrada (antes de F9A/go-live).

**Datos y continuidad**
- [ ] Respaldo automatizado y **restore probado** con el tiempo medido contra el RTO.
- [ ] Simulacro de caída y de rollback ejecutado y documentado.
- [ ] Plan de migración conciliado (conteos y hash) cuando aplique.
- [ ] Modo degradado probado (corte de energía y de conectividad).

**Operación**
- [ ] Runbooks escritos y probados por alguien distinto de quien los escribió.
- [ ] `docs/CUSTODY_REGISTER.md` completo: mínimo dos administradores por recurso.
- [ ] Monitoreo y alertas configurados; alguien recibe las alertas.
- [ ] Material de capacitación entregado y sesión realizada con los champions del área.

**Gobierno**
- [ ] Gate correspondiente **APROBADO** en `docs/APPROVALS.md`, con aprobador y fecha.
- [ ] ADR que la oleada usa, aprobados.
- [ ] Riesgos residuales listados y aceptados explícitamente por quien corresponde.

## 2. Ciclo abreviado para las oleadas B-E (Plan v1.2 §14.1)

Las oleadas posteriores no repiten la fase completa. Secuencia:

1. **Diseño corto**: `medical-architect` actualiza alcance y ADR solo si cambia algo.
2. **Build con datos sintéticos**: backend + frontend según el ciclo por feature.
3. **E2E** del flujo del área.
4. **Revisión de seguridad focal**: solo lo nuevo y sus fronteras, no toda la aplicación.
5. **Material de UAT** para el área.
6. **UAT del área** → aprobación humana.
7. **Migración/configuración, operación en paralelo y go-live**: **siempre humanos**.

Condición de entrada: gate H12 aprobado y la oleada previa en hypercare **sin bloqueantes**.

## 3. Pentest externo

- Lo realiza un **tercero**, no el equipo ni Claude Code.
- Se contrata con antelación: está en la **ruta crítica** antes de F9A
  (`docs/BUDGET_AND_PROCUREMENT.md`).
- Entregable del equipo al pentester: dossier con alcance, arquitectura, roles, credenciales
  de prueba en entorno con **datos sintéticos**, y lista de controles a verificar.
- Entregable del pentester: informe con severidades y pruebas de concepto.
- El equipo produce la **lista de remediación** con responsable y fecha; los críticos y altos
  se cierran y se **reverifican** antes del go-live.

## 4. Operación en paralelo

- El sistema nuevo y el proceso anterior conviven durante un periodo acordado.
- Se definen de antemano: duración, qué se compara, quién concilia y el **criterio de salida**.
- Discrepancias registradas y resueltas; ninguna se cierra sin explicación.
- Es **humana**: Claude Code no participa en la operación con datos reales.

## 5. Rollback

- Punto de retorno identificado antes de cada go-live.
- Procedimiento escrito, **probado** y con tiempo medido.
- Criterio explícito de "cuándo revertimos", decidido antes de necesitarlo.
- Quién decide revertir, nombrado.

## 6. Evidencias que se archivan

| Evidencia | Dónde |
|---|---|
| Salida de la suite de pruebas | CI + `docs/PROGRESS.md` |
| Informe de seguridad y pentest | `docs/security/` |
| Prueba de restore con tiempo medido | `docs/OPERATIONS_RUNBOOK.md` |
| Conciliación de migración | `docs/DATA_MIGRATION_PLAN.md` |
| Acta de UAT | `docs/APPROVALS.md` (fila) + acta enlazada |
| Aprobación del gate | `docs/APPROVALS.md` |

## 7. Motivos para NO entregar

Cualquiera de estos detiene la entrega, sin discusión:

- Un P0 abierto.
- Restore no probado o fuera del RTO.
- Pentest pendiente o con críticos abiertos (en las fases que lo exigen).
- Un solo administrador en un recurso crítico.
- Datos reales presentes en el repositorio o en un entorno con IA.
- Gate sin aprobar en `docs/APPROVALS.md`.

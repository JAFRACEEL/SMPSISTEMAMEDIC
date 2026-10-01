# Reglas de seguridad propias - SISTEMAMEDIC

Complementan (no sustituyen) al plugin `security-guidance` de Anthropic y a
`.claude/skills/healthcare-security/SKILL.md`.

**Este archivo no contiene ni contendrá secretos.**

## 1. Autorización

- **RBAC en el backend, siempre.** Un control implementado solo en el frontend no existe.
- Toda consulta por ID filtra además por el ámbito autorizado del usuario (IDOR).
- Denegación por defecto: lo no concedido explícitamente, se niega.
- Separar filiación, clínica, caja y administración.

## 2. Información de salud (PHI)

- **Sin PHI en logs**, URL, mensajes de error, trazas, analítica ni telemetría.
  Solo IDs técnicos y `correlation_id`.
- Minimización por rol en la respuesta del servidor, nunca ocultando en el cliente.
- Exportaciones limitadas por rol y auditadas.

## 3. Secretos

- Ningún secreto en el código, en los tests, en los comentarios ni en el historial de Git.
- Todo por variable de entorno; los nombres viven en `.env.example`, los valores en el vault.
- El hook `secrets_guard.py` bloquea lo evidente; la CI escanea el diff y el historial.
- Si crees haber comprometido un secreto: **rótalo primero**, investiga después.

## 4. Integridad clínica

- **Nada firmado o cerrado se sobrescribe ni se elimina.** Corrección por addendum o versión,
  con autor, fecha y motivo.
- Ningún cambio silencioso en la HCE: todo cambio deja rastro verificable.
- La auditoría es append-only o con hash encadenado; su alteración debe ser detectable.

## 5. Datos

- **Solo datos sintéticos** en DEV, CI, STAGING y en cualquier herramienta de IA.
- Los datos reales no se anonimizan con IA: lo hacen personas en entorno aislado.
- Nunca pegues una historia, DNI, nombre o captura real en un prompt.

## 6. Ejecución y entorno

- Nunca `bypassPermissions`. Nunca push forzado. Nunca push a `main`.
- Claude Code no tiene credenciales de staging ni de PROD, y no las pide.
- El despliegue lo hace CI/CD con aprobación humana registrada en `docs/APPROVALS.md`.
- Si un hook te bloquea: **repórtalo y cambia de tarea.** No lo edites ni lo rodees.

## 7. Dependencias

- Versiones fijadas; actualizaciones revisadas.
- Escaneo de dependencias en CI; ninguna vulnerabilidad crítica abierta al entregar.
- Antes de añadir una dependencia nueva: ¿la necesitamos de verdad, quién la mantiene,
  qué permisos pide?

## 8. Qué hacer ante una duda de seguridad

Elige **siempre** la opción más restrictiva, anótala en `docs/SETUP_DECISIONS.md` y sigue.
Si la duda bloquea, repórtala con el rol que debe decidirla.

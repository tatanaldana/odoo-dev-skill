# Session Context & History Log

`odoo-dev-skill` mantiene dos archivos por proyecto que el agente gestiona
automáticamente. El desarrollador no necesita prompts especiales — el skill
se encarga del ciclo completo.

| Archivo | Alcance | Tamaño | Propósito |
|---|---|---|---|
| `context_session.xml` | una tarea activa | máx ~12.000 chars | memoria de trabajo — módulo, modelos, patterns cargados, decisiones, preguntas abiertas |
| `history_context.xml` | todas las sesiones | sin límite, append-only | una entrada `<session>` compacta por tarea terminada — auditoría y dataset futuro |

Ambos viven en `.claude/odoo-dev-skill/` dentro del proyecto Odoo (no en el
directorio global del skill).

---

## Cómo funciona — todo automático

El desarrollador simplemente trabaja. El skill detecta el estado de la sesión
y actúa en consecuencia en cada respuesta:

```
developer: "Crea el módulo fleet_tracking en Odoo 18"
  → agente: no existe context_session.xml → lo crea con status="in_progress"
  → agente: genera el modelo base
  → Stop hook: status=in_progress, archivos actualizados → deja pasar

developer: "Ahora las vistas del modelo"
  → agente: trabaja, termina el bloque modelo+vistas
  → agente: escribe checkpoint con status="checkpoint"
  → Stop hook: status=checkpoint → deja pasar sin verificar archivos

developer: "Agrega ir.model.access.csv"
  → agente: trabaja, escribe checkpoint con status="checkpoint"
  → Stop hook: status=checkpoint → deja pasar

developer: "Perfecto, esto es todo"         ← señal de cierre natural
  → agente: detecta cierre, pone status="completed"
  → Stop hook: status=completed → archiva a history_context.xml
                                → resetea context_session.xml
                                → permite el stop
```

---

## El atributo `status` — cómo el hook decide qué hacer

El Stop hook (`hooks/context_session_guard.py`) lee el atributo `status` del
`context_session.xml` en cada respuesta del agente:

| status | Quién lo pone | Qué hace el hook |
|---|---|---|
| `in_progress` | agente al iniciar o entre checkpoints | verifica budget (~12k chars) + archivos desactualizados; bloquea si algo falla |
| `checkpoint` | agente al terminar un bloque lógico | deja pasar limpio, sin verificar archivos |
| `completed` | agente al detectar señal de cierre | archiva `<session>` a `history_context.xml`, resetea el XML, deja pasar |

### Señales de cierre que el agente detecta automáticamente

**Explícitas** — el usuario dice algo que claramente indica fin:
- "terminamos", "listo", "perfecto así", "esto es todo", "abre el PR", "mergea"

**Implícitas** — el usuario pide algo que solo tiene sentido al cerrar:
- Revisión completa del módulo entero
- Generar el `__manifest__.py` final con todos los archivos listados
- Correr el linter sobre el módulo completo

---

## El PostToolUse hook — feedback inmediato en ediciones

`hooks/odoo_edit_guard.py` corre automáticamente después de cada `Edit` o `Write`
sobre `.py` o `.xml`. Solo interrumpe si el archivo recién editado introduce
un hallazgo **CRITICAL** (SQL injection, `cr.commit()` manual, `attrs=`).
HIGH y MEDIUM se dejan para los agentes de revisión — este hook no genera
fricción en el flujo normal.

---

## Retomar una sesión interrumpida

Si la conversación se cortó o se abre Claude Code nuevo sobre el mismo proyecto,
el desarrollador simplemente continúa trabajando con naturalidad:

```
developer: "Continuemos con la seguridad de fleet_tracking"
  → agente: lee context_session.xml una sola vez
  → retoma desde el último checkpoint sin re-preguntar nada
```

No hace falta ningún prompt especial. El agente detecta el archivo existente
y lo usa.

---

## Configurar los hooks — una vez por proyecto

Los hooks son el respaldo mecánico del ciclo de contexto. El agente los verifica
al inicio de cada tarea y avisa si no están configurados, pero no los escribe —
eso es responsabilidad del comando `init`.

### Primera vez en cada proyecto Odoo

Desde la raíz del proyecto, después de haber instalado el skill globalmente:

```bash
cd /mi-proyecto-odoo
npx github:tatanaldana/odoo-dev-skill init
```

Luego **reiniciar Claude Code**. A partir de ese arranque los hooks están activos.

Lo que hace `init`:
- Resuelve la ruta absoluta al skill instalado globalmente
- Crea `.claude/settings.json` si no existe, o agrega los hooks si ya existe
- No toca ninguna otra clave del archivo
- Funciona en Linux, macOS y Windows

```bash
# Ver qué escribiría sin tocar nada
npx github:tatanaldana/odoo-dev-skill init --dry-run
```

### Qué pasa en la primera sesión sin `init`

El skill funciona normalmente — el agente sigue `SKILL.md` y archiva a
`history_context.xml` por instrucción directa. Los hooks no están como
respaldo en esa primera sesión, pero el flujo principal no depende de ellos.

El agente avisa una sola vez por sesión si detecta que los hooks no están
configurados, sin bloquear el trabajo.

### Proyectos futuros

Cada proyecto nuevo requiere correr `init` una vez desde su raíz antes de
la primera sesión de Claude Code. El install global no se repite.

---

## `.gitignore` recomendado

```gitignore
# Contexto personal — ignorar si el historial no es compartido
.claude/odoo-dev-skill/context_session.xml
.claude/odoo-dev-skill/history_context.xml
```

Eliminar esas líneas si el equipo quiere un historial compartido y versionado
en el repositorio del proyecto.

---

## Por qué importa a largo plazo

Cada `<session>` en `history_context.xml` es un registro estructurado de una
tarea real: qué se pidió, qué patterns se aplicaron, qué archivos se tocaron
y cuál fue el resultado. Es exactamente la forma que necesita un dataset para
evaluar la calidad del skill o construir fine-tuning/RAG desde uso real.
Mantener las entradas tersas y estructuradas ahora es lo que hace posible eso después.
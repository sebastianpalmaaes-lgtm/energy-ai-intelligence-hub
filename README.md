# Energy & AI Intelligence Hub — MVP v1

Dashboard web con dos vistas (briefing y buscador) y recolección diaria de noticias, con cupos máximos **4 Chile / 4 mundo / 5 IA / 2 geopolítica**.

## Primera ejecución local

```bash
python -m pip install -r requirements.txt
python update.py
python -m http.server 8000
```

Abre `http://localhost:8000`.

## Publicación con GitHub Pages (versión corregida)

1. Crea un repositorio **público**, por ejemplo `energy-ai-intelligence-hub`.
2. Sube los contenidos de esta carpeta directamente a la raíz. Importante: la carpeta oculta `.github/workflows/update.yml` debe estar presente.
3. Ve a **Settings > Pages > Build and deployment > Source**, elige **GitHub Actions** (NO "Deploy from a branch").
4. Ve a **Actions > Actualizar y publicar Energy Intelligence > Run workflow**, selecciona `main` y ejecútalo.
5. Revisa que la ejecución termine correctamente y entra a la URL publicada en **Settings > Pages > Visit site**.
6. Si el paso `git push` falla por permisos, ve a **Settings > Actions > General > Workflow permissions > Read and write permissions** y guarda. Si la organización restringe esa opción, consulta al administrador.

**Nota:** el workflow hace la recolección, guarda `data/` y publica directamente el sitio actualizado. El envío de ChatGPT sigue siendo independiente.

## Automatización

`.github/workflows/update.yml` intenta ejecutar todos los días a **08:00 America/Santiago** (respeta cambios de horario). Las ejecuciones programadas de GitHub pueden retrasarse y en repositorios públicos inactivos durante 60 días pueden deshabilitarse. El workflow también permite ejecución manual.

## Importante sobre el alcance y la confiabilidad

- No se incluyen noticias ficticias o precargadas: el archivo `data/latest.json` inicial está vacío.
- Se utiliza Google News RSS (interfaz no oficial y no garantizada), con búsqueda en ediciones de Chile y EE. UU. Si el feed deja de funcionar, habrá que sustituirlo.
- El script usa títulos, extractos, fuente y fecha aportados por el feed, seleccionando por palabras clave y actualidad. **No comprueba el contenido completo** del medio ni utiliza un LLM. Los comentarios técnicos son **preguntas/ángulos de seguimiento genéricos**, no análisis generado a partir del artículo.
- El número 15 es un **objetivo/cupo máximo**; puede haber menos resultados pertinentes y recientes. El sistema nunca crea noticias para llenar cupos.
- Los enlaces pueden apuntar a Google News y de allí a la fuente. Para obtener URL original directa y análisis técnico de IA en v2 se debe añadir una API o extractor compatible con licencias y términos de las fuentes y un proceso de validación.
- Los resultados del **briefing en ChatGPT no se sincronizan automáticamente** a esta web; son dos procesos separados.
- La zona horaria de la interfaz y la automatización es America/Santiago.

## Próximas mejoras

Validación editorial de enlaces originales; resúmenes técnicos con API LLM, citando frases del artículo; deduplicación semántica; índice histórico en web; monitorización de errores, métricas CEN y tendencias.

## Integración de las dos salidas

- **Vista Briefing del día en la web**: usa **exactamente el mismo `data/latest.json`** que la vista de noticias, con fuente, fecha, extracto y guía de seguimiento. Los tres destacados iniciales no son una clasificación editorial: corresponden a los primeros 3 resultados del recopilador.
- **Briefing programado en ChatGPT**: ya se configuró de forma independiente en ChatGPT, diariamente a las 08:00 Chile. No existe un vínculo automático entre su respuesta y GitHub. Por tanto, los titulares, enlaces y resúmenes de ambas salidas pueden diferir.
- **Integración real posterior**: crear un backend único que guarde `data/YYYY-MM-DD.json` y un briefing analizado por IA en `data/YYYY-MM-DD-briefing.json`; usar ese mismo backend para generar la web y enviar un correo/aviso diario por un proveedor de notificaciones. Un aviso nativo de una tarea de ChatGPT no se puede sustituir por un envío de ese backend mediante estas herramientas.
- Para que las notas de impacto contengan análisis de artículos (en vez de guías genéricas) será necesario implementar un procesamiento de texto completo con acceso permitido al contenido y una API de IA, con comprobación de fuentes.

## Probar la nueva vista

La página tiene dos pestañas: **Briefing del día** y **Todas las noticias**. Antes de ejecutar `python update.py`, la página muestra correctamente el estado vacío. La actualización en GitHub empieza únicamente cuando se publica el proyecto y se habilita su workflow.

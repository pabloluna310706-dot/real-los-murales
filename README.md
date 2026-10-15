# Real los Murales

Captura de Scaniverse para ver en el navegador de Meta Quest 3 con krpano 1.24.

El archivo PLY original contiene 440,040 splats. Aproximadamente 10,000 forman una esfera panorámica de fondo a unos 240 metros del origen. La versión Quest convierte esa esfera en `murales-background.png` y conserva 220,000 splats cercanos en `murales-quest.splat` para reducir el trabajo de renderizado estereoscópico. El fondo evita las zonas negras que aparecían cuando se retiraban los splats distantes sin reemplazarlos.

`build_quest_assets.py` genera los dos archivos a partir de `murales.splat`, que se conserva como copia compacta completa. krpano muestra una marca de agua de demostración hasta que se use una licencia.

La página abre por defecto un modo de compatibilidad de 80,000 splats con el renderizador estándar de krpano y carga sin streaming. El botón inferior cambia a la versión de 220,000 splats. El estado superior indica si WebGL2 está disponible y cuántos splats reconoce el visor para diagnosticar problemas en Quest.

Abre la URL HTTPS de GitHub Pages en Meta Quest Browser y pulsa el icono VR. La reproducción en el dispositivo aún debe comprobarse allí.

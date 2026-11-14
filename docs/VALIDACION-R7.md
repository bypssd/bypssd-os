# BYPSSD OS Renacer 1.0 · revisión 7

## Cambios visibles

- Página inicial local y sin conexión para Chromium, con búsqueda y enlaces BYPSSD.
- Inicio propio de Firefox y Konqueror; los favoritos iniciales de Konqueror son BYPSSD.
- Los temas de Fedora se sustituyen mediante un RPM que satisface la dependencia
  exacta de Plasma; no se modifican binarios de KDE.
- Se sustituyen los proveedores de fondos F45 y de compatibilidad. SDDM conserva
  sus dependencias satisfechas con el paquete BYPSSD.
- La galería mantiene los temas originales de KDE y añade BYPSSD Renacer.
- Los colores propios y el escritorio conservan la estética de KDE/Breeze.
- Plymouth y KSplash comparten entrada suave, logo, aro amarillo y barra de progreso.
- SDDM usa campos oscuros y botón principal amarillo.
- El instalador se oculta en sistemas instalados; el servicio live muestra el
  lanzador BYPSSD durante la sesión temporal.

## Aplicaciones añadidas a la imagen y publicadas en GitHub

Kate, KCalc, KDE Connect, Elisa, Haruna, Filelight, Skanpage, KDE Partition Manager,
KFind, KRDC, GIMP, Inkscape, LibreOffice Math y diccionario español Hunspell.
Mantienen los RPM oficiales, licencias y firmas sin modificar. Sus dependencias
se resuelven mediante los repositorios oficiales; la colección GitHub no es un
espejo completo ni sustituye por sí sola un repositorio DNF firmado.

## Auditoría

El inventario de la raíz ARM64 revisó 41.231 archivos de texto en configuración,
recursos y ejecutables de script. Excluye binarios y archivos de credenciales.
No hubo coincidencias de Fedora en los recursos de apariencia tras la sustitución.
Quedan 438 rutas con menciones técnicas, documentación o avisos de procedencia.
No se ha borrado ni atribuido a BYPSSD el trabajo de sus autores originales.

Registros locales:
- out/logs/r6-vendor-inventory.json
- out/branding-audit-aarch64.json
- out/logs/r7-arm64-final-validation.log

La auditoría estricta de galerías y preferencias de Chromium también se ejecuta
para x64 en CI. Un resultado con coincidencias impide publicar la ISO.

## Comprobaciones realizadas

La sesión live ARM64 de revisión 6 arrancó con SELinux Enforcing, Plasma y Chromium.
Chromium abrió la página local BYPSSD utilizando sus valores reales de primer inicio.
El tema Plymouth se ejecutó en una VT gráfica de prueba con ignore-serial-consoles;
se verificaron su entrada suave, renderizado y rotación sin errores de sintaxis.
La consola serie fuerza normalmente la salida de texto y no representa el arranque
gráfico de un equipo sin consola serie.

La revisión 7 corrige el enlace de LibreOffice de esa página inicial; se
verificó la URL de destino. La imagen final se recompuso, se comprobó su SHA256
y se volvió a arrancar: Chromium abrió la página propia, Tema global mostró
BYPSSD y los tres temas originales de KDE, y Colores mostró Renacer y Breeze.
El greeter actualizado también se renderizó al cerrar la sesión temporal y
desactivar el autologin solo en la RAM del ensayo. No se modificó la ISO en esa prueba.
La instalación completa y el arranque desde disco se validaron en una candidata
anterior con el mismo instalador Anaconda, kernel base e identidad. No se declara
una instalación completa de cada revisión en cada hardware.

Capturas locales:
- out/qemu-test/plymouth-r6-graphical.png
- out/qemu-test/chromium-renacer-r7.png

## Mantenimiento

El Provides del tema coincide con Plasma 6.8.2-1.fc45. Las futuras actualizaciones
que cambien esa dependencia requieren reconstruir y probar el paquete BYPSSD.
No se promete compatibilidad automática con cualquier versión futura de KDE.
Las referencias de ABI, claves, firmas y licencias oficiales se conservan.
Los RPM BYPSSD siguen sin firma de producción; las releases se marcan prerelease.

# Alcance del cambio de referencias

Revisión 1.0-4 (14/11/2026):

- Identidad de sistema, Acerca del sistema, SDDM, Plymouth, fondo y menú: BYPSSD.
- Lanzador de instalación y nombre de producto: BYPSSD OS Renacer.
- Anaconda GTK: stylesheet propia con logo BYPSSD y cabecera propia.
- Anaconda Web UI/Cockpit: directorio branding/bypssd con logo, favicon y colores.
- DNF 5: nombres visibles de repositorios de base y actualizaciones BYPSSD mediante
  la API de overrides, conservando las configuraciones originales y sus firmas.
- No se encontraron Name/Comment con Fedora en los lanzadores .desktop de la
  imagen preparada en esta revisión.

## Lo que no se sustituye

No se ha logrado ni se afirma la eliminación absoluta del texto Fedora de la ISO.
Estos son restos intencionados por compatibilidad o procedencia, no branding propio:

- Identificador de compatibilidad ID_LIKE=fedora y PLATFORM_ID=platform:f45.
- Identificadores de repositorio fedora/updates, servidores oficiales, claves GPG,
  firmas RPM, nombres/versión de paquetes (.fc45) y dependencias.
- fedora-release y fedora-release-common oficiales sin modificar, incluidas sus
  rutas/archivos de texto. Algunos comandos técnicos pueden mostrar su contenido.
- Ruta UEFI EFI/fedora para conservar compatibilidad con shim, GRUB y actualizaciones.
- Texto compilado dentro de aplicaciones oficiales: por ejemplo Chromium anuncia
  su procedencia de compilación. Los créditos, licencias y avisos de autoría no se
  reescriben como si BYPSSD fuese su autor.
- Ayudas, documentación y diagnósticos originales. No se ha auditado cada diálogo
  de cada aplicación ni todas las rutas de error del instalador.
- Nombres de proyectos KDE y sus créditos permanecen en aplicaciones oficiales.

Eliminar todo esto exigiría mantener forks de paquetes, dependencias, repositorios,
firmas y actualizaciones; un reemplazo global de bytes puede inutilizar el sistema.
Se usa el branding por configuración y extensión previsto por cada componente.
Esto no equivale a una distribución independiente del origen de sus paquetes.

La personalización gráfica se valida con capturas y registros en out/qemu-test y
out/logs. La existencia de CSS por sí sola no garantiza el aspecto de cada pantalla.

## Comprobación gráfica de la ISO 1.0-4

El lanzador real se ejecutó como liveuser en QEMU. La bienvenida de Anaconda Web
UI muestra «Instalación de BYPSSD OS Renacer 1.0», el logo original, cabecera
amarilla, botones amarillos y Español (España). Captura:
`out/qemu-test/anaconda-bypssd-4.png`. No se encontró Fedora en esa pantalla.
No se ha auditado cada pantalla, diálogo de ayuda o error del instalador.

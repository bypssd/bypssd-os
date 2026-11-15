# BYPSSD OS Renacer 1.1

Sistema independiente para oficina y educación de BYPSSD Informática Retro,
Valencia. KDE Plasma, español de España, amarillo #FFB800, negro y blanco.

## Estado real

Se ha reconstruido la versión 1.1 sobre **openSUSE Tumbleweed** para ARM64 y
x64. No se puede sustituir el repositorio de una ISO Fedora por openSUSE: sus RPM
no son intercambiables. Las ISO 1.0 anteriores siguen siendo Fedora; su historial
se conserva en [HISTORIAL-FEDORA-1.0.md](docs/HISTORIAL-FEDORA-1.0.md).

La copia masiva del catálogo Fedora se ha cancelado y sus workflows automáticos
están desactivados. Los RPM ya publicados se conservan como historial y no se usan
en las nuevas recetas. No se ha tocado Parallels ni el disco del Mac para instalar Linux.

- [Compilación openSUSE ARM64/x64](https://github.com/bypssd/bypssd-os/actions/workflows/build-opensuse.yml).
- [Paquetes BYPSSD y fuentes](https://github.com/bypssd/bypssd-os/releases): GitHub aloja los RPM propios y sus SRPM, no las ISO públicas.
- Canal propio [BYPSSD Updates](https://bypssd.github.io/bypssd-os/), inicialmente vacío, con índices RPM válidos para ambas arquitecturas.
- Revisión actual: r8, con corrección del arranque de reserva UEFI y presentación del instalador.

## ISO completas y SourceForge

Las ISO finales se guardan en `out/`, con un archivo `.iso.sha256` junto a cada una.
Son imágenes completas para publicar en SourceForge; no necesitan dividirse.
La subida a SourceForge queda en manos de Andy y todavía no se ha configurado un enlace público.

GitHub Actions se utiliza para compilarlas en runners nativos. Los artefactos de
transferencia son temporales (un día de retención) y se retiran una vez descargados,
verificados y utilizados por la prueba de arranque. No se publican ISO en Releases.
Las antiguas Releases que solo contenían ISO están archivadas como borradores.

Para transferir una compilación propia ya terminada al Mac:

```sh
python3 scripts/download-opensuse-fast.py NUMERO_DE_EJECUCION aarch64
python3 scripts/download-opensuse-fast.py NUMERO_DE_EJECUCION x86_64
```

Se necesita la sesión existente de `gh`. El script verifica SHA256 antes de mover
la ISO a `out/`. Los logs de compilación se conservan por separado durante 30 días.

## Repositorios y Discover

El sistema usa los repositorios oficiales de openSUSE para los paquetes de la base;
las firmas y atribuciones originales se conservan. BYPSSD Updates apunta a:

```
https://bypssd.github.io/bypssd-os/tumbleweed/$basearch/updates/
```

El archivo de configuración está en [opensuse/bypssd-updates.repo](opensuse/bypssd-updates.repo).
El canal está habilitado y se refresca aunque no tenga paquetes. Se exige firma
para los RPM (`pkg_gpgcheck=1`); actualmente el índice vacío no lleva firma propia
(`repo_gpgcheck=0`) y se sirve por HTTPS. No se ha creado ni transferido ninguna
clave privada nueva. Antes de publicar RPM propios como actualizaciones se deberá
configurar y distribuir una clave de firma adecuada.

Discover incluye `discover6-backend-packagekit`, `PackageKit-backend-zypp`,
`PackageKit` y `AppStream`. Es una tienda de aplicaciones: no todos los RPM tienen
metadatos para aparecer en ella. Las pruebas de búsqueda e instalación reales se
documentan debajo. Se ha probado una instalación real desde la interfaz de Discover.

Tumbleweed es una distribución rolling: sus repositorios evolucionan. Sus paquetes
y actualizaciones se descargan de sus servidores, sin mantener un espejo completo
en GitHub. El equipo BYPSSD debe seguir validando las personalizaciones.

## Identidad visual y normas de marca

La identidad del producto es BYPSSD OS Renacer. Se conservan nuestros logos,
fondo, colores, tema global `com.bypssd.desktop`, SDDM y Plymouth. Se usa Breeze
oficial de openSUSE; no se reutiliza el plugin binario que se compiló para Fedora.
Las configuraciones específicas del proveedor se sustituyen por branding propio
o por variantes upstream. Calamares reemplaza a Anaconda para instalar desde Live.

BYPSSD es independiente y no es un producto oficial ni patrocinado por openSUSE o
SUSE. No se usan sus logotipos como marca de BYPSSD. Las menciones a openSUSE en
repositorios, firmas, licencias, productos técnicos y documentación de procedencia
se conservan. No se atribuyen a BYPSSD compilaciones realizadas por terceros.

Referencia: [openSUSE Trademark Guidelines](https://en.opensuse.org/openSUSE:Trademark_guidelines)
y [anuncio oficial](https://news.opensuse.org/2009/03/02/opensuse-trademark-guidelines-released/).
La descarga directa del PDF devolvió HTTP 403; se consultaron sus apartados
indexados sobre distribuciones modificadas y referencias de compatibilidad. Se
aplica una identidad propia sin usar sus signos como marca del producto ni afirmar
respaldo oficial. Se permiten menciones técnicas en rutas; se conserva la procedencia.

## Reproducir desde el Mac

```sh
./build.sh github
```

Lanza las compilaciones nativas ARM64 y x64 en runners de GitHub, cada una dentro
de un contenedor privilegiado openSUSE aislado. Solo el proyecto se comparte con
el contenedor; no se accede a Parallels ni a unidades físicas del usuario.

Para regenerar la descripción localmente sin construir:

```sh
BYPSSD_ARCH=aarch64 ./build.sh prepare
BYPSSD_ARCH=x86_64 ./build.sh prepare
```

Receta: [scripts/opensuse/prepare.py](scripts/opensuse/prepare.py), configuración:
[opensuse/config.sh](opensuse/config.sh), paquetes: [opensuse/packages.txt](opensuse/packages.txt).
El ejemplo de KIWI usado como referencia está fijado al commit
`c5b6534766f9538345a899f6bf93ea8a2ce2dea2` de OSInside/kiwi-descriptions.
Los repositorios rolling no están congelados, por lo que la reproducción es
funcional y no bit a bit. Se publica el manifiesto de paquetes de cada composición.

## Validación

- Compilación y auditoría r8: correctas en ARM64 y x64 ([ejecución](https://github.com/bypssd/bypssd-os/actions/runs/43725037977)).
- SHA256 de los artefactos y de las dos ISO completas verificados antes de su entrega local.
- ARM64 r8: arranque UEFI Live hasta KDE Plasma en QEMU/HVF, con la ISO en solo lectura y sin disco duro conectado.
- x64 r8: arranque UEFI Live hasta KDE Plasma ([ejecución](https://github.com/bypssd/bypssd-os/actions/runs/43726136936)).
- Por petición de Andy, no se ha instalado la revisión r8: su comprobación final se limita al arranque Live.
- En las pruebas anteriores se verificaron la instalación ARM64, la contraseña propia del administrador, la retirada de los permisos Live y la instalación gráfica de VLC desde Discover. La configuración EFI de reserva se probó en el disco virtual de aquella instalación antes de incorporarla a r8.
- BYPSSD Updates: índices públicos vacíos y SHA256 de `primary` comprobados; refresco ZYpp correcto en ambas arquitecturas ([ejecución](https://github.com/bypssd/bypssd-os/actions/runs/43699679512)).
- Imágenes para equipos UEFI de la arquitectura correspondiente. ARM64 no implica arranque nativo en un Mac Apple Silicon ni compatibilidad con todas las placas.
- Hardware físico y Secure Boot siguen pendientes de validación.

Los logs completos de compilación quedan en artefactos de Actions durante 30 días
y se copian a `out/logs/` para las comprobaciones locales.

## Presentación durante la instalación

Cinco pantallas en español: bienvenida a Renacer; LibreOffice y Okular; navegación
con Chromium y Firefox; aplicaciones con Discover; personalización y Dolphin.
Cambian cada diez segundos, con iconos SVG propios y transiciones suaves.
La barra amarilla inferior, de 26 píxeles de alto, muestra el porcentaje real calculado por la cola de
trabajos de Calamares; debajo se indica la operación en curso. No usa una animación
que simule avances. Fuentes en `opensuse/calamares/branding/`.

La prueba completa detectó en r3 una configuración incompleta de GRUB
(`KeyError: grubInstall`). r8 define las rutas nativas de grub2-install,
grub2-mkconfig, grub2-probe y efibootmgr. r4/r5 se cancelaron para incorporar la solución.

Se fuerza el renderizado Qt Quick por software solo en el instalador mediante
un lanzador propio autorizado por Polkit. Evita zonas negras en GPU virtuales
y mantiene visibles las diapositivas, la barra real y el porcentaje.

La validación instalada detectó también el valor nativo `targetpw` de sudo.
Se configura `Defaults:%wheel !targetpw` para que el administrador utilice
su propia contraseña, manteniendo root bloqueado. El acceso directo del instalador
se retira también del escritorio del usuario creado durante la instalación.

Prueba del administrador: contraseña propia aceptada por sudo y por la instalación
gráfica de VLC. Se ha comprobado la ausencia de sudo, Polkit y autologin especiales
de Live en el destino instalado, y el refresco correcto de ambos repositorios.

La prueba de reinstalación encontró que GRUB necesitaba también su `grub.cfg`
junto al cargador de reserva `EFI/BOOT`. Un trabajo posterior a `bootloader` copia
la configuración EFI nativa a esa ruta, sin modificar los binarios del cargador.
La corrección se ha probado arrancando el mismo disco por la ruta de reserva.

La revisión r8 usa compresión Zstandard para el sistema Live: reduce el tiempo
de generación frente a XZ, a cambio de una ISO algo mayor. Es una opción
[compatible con KIWI](https://osinside.github.io/kiwi/image_description/elements.html).
Las ISO completas y sus SHA256 sirven también para publicarlas en SourceForge.

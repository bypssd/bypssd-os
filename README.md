# BYPSSD OS Renacer

Distribución para oficina y educación de BYPSSD Informática Retro (Valencia),
basada en Fedora Linux 45 y KDE Plasma 6.8.2. Identificador del sistema: `bypssd`.
Versión inicial: 1.0. Primero aarch64; x86_64 queda fuera de esta compilación.

**Estado: ISO candidata ARM64 generada, sesión live e instalación completa en disco QEMU comprobadas; arranque desde disco y acceso gráfico SDDM/Plasma validados. Pendiente de preparación para publicación.**
No se ha accedido ni modificado Parallels.

## Decisiones

- Español de España, teclado español y zona horaria Europe/Madrid.
- Amarillo #FFB800, negro #000000 y blanco #FFFFFF; tema oscuro inicial.
- LibreOffice Writer, Calc, Impress y Draw; Chromium; Okular para PDF.
- Dolphin, Konsole, Ark, Gwenview, Spectacle, impresión y ajustes del sistema.
- Sin grupos de juegos, emulación ni herramientas de restauración retro.
- Sesión en vivo con usuario temporal, inicio automático e instalador.
- Firefox también es una dependencia del instalador web oficial.
- Las credenciales del sistema instalado se definen en el instalador;
  la sesión live no debe convertirse en un usuario instalado sin contraseña.

## Estructura

- `assets/`: originales facilitados por Andy, logo a 48 y 256 píxeles y fondo.
- `src/breeze/`: único componente C++ recompilado; plugin Qt propio BYPSSD.
- `src/plasma-workspace/`: fuente estable de la pantalla de bienvenida y referencia del diseño inicial.
- `kickstart/bypssd.ks`: selección y configuración propia para Fedora 45 aarch64.
- `kickstart/upstream/`: kickstarts históricos oficiales conservados como referencia.
- `branding/`: temas, colores, configuraciones, políticas y especificaciones RPM.
- `scripts/`: preparación del entorno, fuentes, RPM y composición.
- `out/rpms/`: RPM propios y caché de RPM oficiales sin modificar.
- `out/srpms/`: código fuente empaquetado de los componentes propios y derivados.
- `out/logs/`: registros de cada intento y diagnósticos.
- `out/verification/`: verificación de la ISO oficial proporcionada por Andy.
- `build.sh`: entrada para repetir el proceso.

## Entorno del Mac

Herramientas comprobadas: Homebrew, git, Podman 6.2.0, vfkit y QEMU.
Podman y QEMU se utilizan directamente; no dependen de Parallels.

La máquina operativa es **bypssd-build**, proveedor **applehv**,
6 CPU, 8192 MiB de RAM y disco de 60 GiB. Solo se comparte este proyecto.
El contenedor privilegiado `bypssd-build-f45` usa Fedora 45 aarch64.
El modo privilegiado se limita a la VM y permite crear dispositivos loop y montar
los sistemas de archivos usados por livemedia-creator; no da acceso al disco del Mac.

El disco de trabajo de la imagen se crea dentro del contenedor, sobre el disco
Linux de la VM, no sobre la carpeta compartida del Mac.

Los primeros intentos (`bypssd-builder`, libkrun, y `bypssd-applehv`) se conservan
para diagnóstico. El primer arranque llegó a funcionar, pero la máquina desapareció
al cerrar la ejecución que la lanzó; un segundo arranque cayó en Ignition con:
`useradd: cannot lock /etc/group; try again later.`
Referencia: https://github.com/podman-container-tools/podman/issues/28439
No se ha demostrado que cambiar solo de proveedor resuelva esa incidencia.

La máquina operativa se creó desde cero y su primer arranque se realizó mediante
un servicio temporal de usuario `com.bypssd.builder`, para sobrevivir al cierre
de la ejecución. Su plist y su script están dentro de `scripts/`, no se han
instalado en Library/LaunchAgents y no se ha usado sudo.

## Repetir la compilación

Desde `/Users/andy/BYPSSD-OS`:

```sh
./build.sh all
```

Etapas disponibles:

```sh
./build.sh env      # comprobar/arrancar VM, contenedor y dependencias Linux
./build.sh rpms     # fuentes fijadas y generación completa de RPM + SRPM
./build.sh iso      # componer usando el repositorio de RPM ya preparado
```

Requisitos previos del Mac, si se prepara otro equipo:

```sh
brew install git podman vfkit qemu
```

El script falla ante errores; no elimina ni recrea máquinas existentes.
No usar `bypssd.ks` para instalar directamente un equipo: sus instrucciones de
particionado son para el disco de imagen del proceso de composición.
La instalación desde el escritorio live utiliza el instalador interactivo.

La reproducción es funcional, no una garantía de ISO idéntica bit a bit:
las fuentes KDE están fijadas, pero los repositorios de actualizaciones de Fedora
pueden cambiar y las imágenes base pueden recibir actualizaciones. Para congelar
una edición pública deben conservarse el manifiesto, todos los RPM y sus fuentes.

## Fuentes fijadas y alcance de la recompilación

| Repositorio | Etiqueta | Commit |
|---|---|---|
| https://invent.kde.org/plasma/breeze | v6.8.2 | c97883a8fe41bce774835c25d7f7e321c71fa618 |
| https://invent.kde.org/plasma/plasma-workspace | v6.8.2 | 30beb0095873364c6b34ebcfd292ecafd4db7f61 |

Breeze se compila con Qt 6, sin Qt 5, cursores, decoraciones, fondos ni pruebas de
upstream. Solo se construye el objetivo del estilo y se empaqueta el plugin
`/usr/lib64/qt6/plugins/styles/bypssdstyle6.so`, seleccionable como `BYPSSD`.
No se reemplaza el plugin oficial Breeze. El parche está en
`branding/breeze-bypssd.patch`; el script de preparación aplica los cambios de forma idempotente.

La pantalla de bienvenida deriva del QML de Plasma Workspace. Es código
interpretado: se empaqueta su fuente adaptada, sin recompilar todo Plasma.
El tema SDDM es propio y utiliza el SDDM oficial de Fedora; no requiere clonar otro
repositorio. Los demás componentes KDE se instalan desde los RPM oficiales.

## Cambios de marca

| Superficie | Implementación |
|---|---|
| Nombre del sistema | `bypssd-release-identity` proporciona `/usr/lib/os-release` con ID `bypssd` |
| Dependencias de Fedora | Se conserva `fedora-release-common` sin editar y se proporcionan las capacidades de identidad/variante que necesita |
| Repositorios | `/etc/dnf/vars/releasever` fija 45, aunque VERSION_ID del producto sea 1.0 |
| Tema global | `com.bypssd.desktop`, colores BYPSSDRenacer y estilo Qt BYPSSD |
| Fondo | `assets/wallpaper.png`, generado con image_gen; modo de ajuste completo para evitar recortes en pantallas 16:10 |
| Menú y panel | Logo BYPSSD, accesos a Chromium y LibreOffice mediante el diseño inicial del tema global |
| Bienvenida de sesión | QML derivado de Plasma Workspace con imágenes y nombre BYPSSD |
| SDDM | Tema `bypssd` con fondo, logo y textos en español |
| Plymouth | Tema `bypssd`, configurado con `plymouth-set-default-theme` |
| Acerca del sistema | Configuración inicial de usuario `kcm-about-distrorc` con nombre, versión, web y logo BYPSSD |
| Instalador | Perfil Anaconda para ID `bypssd`, estilo propio y lanzador que usa el punto de extensión LIVECMD de liveinst para fijar el nombre BYPSSD, sin editar system-release |
| Consola de login | agetty se configura con `--noissue` para no mostrar la cabecera de la distribución base |
| Arranque ISO | Nombre BYPSSD OS, etiqueta BYPSSD y metadatos KIWI propios; el script alternativo de livemedia-creator conserva `--project "BYPSSD OS" --volid BYPSSD` |

No se han editado archivos propiedad de `fedora-release-common` ni binarios
oficiales. Se sustituye el paquete de identidad, no el paquete común de release.
El paquete propio satisface exactamente la versión de identidad requerida por
`fedora-release-common`; una futura actualización de ese paquete puede exigir
reconstruir el paquete de identidad BYPSSD.

La ruta técnica UEFI `EFI/fedora` se conserva para ser compatible con los
cargadores firmados oficiales y sus actualizaciones. No es el nombre visible del
sistema. No se ha validado Secure Boot en hardware real.

Los logos originales se conservan, y las variantes de 48 y 256 píxeles son
redimensionados deterministas. La mascota y el logotipo horizontal se incluyen
como recursos, sin convertirlos en un elemento obligatorio del escritorio.
El prompt completo del fondo está en `assets/wallpaper-prompt.txt`.

## Origen del kickstart

Fedora ha retirado fedora-kickstarts y migrado sus definiciones actuales a KIWI.
Referencia: https://forge.fedoraproject.org/releng/spin-kickstarts

Se conserva el último árbol anterior a su retirada:
`d93b2accc04f9dfae72d9d6272a66cfb69df0d00`.
`bypssd.ks` adapta `fedora-live-kde.ks`, `fedora-live-kde-base.ks`,
`fedora-kde-common.ks` y `fedora-live-base.ks`, con selección explícita y ligera
para oficina en vez del grupo completo del escritorio con todas sus aplicaciones.
No hereda el repositorio Rawhide de ese árbol histórico.

La composición final usa KIWI 11.1.1 dentro del contenedor. Se conserva también el script de livemedia-creator 45.4 como diagnóstico; Anaconda no llegó a completar la composición en ese entorno. El repositorio de
actualizaciones tiene el identificador `bypssd-fedora-updates` porque Anaconda
puede desactivar automáticamente el identificador especial `updates`.
El intento de livemedia-creator sirve los RPM solo en 127.0.0.1:8765. KIWI accede directamente al repositorio local de RPM del proyecto.

## Validaciones realizadas

- Fedora 45 y aarch64 comprobados dentro del contenedor operativo.
- Etiquetas y commits estables de KDE fijados y registrados.
- Estilo C++ compilado y cargado mediante QStyleFactory, con resultado 0.
- RPM y SRPM generados por rpmbuild completo, sin short-circuit en los entregables.
- Sintaxis QML comprobada con qmlformat.
- Kickstart validado por ksvalidator F45.
- Selección de paquetes resuelta por DNF 5, sin omitir errores de dependencias.
- ISO final híbrida UEFI aarch64 con volumen BYPSSD y checksum SHA256 comprobado desde el Mac.
- Arranque del kernel, sesión live automática y escritorio Plasma final verificados en QEMU con SELinux estricto.
- Revisión visual final: fondo completo sin recorte, logo propio y accesos a Chromium y LibreOffice. Captura: `out/qemu-test/final-live-desktop.png`.
- Instalación completa con Anaconda en un disco QEMU de 24 GiB, UEFI, EFI + ext4 + Btrfs. Registro: `out/logs/qemu-install-interactive.log`.
- Arranque del disco instalado sin conectar la ISO; identidad BYPSSD correcta y SELinux Enforcing.
- Usuario de laboratorio creado, autenticación SDDM propia y sesión Plasma Wayland correctas. El usuario liveuser y su autologin no quedan instalados.
- Idioma es_ES.UTF-8 y versiones de Chromium y LibreOffice comprobados en el sistema instalado.
- Okular 26.08.2 comprobado con QT_QPA_PLATFORM=offscreen. La consulta inicial sin display falló; ambos resultados se conservan.
- Segundo arranque del disco: graphical.target, SDDM activo y SELinux Enforcing; sin autologin.
- No se detectaron unidades systemd fallidas en el arranque instalado. Capturas: `out/qemu-test/installed-sddm.png` e `installed-desktop.png`.
- La instalación completa se probó con la interfaz de texto. En branding 1.0-4 se abrió el lanzador real como liveuser y se comprobó la bienvenida gráfica web: título BYPSSD, logo, cabecera amarilla, botones y español. Captura: `out/qemu-test/anaconda-bypssd-4.png`.
- No se ha repetido una instalación completa con la interfaz web ni validado Secure Boot. El lanzador oficial pone temporalmente SELinux en permisivo durante Anaconda; se restauró Enforcing antes de apagar esta prueba.

Los fallos y sus registros se conservan. Se corrigieron una ruta de instalación
del plugin, nodos loop ausentes en el contenedor, la exclusión especial de updates
y conflictos de configuración con Plymouth/kde-settings. Los archivos de
configuración de paquetes ajenos no se fuerzan con `--replacefiles`.

## Ruta de construcción KIWI

`kickstart/kiwi/BYPSSD.kiwi` se genera desde la selección del kickstart mediante
`scripts/prepare-kiwi.py`. Usa el mismo postprocesado y plantillas UEFI adaptadas
de fedora-kiwi-descriptions, commit `4aec82eba1e440cefd40bb1ea79ebcbe3bd3b71c`.
Se han traducido las entradas del menú y retirado su clase visual Fedora.
La etiqueta ISO sigue siendo BYPSSD. El sistema live usa EROFS, como las imágenes
actuales de Fedora, y el instalador sigue siendo el Anaconda oficial.

KIWI construye sobre un volumen ext4 de trabajo de 24 GiB dentro de la VM,
incluidos todos sus temporales; no se usa el overlay del contenedor para el árbol
final, porque su montaje con contexto SELinux fijo impide reetiquetar archivos.
La máquina CoreOS de Podman es de una versión anterior al sistema destino.
`build.sh` pone temporalmente SELinux de esa VM en modo permisivo y restaura su
estado inicial al acabar. La imagen BYPSSD conserva SELINUX=enforcing.

Los intentos de Anaconda se detuvieron por archivos de configuración en conflicto,
estado persistente en /run y procesos de sus módulos que salían con código 132.
No se parchearon sus binarios ni se continuó tras ignorar fallos.

## ISO oficial aportada por Andy

Archivo intacto:
`/Users/andy/Downloads/Fedora-KDE-Desktop-Live-45-1.4.aarch64.iso`.
SHA256:
`46a73d4c0a82a77551311ab1589255ecac51b5ce311b4fc84577f5ede5a44f5c`.

Coincide con el checksum oficial firmado. GPG informó de firma válida con la clave
Fedora 45 `4F50A6114CD5C6976A7F1179655A4B02F577861E`, descargada del sitio oficial.
La verificación usa un llavero exclusivo en `out/verification/gnupg`, sin tocar
el llavero personal. Esta ISO no es la ISO de BYPSSD.

## Publicación, marcas y licencias

**No se ha publicado ninguna imagen ni se declara esta edición lista para publicar.**

Se revisaron estas fuentes oficiales el 14 de noviembre de 2026:

- Fedora Trademark Guidelines: https://docs.fedoraproject.org/en-US/legal/trademarks/
- Fuente oficial consultada, ante el bloqueo de la web:
  https://gitlab.com/fedora/legal/fedora-legal-docs/-/blob/main/modules/ROOT/pages/trademarks.adoc
- KDE Logo y condiciones de uso: https://kde.org/stuff/clipart/
- Guía de marca KDE: https://community.kde.org/Promo/Guidance/Branding

Las copias de referencia están en `branding/policies/`; conservan su licencia de
origen y no forman parte de los RPM de branding.

BYPSSD no se presenta como una edición oficial ni como un producto avalado por
Fedora, Red Hat o KDE e.V. El logo KDE no se usa como logo de BYPSSD.
Se conservan avisos de autoría y licencias de los componentes derivados.

La eliminación absoluta de cualquier nombre o logo KDE/Fedora de todos los
menús, ayudas, créditos, listados de paquetes y aplicaciones oficiales **no está
cumplida**. Conservar los binarios oficiales implica conservar sus funciones de
créditos y sus identificadores. La identidad principal se personaliza mediante
temas y configuración; las aplicaciones y repositorios requieren una auditoría
visual adicional. No se ocultan avisos legales o de autoría.

Las directrices de Fedora para el uso de la marca Remix describen condiciones
adicionales sobre paquetes de release y avisos. Como este proyecto conserva
`fedora-release-common` por requisito técnico, no se asume que pueda usar esa marca.
Antes de distribuir públicamente debe cerrarse la revisión de marca para el
producto con nombre propio y el alcance exacto de las referencias técnicas.

Para publicar faltan, además de las pruebas técnicas:

1. Auditoría visual completa y decisión documentada sobre las referencias a upstream.
2. Confirmación de derechos y licencia de distribución del kit de marca BYPSSD.
3. Disponibilidad del código fuente correspondiente de los componentes distribuidos,
   no solo de los RPM propios. Los SRPM propios ya están en `out/srpms/`.
4. Firma de RPM y checksum/ISO con una clave de publicación de BYPSSD;
   los paquetes de desarrollo locales no están firmados.
5. Política de actualizaciones, soporte y mantenimiento de la identidad de release.
6. Pruebas en cada familia ARM64 anunciada. Una ISO UEFI aarch64 no garantiza
   soporte para cualquier placa ARM, Raspberry Pi o instalación nativa en Apple Silicon.

## Parar el entorno dedicado

Cuando no haya compilaciones en curso:

```sh
podman --connection bypssd-build-root stop bypssd-build-f45
CONTAINERS_MACHINE_PROVIDER=applehv podman machine stop bypssd-build
launchctl bootout gui/$(id -u)/com.bypssd.builder
```

No usar `podman machine reset`, que afectaría a máquinas ajenas al proyecto.

## Pruebas desechables con QEMU

`scripts/test-qemu.sh` usa una VM ARM64 con aceleración HVF, 4 CPU y 4 GiB de RAM.
Solo conecta la ISO y `out/qemu-test/install.qcow2`; no comparte carpetas del Mac
ni conecta discos físicos. Los archivos vars.fd y qcow2 son exclusivos de prueba.

`out/qemu-test/install-test.ks` contiene una configuración destructiva limitada al
disco virtual vda y una cuenta de laboratorio. No se incluye en la ISO ni debe
usarse en un equipo real. `scripts/test-live-install.py` automatiza esa prueba
por consola y conserva sus registros. Anaconda live ignora el kickstart pasado
por argumento; el arnés carga sus valores en interactive-defaults.ks únicamente
en la memoria de la VM de prueba y confirma el disco por su interfaz de texto.
El intento con --cmdline se detuvo porque el destino requiere confirmación; no
era un fallo de detección del disco. No se modifica la ISO para hacer esta prueba.

El ensayo inicial de texto eligió multi-user.target; se activó graphical.target
solo en el disco de laboratorio para probar SDDM. El kickstart de ensayo ya
explicita xconfig --startxonboot para repeticiones. Esto no altera la ISO, cuyo
modo live es gráfico. La contraseña de laboratorio nunca es una cuenta de la ISO.

Las capturas de la primera candidata están en out/qemu-test/. La auditoría visual
identificó el recorte del fondo en 16:10 y Firefox en el panel; la revisión de
branding 1.0-3 corrige ambos y añade el lanzador de instalación de marca propia.


## Entregables de esta compilación

- ISO: `out/BYPSSD-OS-Renacer-1.0-aarch64.iso` (1.702.719.488 bytes).
- SHA256: `38994637d25b347b87dd3393650b41027cc017584bd1451e2559526308ad4937`.
- Verificación: `cd out && shasum -a 256 -c BYPSSD-OS-Renacer-1.0-aarch64.iso.sha256`.
- Procedencia y hashes: `out/build-manifest.json`; paquetes: `out/package-manifest.txt`.
- Branding final: bypssd-branding 1.0-4.fc45; estilo 6.8.2-1.fc45; identidad 1.0-1.fc45.
- Candidata anterior archivada en `out/archive/candidate-1/`, no confundir con la ISO final.

La VM de compilación y el entorno de prueba se dejan parados al terminar para
liberar memoria. No se ha instalado el sistema en el Mac ni en Parallels.

## Revisión rápida de branding 1.0-4

Se añaden logo/cabecera propios para Anaconda GTK, branding completo de recursos
para Cockpit bajo ID bypssd, título de instalación y etiquetas BYPSSD en DNF 5.
El alcance exacto y las referencias que permanecen están en
[docs/REFERENCIAS-DE-MARCA.md](docs/REFERENCIAS-DE-MARCA.md). No se declara borrado
absoluto de Fedora ni se han reescrito binarios, firmas o créditos originales.

El repositorio sin VPS está preparado y explicado en
[docs/REPOSITORIO-GITHUB.md](docs/REPOSITORIO-GITHUB.md). La demostración local
usa un nombre ficticio y permanece deshabilitada al no estar firmada. No hay
repositorio real publicado ni claves privadas generadas.

# BYPSSD OS Renacer 1.1

Entrega local verificada el 17 de noviembre de 2026 (r16):
`iso_final/BYPSSD-OS_Renacer_arm64.iso` y
`iso_final/BYPSSD-OS_Renacer_x86_64.iso`, con sus archivos `.sha256`.
Los detalles de integridad y pruebas están en `iso_final/verification.json`.
Las ISO se generaron el 16 de noviembre y se comprobaron instaladas el 17;
no se publican como Releases de GitHub. Están listas para subir a SourceForge.


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
- Revisión actual: r16, con reinicio corregido, menús comprobados visualmente, sonidos y sesión Live sin bloqueo.

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

## Revisión r10: correcciones de instalación e inicio de sesión

La fotografía del error x64 mostró que `/boot/efi/EFI/BYPSSD/grub.cfg` no existía.
El trabajo final de Calamares conserva ese fichero cuando GRUB lo proporciona;
si falta, genera una configuración usando el UUID y la ruta real de GRUB y la
copia también a `EFI/BOOT/grub.cfg`. Ambas ramas se han comprobado con las
herramientas GRUB nativas sobre sistemas de archivos de prueba en las dos arquitecturas.
Compilación y auditoría r10 correctas: ejecución 43755582221.

SDDM incluye una presentación oscura con amarillo BYPSSD, selector de las cuentas
existentes y selección inicial de la última cuenta. Solo hay que introducir su
contraseña. No se incorporan cuentas personales de prueba a la distribución.

El acceso propio a instalar se elimina del menú y del escritorio tras la
instalación. Las entradas genéricas de Calamares se ocultan mediante archivos
XDG en `/usr/local/share/applications`, sin editar los archivos oficiales.
En Live se mantiene el lanzador propio de BYPSSD.

Destino de entrega: `iso_final/aquilas.iso` (x86_64) y
`iso_final/aquilas-arm64.iso` (aarch64), con un `.sha256` junto a cada ISO.
No se publican ISO en Releases de GitHub. Las comprobaciones finales de esta
revisión son de arranque Live; no se realiza una instalación nueva ni se usa Parallels.

Entrega r10 verificada el 15 de noviembre de 2026: SHA256 de ambas ISO
comprobados nuevamente tras la descarga. Arranque UEFI Live hasta el escritorio
KDE confirmado en ARM64 (QEMU/HVF local, sin disco) y x64 (Actions 43756813345).
Capturas locales: `out/qemu-r10-live-only/final.png` y
`out/r10-x64-boot/desktop-preview.png`. Los registros de las pruebas nativas
EFI y de SDDM están en `out/logs/r10-native/`, con auditorías sin errores.

## Revisión r11: reinicio, menú instalado y sonidos

- Calamares ofrece reiniciar al terminar y usa `systemctl --no-block -i reboot`.
- El initramfs Live incorpora un hook de apagado propio. Tras liberar el sistema
  Live, expulsa el CD cuando existe, muestra «Please remove the installation media,
  and then press enter» y espera Enter antes de reiniciar. El hook solo actúa con
  `rd.live.image` y durante un reinicio; no se activa al reiniciar un sistema instalado.
- El lanzador propio se guarda como plantilla y solo se crea en la capa temporal
  Live. No se incluye en el árbol de aplicaciones que copia Calamares.
- La limpieza del destino oculta lanzadores genéricos mediante XDG, retira accesos
  personales y cachés de menú y elimina los permisos y autologin de Live.
- Se incluyen `ocean-sound-theme6`, `oxygen6-sounds`, `plasma6-pa` y
  `pipewire-pulseaudio`. Ocean queda seleccionado con sonidos habilitados.
- `scripts/opensuse/check-installed.py` comprueba el sistema arrancado desde su
  disco. El flujo `qa-installed.yml` instala en un disco QEMU desechable y comprueba
  el aviso de retirada del medio, el inicio desde disco y los sonidos en Ajustes.
- Las pruebas no utilizan Parallels. Las cuentas y accesos de diagnóstico solo
  existen en las máquinas de prueba y no forman parte de las ISO.

### Corrección adicional r12 del reinicio Live

La prueba instalada de x64 detectó que r11 no mostraba el aviso: el sistema Live
conservaba `/boot/initrd` apuntando a un fichero ausente. Aunque el hook estaba
en el initramfs del medio, dracut no podía recuperarlo al apagar.
La preparación de Live enlaza ahora `/boot/initrd-$(uname -r)` con el initramfs
real del CD/USB, en `/run/overlay/live/boot/$(uname -m)/loader/initrd`. El enlace
se crea exclusivamente en la capa temporal Live, y no se copia al destino.
En la comprobación ARM64 el aviso se mantuvo visible hasta pulsar Enter y el
equipo arrancó desde el disco instalado después de retirar el CD virtual.

## Revisión r14: bloqueo Live y accesos de superusuario

Solo la cuenta temporal `linux` recibe `Autolock=false`, `LockOnResume=false`,
`LockOnStart=false` y `RequirePassword=false` en su `kscreenlockerrc`. Estos
ajustes no se guardan en `/etc/skel` ni en la configuración global y no se
copian a las cuentas del sistema instalado. Calamares se ejecuta bajo una
inhibición de `idle:sleep`, que se libera al cerrar el instalador.

Los lanzadores de gestor de archivos y terminal como superusuario se ocultan
mediante entradas XDG `Hidden=true` en `/usr/local/share/applications`, tanto
en Live como en el destino. Se conservan los lanzadores normales y los archivos
oficiales de los paquetes. El informe queda en
`/var/lib/bypssd/hidden-admin-launchers.json`. La prueba instalada comprueba
además que los ajustes sin bloqueo de Live no se heredan.

La prueba x64 deja Calamares abierto sin actividad durante 330 segundos,
más que el bloqueo predeterminado de cinco minutos, y consulta por D-Bus
que la sesión permanezca desbloqueada antes de continuar la instalación.

## Revisión final r15: coherencia del sistema instalado y consola de reinicio

Calamares genera `/etc/default/grub` con `overwrite: true` y parámetros
derivados del destino. Así no hereda `rd.live.image` ni otros argumentos de
la sesión temporal. Se fija la ruta existente del tema en
`/usr/share/grub2/themes/bypssd/theme.txt` y se usa la terminal gráfica de GRUB.

Los diálogos comunes incluyen `qt6-translations`, `kf6-kcmutils-lang` y las
traducciones de `libKF6KCMUtils6`, `libKF6ConfigWidgets6`, `libKF6WidgetsAddons6`
y `libKF6XmlGui6`. Se comprobó la interfaz de sonidos con «Océano» y «Oxígeno»
y botones en español, reproducción con salida PCM real e instalación de VLC
desde Discover con la contraseña del administrador normal.

La URL antigua de BYPSSD Updates quedó inutilizable por la redirección de Pages
y la desaparición de sus metadatos. El repositorio vacío se sirve ahora desde
`https://raw.githubusercontent.com/bypssd/bypssd-os/main/repo/tumbleweed/$basearch/updates/`.
Se mantienen las comprobaciones de firmas de paquetes. Su refresco se comprueba
en las dos compilaciones nativas, sin cambiar la web o el dominio personalizado.

En x64, la consola gráfica podía quedar negra al apagar. El hook usa ahora
`chvt 1`, normaliza el terminal y escribe/lee en `/dev/tty1` (o en la consola
si no existe). Las órdenes de expulsión del CD y salida de Plymouth tienen
un tiempo máximo. La prueba específica 43935354088 confirmó el aviso visible
y la espera de Enter; es un diagnóstico de reinicio Live, no una prueba completa
de instalación. La validación completa se registra aparte.

## Revisión r16: ocultación efectiva de los accesos del menú

La revisión visual detectó que los pequeños archivos globales `Hidden=true`
no bastaban: los accesos SU todavía aparecían en Live aunque la auditoría de
archivos los consideraba ocultos. Se sustituyen por copias completas de las
entradas, con `NoDisplay=true`, tanto globalmente como en
`/etc/skel/.local/share/applications/`. Así cada cuenta Live o instalada recibe
las entradas válidas que KDE lee con prioridad. Los archivos oficiales no se editan.

Se ocultan `konsolesu.desktop`, `org.kde.dolphinsu.desktop` y la entrada genérica
`calamares.desktop`. El lanzador propio BYPSSD se crea solo en Live y se retira
del destino. La limpieza conserva las entradas NoDisplay, y las pruebas revisan
el menú real mediante capturas y OCR antes y después de instalar.

Compilación r16: ejecución 43948175754, fuente afdbd44. Prueba completa x64
43950440698: correcta, con 330 segundos de inactividad sin bloqueo, aviso de
retirada del medio, arranque instalado, auditoría sin errores, temas Ocean/Oxygen
y salida de audio PCM comprobada. Los ajustes sin contraseña de Live no se
heredan en el sistema instalado. La validación local ARM64 y sus capturas se
conservan en `out/qemu-r16-installed/` y `out/logs/`.

### Verificación final r16 — 17 de noviembre de 2026

- ARM64: instalación completa en disco QEMU/HVF exclusivo del proyecto, aviso
  visible al reiniciar, retirada del CD, acceso al escritorio instalado y
  auditoría sin errores. Servicios de audio activos y salida PCM con pico 23233.
- x64: ejecución 43950440698 correcta, con 330 segundos reales sin bloqueo en
  Live, comprobación visual del menú antes y después de instalar, aviso de
  retirada del medio, inicio desde disco, temas de sonidos y audio PCM correcto.
- El sistema instalado conserva el bloqueo normal y no hereda el autologin ni
  las autorizaciones especiales de Live. Las cuentas de QA no están en las ISO.
- Los originales anteriores de `iso_final/` se conservaron en
  `out/archive/before-r16-20261117/`. Se retiraron las copias temporales de
  entrega de Actions; se conservan logs y paquetes BYPSSD. Parallels no se utilizó.
- Pruebas realizadas en QEMU; la validación de hardware físico y Secure Boot
  continúa pendiente.


### NextWindow opcional para HP TouchSmart (18 de noviembre de 2026)

- Se ha añadido `opensuse/nextwindow/`: fuentes GPL fijadas al commit upstream
  `5fda7859cf07d99cd23ac1c842643411d780e7ae`, decodificadores originales Intel
  de 32 bits con licencia NextWindow MIT, integración RPM y servicios optativos.
- El módulo produce eventos direct-touch multitáctiles tipo B para libinput/KDE;
  no instala el driver Xorg antiguo ni cambia la sesión. No hay versión ARM64.
- El workflow `nextwindow.yml` comprueba compilación real con cabeceras
  Tumbleweed, carga de ambos ELF32, dependencias RPM y unidades systemd.
- El módulo se compila para el kernel arrancado al activar y en próximos
  arranques. Requiere cabeceras coincidentes. Secure Boot activo requiere un
  procedimiento de firma aparte: el paquete no cambia firmware ni genera claves.
- No modifica las ISO r16 entregadas ni habilita el controlador en otros equipos.
  El paquete es experimental: falta confirmar USB VID/PID y respuesta táctil en
  el HP físico. No se incorpora aún al canal general de actualizaciones.
- Instrucciones: `opensuse/nextwindow/README.md`. Instalar el RPM en el equipo ya
  instalado permite probarlo sin reinstalar ni modificar archivos personales.


### Actualización instalada r17 preparada (18 de noviembre de 2026)

- RPM `bypssd-branding-1.1-17` y `bypssd-nextwindow-0.7.0.1-2` compilados sin
  reconstruir las ISO. Módulos 7.3.3/7.3.4 incluidos; autodetección del USB validado.
- Chromium usa renderizado software/XWayland solo en Radeon antigua activa;
  AMDGPU moderno conserva aceleración. Paquetes Mesa/RADV/firmware oficiales.
- Pruebas: actualización real ARM64 r16→r17, dependencia x64 en contenedor,
  nueve casos de selección gráfica y captura Chromium con sandbox activo.
  La corrección visual en AMD física queda pendiente de confirmación.
- Entrega revisable: `out/updates/r17/`; logs: `out/logs/nextwindow/`.
- **No publicada en el canal activo**: la revisión automática rechazó crear una
  clave privada de firma sin autorización explícita. No se ha creado ninguna
  clave ni se han desactivado verificaciones. Se espera autorización para firmar
  y publicar los RPM y metadatos preparados.
- Los equipos deberán confiar una vez en la clave pública y actualizar mediante
  Discover o zypper; no requieren reinstalación ni otra ISO.

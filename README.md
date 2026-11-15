# BYPSSD OS Renacer · migración a openSUSE

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
- [Releases](https://github.com/bypssd/bypssd-os/releases). La nueva candidata se
  llama `renacer-1.1-opensuse-r3` (ambas arquitecturas publicadas). La revisión r6
  añade cinco diapositivas, barra con porcentaje real y correcciones del instalador; está en compilación.
- Canal propio [BYPSSD Updates](https://bypssd.github.io/bypssd-os/), inicialmente
  vacío, con índices RPM válidos para ambas arquitecturas.

Las ISO completas superan el límite de 2 GiB por archivo de GitHub Releases. Se
publican en dos partes por arquitectura, con checksums individuales y de la ISO.
Para descargarlas y reconstruir la imagen sin guardar copias adicionales:

```sh
python3 scripts/download-opensuse-iso.py aarch64
python3 scripts/download-opensuse-iso.py x86_64
```

El resultado en `out/` es una ISO completa; las partes sueltas no se pueden arrancar.

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

- Herramientas nativas: KIWI 10.3.11 y paquetes Discover/ZYpp/Calamares disponibles.
- Índices públicos BYPSSD Updates: conteo cero y SHA256 de `primary` comprobados.
- Refresco con ZYpp nativo: correcto en ARM64 y x64 ([ejecución](https://github.com/bypssd/bypssd-os/actions/runs/43699679512)).
- Compilación r3: correcta en ambas arquitecturas ([ejecución](https://github.com/bypssd/bypssd-os/actions/runs/43704624342)).
- Arranque UEFI x64 r3: escritorio KDE y sesión automática comprobados ([ejecución](https://github.com/bypssd/bypssd-os/actions/runs/43706493860)).
- ARM64 r3: arranque UEFI, sesión automática y entrada de teclado comprobados en QEMU/HVF.
- Discover: instalación gráfica de VLC como usuario Live sin privilegios en r1 con las correcciones incorporadas en r3; transacción PackageKit de 12,95 s, paquete oficial aarch64.
- Instalación completa ARM64 UEFI: finalizada sobre el disco virtual de 32 GiB usando r3 con la configuración GRUB y presentación corregidas. Arranque del disco instalado: en comprobación.
- Secure Boot y equipos físicos requieren validación aparte.

Los logs completos de compilación quedan en artefactos de Actions durante 30 días
y se copian a `out/logs/` para las comprobaciones locales.

## Presentación durante la instalación

Cinco pantallas en español: bienvenida a Renacer; LibreOffice y Okular; navegación
con Chromium y Firefox; aplicaciones con Discover; personalización y Dolphin.
Cambian cada diez segundos, con iconos SVG propios y transiciones suaves.
La barra amarilla inferior muestra el porcentaje real calculado por la cola de
trabajos de Calamares; debajo se indica la operación en curso. No usa una animación
que simule avances. Fuentes en `opensuse/calamares/branding/`.

La prueba completa detectó en r3 una configuración incompleta de GRUB
(`KeyError: grubInstall`). r6 define las rutas nativas de grub2-install,
grub2-mkconfig, grub2-probe y efibootmgr. r4/r5 se cancelaron para incorporar la solución.

Se fuerza el renderizado Qt Quick por software solo en el instalador mediante
un lanzador propio autorizado por Polkit. Evita zonas negras en GPU virtuales
y mantiene visibles las diapositivas, la barra real y el porcentaje.

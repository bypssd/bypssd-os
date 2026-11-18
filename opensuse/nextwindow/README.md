# BYPSSD NextWindow (experimental, x86_64)

Paquete opcional para probar los controladores NextWindow Fermi en BYPSSD OS
basado en openSUSE Tumbleweed. El nombre HP TouchSmart 520 no identifica por sí
solo el controlador USB: comprobar `lsusb` en el HP. No se ha probado aún en ese
hardware y no se promete compatibilidad de todas sus variantes.

El módulo GPL se adapta a eventos multitáctiles tipo B, INPUT_PROP_DIRECT,
BTN_TOUCH y libinput; no se instala el antiguo módulo Xorg ni se cambia la
sesión KDE/SDDM. El decodificador original Intel 32 bits se conserva con su
licencia MIT. No es compatible con ARM64. El paquete no activa el módulo ni
habilita servicios durante su instalación.

## Paquete experimental comprobado

Paquete: https://github.com/bypssd/bypssd-os/releases/tag/nextwindow-0.7.0.1-r1-experimental

Compilación validada: Actions 44262462023, cabeceras 7.3.4-1-default, instalación
real de dependencias RPM, ambos decodificadores ELF32 y unidades systemd correctas.

## Instalación sin reinstalar

1. Descargar el RPM y su SHA256 del artefacto del workflow NextWindow.
2. Comprobar SHA256. Los RPM experimentales no tienen firma de producción:
   revisarlos antes de aceptar la advertencia de firma de zypper. El canal
   normal BYPSSD conserva `pkg_gpgcheck=1`; no se desactiva.
3. En BYPSSD del HP: `sudo zypper install kernel-default kernel-default-devel ./bypssd-nextwindow-0.7.0.1-1.x86_64.rpm`.
   Instala también las cabeceras y dependencias de compilación/32 bits.
4. Si el kernel de las cabeceras difiere del activo, reiniciar y arrancar ese
   kernel primero. `sudo bypssd-nextwindow-enable` compila para `uname -r`,
   carga el módulo y habilita su reconstrucción en próximos arranques.
5. Tocar la pantalla y comprobar `sudo libinput debug-events`. Puede ser
   necesario cerrar sesión para que KWin detecte un dispositivo nuevo.

Secure Boot: se rechaza la activación de módulos sin firma cuando está activo.
No se generan claves ni se modifica el firmware. La firma/inscripción de una
clave MOK existente requiere un procedimiento aparte antes de usarlo así.

## Prueba temporal en el Live r16 x64

La ISO r16 arranca `7.3.3-1-default`. Instalar las cabeceras más recientes no
proporciona las de ese kernel: reiniciar el Live tampoco lo cambia. Si ya está
instalado este RPM, para obtener las cabeceras exactas oficiales:

```bash
sudo zypper install --oldpackage \
  https://download.opensuse.org/tumbleweed/repo/oss/noarch/kernel-devel-7.3.3-1.1.noarch.rpm \
  https://download.opensuse.org/tumbleweed/repo/oss/x86_64/kernel-default-devel-7.3.3-1.1.x86_64.rpm
sudo bypssd-nextwindow-enable
```

Ejecutar solo si `uname -r` devuelve `7.3.3-1-default` y la arquitectura es x86_64.
No reiniciar: los cambios Live son temporales. Estas URL son de upstream y pueden
caducar cuando rote el repositorio. El workflow `target=live-r16` conserva el
módulo precompilado y comprueba su vermagic exacto para poder distribuirlo aparte.

## Actualizaciones y diagnóstico

El servicio compila de nuevo para el kernel arrancado. Deben conservarse gcc,
make y las cabeceras exactas de ese kernel; no promete compatibilidad con futuros
cambios de API. Si falla la compilación, no elimina el módulo anterior. El resto
del sistema sigue funcionando con teclado/ratón.

`sudo bypssd-nextwindow-diagnose > nextwindow-diagnostico.txt` recopila datos
sin cambiar configuración. Revisar el archivo antes de compartirlo.

No se añaden usuarios al grupo input, no se abre hidraw al mundo y no se
inhabilitan hid-generic/hid-multitouch. Los servicios se activan por dispositivo;
fwprod solo para IDs 1926:1846, 1926:1875 y 1926:1878 según upstream.

## Desactivar

`sudo systemctl disable --now bypssd-nextwindow.service` evita reconstrucciones.
`sudo zypper remove bypssd-nextwindow` retira el paquete. Antes de eliminarlo,
parar las instancias `nwfermi@*.service` / `fwprod-*.service` que muestre el
diagnóstico y descargar `sudo modprobe -r nw-fermi` si no está en uso. Los módulos
compilados se conservan en `/lib/modules/<kernel>/updates/bypssd/`; para una
retirada completa eliminarlos explícitamente y ejecutar `sudo depmod -a` antes
de reiniciar. No se tocan otros controladores ni datos personales.

## Compilación

Workflow `.github/workflows/nextwindow.yml`: RPM y SRPM, carga de ambos ELF de
32 bits y compilación real del módulo contra las cabeceras Tumbleweed. Guarda
RPM/SRPM, fuentes, hashes y log. No construye ni publica ISO y no incorpora un
controlador experimental al canal general antes de la prueba física en el HP.

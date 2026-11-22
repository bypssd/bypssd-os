# NextWindow para Fedora 45 x64

Paquete específico de Fedora, independiente del repositorio openSUSE/BYPSSD OS.
Incluye módulos para los tres últimos kernels F45 publicados como estables en
Bodhi a 22 de noviembre de 2026: 7.3.4-300.fc45.x86_64,
7.3.3-300.fc45.x86_64 y 7.2.15-300.fc45.x86_64.

La fuente del controlador y los decodificadores son los mismos que en BYPSSD:
GPL-2.0-only para el módulo y MIT NextWindow para los binarios Intel32. Los
servicios usan libinput sin cambiar la sesión a X11. Se incluyen fuentes y
cabeceras oficiales exactas en el SRPM para reconstruir los tres módulos.

Instalar el archivo .fc45.x86_64.rpm con `sudo dnf install ./archivo.rpm` y ejecutar
`sudo bypssd-nextwindow-enable`. La detección automática se limita al USB probado
1926:0DBE. El firmware Secure Boot activo requiere firma de módulo/MOK aparte;
el paquete no modifica esa configuración. La firma RPM de un paquete no sustituye
la firma del módulo. Esta compilación experimental Fedora no está firmada con la
clave privada del canal BYPSSD, que permanece en el disco local no disponible en
esta sesión. No se desactivan verificaciones del sistema para instalarla.

El workflow comprueba compilación, dependencias de los decodificadores Intel32,
instalación DNF, tres vermagic exactos y unidades systemd. La prueba en pantalla
física y SELinux del equipo Fedora se realiza después de instalar.

Comprobar `uname -r`: si se arranca otro kernel, instalar sus cabeceras exactas
con `sudo dnf install kernel-devel-$(uname -r)` para que el helper lo reconstruya.
Se mantienen gcc/make/kernel-devel para futuras reconstrucciones. No se cambia
el kernel de arranque ni se instalan tres kernels completos, solo sus módulos.

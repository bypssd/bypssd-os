# NextWindow para BYPSSD OS x64

Versión actual del canal: **0.7.0.1-2**, firmada. Distribución:
https://github.com/bypssd/bypssd-os/releases/tag/updates-20261118-r17

El módulo GPL se basa en el commit upstream
`5fda7859cf07d99cd23ac1c842643411d780e7ae`. Los decodificadores originales Intel
32 bits conservan su licencia NextWindow MIT. La salida se adapta a multitáctil
tipo B/INPUT_PROP_DIRECT para libinput/KDE. Incluye módulos precompilados para
7.3.3-1-default y 7.3.4-1-default, y fuentes para reconstruir con otros kernels.

Se ha confirmado respuesta táctil física para USB **1926:0DBE**. La detección
automática se limita a ese identificador; otros modelos necesitan validación y
activación manual. El paquete no tiene decodificador ARM64. La dependencia del
branding solo lo incorpora si el kernel instalado es x64.

## Sistemas instalados

Importar la clave pública y actualizar según `scripts/updates/README.md`.
El paquete de branding r17 incorpora el controlador; el servicio autodetecta el
USB probado y activa el módulo sin reinstalación. Los equipos sin ese USB no
lo activan. Para desactivar la autodetección, crear
`/etc/bypssd-nextwindow/disable-auto` y deshabilitar el servicio
`bypssd-nextwindow-auto.service`.

Para otro USB soportado: `sudo bypssd-nextwindow-enable`.
Diagnóstico: `sudo bypssd-nextwindow-diagnose > nextwindow-diagnostico.txt`.
Revisar el archivo antes de compartirlo. No se añade el usuario al grupo input.

Secure Boot requiere firma de módulo e inscripción de clave aparte. El paquete
no genera claves MOK ni modifica Secure Boot. La firma RPM verifica el paquete;
no equivale a una firma del módulo aceptada por el firmware.

Si un kernel futuro no tiene módulo precompilado, la reconstrucción requiere las
cabeceras exactas instaladas; gcc, make y kernel-devel se mantienen como
dependencias. No se promete compatibilidad con futuras roturas de API del kernel.

## Live

Los cambios Live desaparecen al reiniciar. El antiguo paquete r1 necesitaba las
cabeceras exactas de la ISO; r2 contiene ya el módulo 7.3.3 correspondiente a r16.
Las ISO r16 entregadas no se han reconstruido para esta actualización instalada.

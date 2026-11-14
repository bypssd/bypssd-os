BYPSSD OS Renacer 1.0 para ARM64 y x64, con branding revisión 7 y cierre de arranque revisión 8.

La imagen ARM64 es idéntica, byte por byte, a la candidata r7 validada. En x64 se corrige únicamente el bloque de vídeo GRUB que emitía avisos de sintaxis antes del menú; no se recompilan ni modifican el kernel, los cargadores EFI firmados, el initrd ni el sistema LiveOS.

Se valida la configuración con grub2-script-check, se conserva el arranque híbrido mediante xorriso replay y se actualiza y comprueba el MD5 interno del medio. Cada ISO tiene su SHA256 y sus manifiestos.

Escritorio KDE Plasma, inicio BYPSSD en los navegadores, galerías sin temas Fedora, login propio y animaciones Renacer. Los paquetes y fuentes se publican por arquitectura en las releases packages-1.0-7-aarch64 y packages-1.0-7-x86_64.

Candidata de desarrollo: los paquetes propios aún no tienen firma de publicación y las pruebas realizadas son en máquinas virtuales, no en todas las familias de equipos físicos.

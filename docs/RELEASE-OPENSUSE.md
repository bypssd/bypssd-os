BYPSSD OS Renacer 1.1 · candidato basado en openSUSE Tumbleweed

Reconstrucción nativa para ARM64 y x64; no mezcla RPM ni repositorios Fedora.
KDE Plasma con fondo, colores, sesión, login y Plymouth propios BYPSSD. Se utiliza
Breeze oficial sin trasplantar el plugin compilado para Fedora. Calamares sustituye
a Anaconda para la instalación desde la sesión Live. Idioma español de España.

Discover incluye PackageKit, backend ZYpp y AppStream. Repositorios activos:
openSUSE Tumbleweed oficial y BYPSSD Updates en GitHub Pages, inicialmente vacío.
Las firmas y procedencia de los paquetes oficiales se conservan. El branding
propio se publica con su fuente como candidato sin firma de producción.

BYPSSD es una distribución independiente; no es un producto oficial de openSUSE
ni de SUSE. No se usan sus logotipos ni se afirma patrocinio. Los nombres de
repositorios oficiales y atribuciones técnicas se conservan para evitar confusión.

Candidato: las pruebas reales de arranque, tienda e instalación deben constar en
README antes de considerarlo listo para uso general. Secure Boot y hardware físico
no se presuponen compatibles por el hecho de generar una ISO.

Revisión r8: cinco diapositivas en español durante la instalación, barra amarilla
con porcentaje real y operación en curso. Corrige las claves de comandos GRUB
para la instalación UEFI y elimina la opción antigua de swap.

Incluye la configuración de arranque de reserva UEFI y compresión Zstandard.

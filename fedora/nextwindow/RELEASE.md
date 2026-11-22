RPM experimental específico para Fedora 45 x86_64, independiente del canal openSUSE/BYPSSD OS.

Incluye módulos precompilados para los tres últimos kernels publicados como estables en Bodhi a 22/11/2026:
- 7.3.4-300.fc45.x86_64
- 7.3.3-300.fc45.x86_64
- 7.2.15-300.fc45.x86_64

Compilación de los tres módulos, dependencias ELF32, instalación DNF y unidades systemd verificadas en Fedora 45. La respuesta táctil en Fedora físico queda pendiente de prueba. Secure Boot activo requiere firma de módulo/MOK aparte. No desactiva Secure Boot ni sandbox, ni añade repositorios openSUSE.

Esta compilación experimental no tiene firma RPM de producción. No se desactivan verificaciones del sistema. SHA256SUMS y las fuentes completas para reconstruirla se incluyen en esta Release.

Instalación (Fedora 45 tradicional con DNF):

```bash
curl -fL https://github.com/bypssd/bypssd-os/releases/download/nextwindow-fedora45-0.7.0.1-3/bypssd-nextwindow-0.7.0.1-3.fc45.x86_64.rpm -o /tmp/nextwindow-fedora45.rpm
sudo dnf install /tmp/nextwindow-fedora45.rpm
sudo bypssd-nextwindow-enable
```

Comprobar `uname -r`. Los tres módulos no instalan ni cambian el kernel de arranque. Otros kernels requieren sus cabeceras exactas para reconstruir el controlador. No sustituye un akmod mantenido y probado en cada actualización futura.

# Canal RPM BYPSSD: actualización instalada r17

Preparación de actualización, sin reconstruir ISO:

- `bypssd-branding-1.1-17.noarch.rpm`: configuración de Chromium para Radeon
  antigua y dependencias oficiales Mesa/RADV/firmware. Requiere NextWindow r2
  solo si está instalado `kernel-default(x86-64)`; ARM64 no recibe binarios x86.
- `bypssd-nextwindow-0.7.0.1-2.x86_64.rpm`: módulos precompilados 7.3.3 y kernel
  actual, fuentes de reconstrucción, activación automática solo USB 1926:0DBE.
  `/etc/bypssd-nextwindow/disable-auto` permite desactivarla. No cambia Secure Boot.
- Chromium: un launcher con el mismo ID de escritorio conserva accesos y perfiles;
  software/XWayland solo para Radeon antigua activa (`radeon`). AMDGPU/Intel y
  otros controladores conservan sus parámetros. La reparación de la corrupción
  de imágenes requiere confirmación en el equipo físico; no es una certificación
  de todas las GPU AMD. Nunca se añade `--no-sandbox`.

## Publicación

1. Workflow NextWindow `target=updates`: generar RPM/SRPM y comprobarlos.
2. Descargar artefacto a `out/updates/`. No subir ningún archivo privado del equipo.
3. Firmar en Linux LOCAL con una clave existente y autorizada. La clave privada
   nunca se exporta ni se envía al runner/GitHub. `sign-packages.sh` usa una clave
   existente; no genera credenciales. Si falta autorización, no activar el canal.
4. Publicar los RPM y SRPM firmados como assets de una Release propia. Las ISO
   permanecen fuera de GitHub.
5. Copiar los RPM y los `repodata/` firmados de staging a
   `repo/tumbleweed/{aarch64,x86_64}/updates/repodata/`, y la clave PÚBLICA a
   `repo/keys/BYPSSD-OS-RPM.asc`. Los dos RPM propios se sirven junto al catálogo para ser compatibles con ZYpp; las fuentes y copias adicionales están en la Release.
6. Probar el refresh, las firmas y la actualización desde r16 antes de anunciarla.

`stage-repository.sh` genera un staging nuevo; no modifica el repositorio activo.
Las ubicaciones RPM son relativas al catálogo, como requiere ZYpp. Los checksums y firmas se generan
DESPUÉS de firmar los RPM; firmar cambia el archivo y sus hashes.

## Equipos ya instalados

El repositorio estaba vacío y no había clave propia de confianza. La primera
actualización necesita importar/verificar la clave pública una vez. No se puede
mandar una orden remota a equipos sin agente: reciben los paquetes cuando abren
Discover, actualizan o ejecutan zypper. Clave publicada: `9979 0066 54A3 6906 D207 9972 1F4D 7FF1 32BD 7358`.
En cada equipo instalado, una vez:

```bash
sudo rpm --import https://raw.githubusercontent.com/bypssd/bypssd-os/main/repo/keys/BYPSSD-OS-RPM.asc
sudo zypper refresh
sudo zypper update bypssd-branding
```

No hace falta reinstalar. El nuevo requisito del paquete ya instalado hace que
los x64 incorporen el controlador. El resto de actualizaciones del sistema
continúa viniendo del upstream configurado. Una prueba Live no conserva cambios
al reiniciar; en instalado se mantienen. Cerrar todas las ventanas de Chromium y
volver a abrirlo aplica el launcher nuevo. Perfiles y archivos personales se conservan.

Publicado: https://github.com/bypssd/bypssd-os/releases/tag/updates-20261118-r17

El fallo de corrupción general al reanudar tras suspensión está pendiente de
identificar la GPU y analizar registros del kernel. Esta publicación no modifica
parámetros de energía del kernel ni declara ese fallo reparado.

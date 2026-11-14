# Repositorio BYPSSD sin ocupar el VPS

GitHub no ejecuta un servidor DNF: sirve los archivos estáticos que necesita DNF.
Para BYPSSD conviene separar **los paquetes propios** de los paquetes oficiales
sin modificar. No hace falta copiar ni mantener un espejo de toda la base.

- GitHub Releases: los RPM propios, sus SRPM y la ISO.
- GitHub Pages: `repodata/`, la clave pública y `bypssd.repo`.
- Servidores oficiales: kernel, Plasma, LibreOffice, Chromium y sus actualizaciones.
- VPS: cero archivos necesarios. Tu web puede enlazar la descarga de GitHub.

Esto distribuye tus cambios; no convierte los paquetes oficiales en paquetes
compilados por BYPSSD. Las referencias técnicas a su origen se conservan.

## Límites comprobados el 14/11/2026

GitHub Releases admite hasta 1000 archivos por release y cada uno debe ser menor
que 2 GiB. La ISO actual (~1,6 GiB) cabe. Los tres RPM propios ocupan pocos MB;
el SRPM de Breeze ocupa unos 41 MB. No subas la caché completa de out/rpms a Git.

GitHub Pages admite sitios publicados de hasta 1 GB y tiene un límite flexible
de transferencia de 100 GB/mes. Por eso alojamos solo metadatos en Pages y los
binarios de este proyecto en Releases. No usar LFS ni GitHub Packages para esto.
No se trata de un almacén de archivos arbitrarios: acompaña los binarios con el
código, las recetas de construcción, las licencias y las notas de esta distribución.

Fuentes:
- https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

## 1. Crear un repositorio público

En GitHub crea `bypssd-os` bajo tu usuario u organización. En Settings → Pages →
Build and deployment, elige **GitHub Actions**. Clona ese repositorio en una
carpeta distinta, por ejemplo `~/BYPSSD-OS/github-publish/`.

No subas todo ~/BYPSSD-OS con git add .: contiene discos virtuales, cachés y logs.
En el repositorio público guarda código/recetas/licencias, no secretos ni discos.

Los ejemplos usan `TU_USUARIO/bypssd-os`; reemplázalo por el nombre real.
No se ha creado ni publicado ningún repositorio desde esta sesión.

## 2. Firmar los paquetes propios

Hace falta una clave de publicación propia. No publiques una clave privada ni
copies la clave oficial de la base para firmar tus paquetes.

Arranca el entorno con `./build.sh env` y abre su terminal:

```sh
podman --connection bypssd-build-root exec -it bypssd-build-f45 bash
```

Dentro del contenedor, crea una clave de firma con contraseña y conserva una
copia privada segura fuera del repositorio público. No dejes que la única copia
sea este contenedor:

```sh
export GNUPGHOME=/var/tmp/bypssd-release-gnupg
mkdir -m 700 -p "$GNUPGHOME"
gpg --quick-generate-key 'BYPSSD OS Release <info@bypssd.com>' rsa3072 sign 2y
gpg --list-secret-keys --keyid-format long
```

Copia la **huella completa** de la clave y prepara una revisión nueva e inmutable:

```sh
export BYPSSD_SIGNING_KEY=HUELLA_COMPLETA
bash scripts/prepare-github-repo.sh TU_USUARIO/bypssd-os packages-1.0-4
```

El script firma copias de los últimos tres RPM BYPSSD, genera metadatos con URLs
absolutas a los assets de esa release, firma `repomd.xml`, exporta la clave pública
y adjunta los tres SRPM correspondientes. No modifica los RPM del archivo de
compilación ni los paquetes oficiales. El tag debe ser nuevo; no reutilizarlo ni
reemplazar binarios que ya se publicaron.

Si falta BYPSSD_SIGNING_KEY prepara solo una demostración **deshabilitada** y sin
firmas. Está así la muestra local `out/github-repository/packages-1.0-4-preview2/`.
No instalarla saltándose gpgcheck. El enlace BYPSSD-EJEMPLO es deliberadamente
ficticio; no es un servicio desplegado.

## 3. Subir los RPM y las fuentes a Releases

En el Mac instala GitHub CLI si aún no lo tienes (`brew install gh`) y autentícate
con `gh auth login`. Desde ~/BYPSSD-OS ejecuta:

```sh
bash scripts/publish-github-repo.sh TU_USUARIO/bypssd-os packages-1.0-4
```

La publicación exige las firmas y crea una release nueva. Primero publica los
assets y después los metadatos: así no anuncias archivos que aún no existen.
La firma de los SRPM y de la ISO se puede añadir con GPG antes de publicarlos;
los RPM binarios y repomd.xml sí se firman obligatoriamente en este flujo.

## 4. Activar el sitio de metadatos

En el clon de tu repositorio GitHub:

1. Copia el contenido de `out/github-repository/packages-1.0-4/pages/` a `site/`.
2. Copia `scripts/github-pages.yml` a `.github/workflows/pages.yml`.
3. Añade también las recetas, parches y licencias del proyecto; no añadas out/,
   claves privadas, GNUPGHOME, discos qcow2, sockets ni la copia de trabajo completa.
4. Haz commit y push. El workflow publicará site/ mediante Pages.

El árbol publicado debe quedar así:

```text
site/
  .nojekyll
  index.html
  bypssd.repo
  RPM-GPG-KEY-BYPSSD
  45/aarch64/repodata/
    repomd.xml
    repomd.xml.asc
    ...primary.xml... y demás metadatos...
```

El resultado será `https://TU_USUARIO.github.io/bypssd-os/`. Comprueba que existen
`bypssd.repo`, `RPM-GPG-KEY-BYPSSD` y `45/aarch64/repodata/repomd.xml`, y descarga
un RPM usando la URL absoluta de los metadatos. Verifica la huella de la clave
por un canal independiente, por ejemplo una página de bypssd.com controlada por ti.

## 5. Habilitarlo en un sistema BYPSSD

Solo después de comprobar URL, firmas y huella. Estos comandos son para el Linux
instalado, no para macOS:

```sh
curl -fL https://TU_USUARIO.github.io/bypssd-os/RPM-GPG-KEY-BYPSSD -o /tmp/BYPSSD.asc
gpg --show-keys --with-fingerprint /tmp/BYPSSD.asc
# Comparar la huella completa con la publicada por BYPSSD.
sudo rpm --import /tmp/BYPSSD.asc
curl -fL https://TU_USUARIO.github.io/bypssd-os/bypssd.repo -o /tmp/bypssd.repo
sudo install -m 644 /tmp/bypssd.repo /etc/yum.repos.d/bypssd.repo
sudo dnf --repo=bypssd makecache
sudo dnf upgrade
```

La ISO no lleva habilitada ninguna URL ficticia ni ninguna clave de publicación
inventada. Se añadirá el repositorio real al branding cuando exista y esté probado.
Para cada actualización: aumenta Release del RPM, reconstruye, prepara un tag
nuevo, publica los nuevos assets y actualiza site/ con los metadatos completos.
No retires los assets antiguos mientras haya clientes que puedan tener sus
metadatos en caché. Incrementa la versión del producto si cambias de base.

## 6. Descargar la ISO desde GitHub

Puedes adjuntar la ISO y su checksum a una release específica del sistema:

```sh
gh release create renacer-1.0 \
  out/BYPSSD-OS-Renacer-1.0-aarch64.iso \
  out/BYPSSD-OS-Renacer-1.0-aarch64.iso.sha256 \
  --repo TU_USUARIO/bypssd-os --title 'BYPSSD OS Renacer 1.0' \
  --notes-file docs/github-release-notes.md
```

Antes de publicar la distribución completa deben cerrarse los puntos de marcas,
fuentes correspondientes de los componentes oficiales y pruebas del README.
Una release de ISO no debe reemplazar el tag de los RPM: sus metadatos utilizan
URLs de descarga estables para cada revisión de paquetes.

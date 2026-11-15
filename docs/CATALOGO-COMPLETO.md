# Catálogo completo servido por BYPSSD

El workflow `mirror-catalog.yml` copia el catálogo binario estable completo de la
base 45 y sus actualizaciones para aarch64 y x86_64, incluyendo noarch y las
arquitecturas auxiliares presentes en esos repositorios. No limita la copia a las
aplicaciones de la ISO. Deduplica por nombre y checksum y divide los RPM en
releases inmutables de hasta 900 archivos. No incluye rawhide, testing, debuginfo,
otras versiones ni otras arquitecturas. Las fuentes originales deben seguir
accesibles conforme a las licencias; este espejo binario no sustituye esa obligación.

El origen de descarga DNF será `bypssd-base` o `bypssd-updates`. El proveedor que
figura dentro de un RPM, sus licencias, firma y sufijo fc45 siguen siendo originales:
no se atribuyen a BYPSSD compilaciones realizadas por otra organización.

## Estado y activación

No activar hasta que termine correctamente el workflow. Solo después de comprobar
cada asset y su digest se publica `catalog-summary.json` con `status: complete` y
los índices de los dos repositorios en GitHub Pages. Antes de eso, las ISO r8
existentes mantienen sus repositorios anteriores. No han sido reconstruidas por
esta operación de espejo.

En BYPSSD Linux, desde una copia del proyecto:

```sh
sudo bash scripts/use-bypssd-repositories.sh
```

El script rechaza macOS y otras distribuciones, verifica la publicación completa,
guarda la configuración anterior y habilita exclusivamente los repositorios BYPSSD.
No se ejecuta automáticamente en el Mac ni en Parallels.

## Integridad y actualizaciones

Cada RPM se comprueba contra el checksum del inventario original antes de subirlo.
Cada asset publicado se vuelve a verificar mediante tamaño y digest SHA256 de
GitHub antes de publicar los índices. Los índices señalan exclusivamente a GitHub
Releases. DNF conserva `gpgcheck=1` y la clave pública original instalada. Los
índices usan HTTPS y `repo_gpgcheck=0`, no una firma BYPSSD nueva. No se ha creado
ni transferido una nueva clave privada de firma.

Es un snapshot: no habrá actualizaciones nuevas hasta completar otra sincronización.
Para actualizar, ejecutar el workflow con un identificador nuevo; solo se publican
los índices cuando todos los lotes han terminado. No borrar releases antiguas que
puedan seguir referenciadas por cachés de clientes. La copia de un catálogo completo
puede ocupar cientos de GB y tardar horas; no utiliza el VPS de BYPSSD.

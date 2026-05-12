# Copia por atributo a archivos IS

## Forma correcta de buscar los archivos de dibujo (IS05, IS06, etc.)

**Problema:** `DocumentNameService.GetLoadedDocumentsNameData()` solo devuelve el archivo de dibujo **actualmente activo**. No devuelve el resto de archivos del proyecto que ves en el gestor (p. ej. 700 IS05, 701 IS06). Por eso no se puede usar solo esa lista para encontrar el archivo cuyo nombre contiene el valor del atributo (IS05).

**Solución (lo que implementa `Saneamiento.py`):** usar `GetDocumentNameByFileNumber(file_number, withNumber, withLabel, delimiter)` sobre un **rango de números de archivo** del proyecto y, con los `file_number` encontrados, hacer `LoadFile` y crear allí las copias.

1. Obtener el archivo activo: `DrawingFileService.GetActiveFileNumber()` (p. ej. 699).
2. Para cada `file_number` en un rango alrededor del activo (p. ej. de `active_file - 50` hasta `active_file + 50`), llamar:
   ```python
   full_name = DocumentNameService.GetDocumentNameByFileNumber(
       file_number,
       withNumber=True,
       withLabel=True,
       delimiter=" "
   )
   ```
3. Si `full_name` no es vacío y el valor buscado (p. ej. `"IS05"`) está contenido en `full_name` (comparación sin distinguir mayúsculas), ese `file_number` se añade a la lista de **archivos destino**.
4. Para cada `file_number` encontrado:
   - Llamar `DrawingFileService().LoadFile(doc, file_number, ActiveForeground)` para activar ese archivo.
   - Crear allí las copias (`CreateElements`) y recoger los nuevos UUIDs.
   - Guardar esos UUIDs y el `file_number` en los parámetros `CopiedElementsUUIDs` y `CopiedElementsFiles` del `build_ele` para poder borrarlos en futuras ediciones.

Así se encuentra el archivo "700 IS05" aunque en ese momento solo esté "cargado" el archivo 699, y se crean/copias los elementos allí. Este comportamiento está implementado en:

- `_find_target_files_for_parent(parent_id, search_radius=50)` → localiza los `file_number` por nombre.
- `_copy_elements_by_pmp_pare(elems)` → llama a la función anterior, cambia de archivo con `LoadFile`, crea las copias y persiste los UUIDs/archivos para su borrado posterior.


hacer que funcione en todos los rangos

DocumentNameService.GetLoadedDocumentsNameData()`
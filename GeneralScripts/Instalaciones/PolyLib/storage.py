# -*- coding: utf-8 -*-
"""
Módulo para persistir y leer JSON (merge por path_id).
API principal: PolylineStorage(path=None)
- save_path(path_id, evento_dict)
- load_all()
- load_path(path_id)
"""
import json, os

from typing import Any, Dict, List
from .utils import _flush
from pathlib import Path


class PolylineStorage:
    def __init__(self, name: str = "default"):
        self.path = os.path.join(Path(__file__).resolve().anchor, f"polyline_lib_{name}.json")
        self.storage_name: str = name
        self.numbering_by_type = {}
        self.base_path: str | None = None

    def load_all(self) -> List[Dict[str, Any]]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
        except FileNotFoundError:
            return []
        except Exception as e:
            print("[PolylineStorage] load_all EXC:", e); _flush()
            return []

    def save_all(self, path_id: int, data: dict) -> bool:
        clear_file = {}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(clear_file, f, ensure_ascii=False, indent=2)

        index: Dict[int, Dict[str, Any]] = {}
        for entry in data:
            try: index[int(entry.get("path_id"))] = entry
            except Exception: pass

        if path_id in index:
            dst = index[path_id]
            for k in ("iniciales","intermedios","finales"):
                dst[k] = (dst.get(k) or []) + data[k]
        else:
            index[path_id] = {"path_id": path_id, **data}

        out_list = [index[k] for k in sorted(index.keys())]
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(out_list, f, ensure_ascii=False, indent=2)
            print(f"[JSON] OK saved_path={self.path} (len={len(out_list)})"); _flush()
            return True
        except Exception as e:
            print("[JSON] ERROR escritura:", e); _flush()
            return False

    def _get_numbering_file_path(self, element_type):
        """
        Obtiene la ruta al archivo NumTD específico para el tipo de elemento.
        Si el archivo no existe, lo crea.
        """
        try:
            # Raiz del usuario
            base_path = self.find_file()

            # Carpeta base del proyecto
            num_dir = os.path.join(base_path, "AbsEnum\\instalaciones", self.storage_name.lower())

            # Crear directorio si no existe
            os.makedirs(num_dir, exist_ok=True)

            # Ruta completa al archivo
            filename = f"{element_type}.txt"
            num_file = os.path.join(num_dir, filename)

            # 👉 CREAR EL ARCHIVO SI NO EXISTE
            if not os.path.exists(num_file):
                with open(num_file, "w", encoding="utf-8") as f:
                    f.write("")  # archivo vacío inicial
                print(f"[NUMTD] Archivo creado: {num_file}")

            return num_file

        except Exception as e:
            print(f"[NUMTD] Error obteniendo ruta de numeración para {element_type}: {e}")
            return None

    def find_file(self):
        base_path = Path(__file__).resolve().anchor
        if self.base_path:
            base_path = self.base_path
        return base_path

    def _load_numbering_file(self, element_type):
        """
        Carga los números existentes del archivo NumTD específico para un tipo de elemento.
        Si el archivo no existe, se crea automáticamente.
        """

        # Inicializar entrada en el diccionario si no existe
        if element_type not in self.numbering_by_type:
            self.numbering_by_type[element_type] = {"used": set(), "next": 1}

        # Obtener (y crear si hace falta) el archivo
        num_file = self._get_numbering_file_path(element_type)
        if not num_file:
            return  # error real, no debería pasar normalmente

        try:
            used_nums = set()
            # Leer archivo (aunque esté vacío)
            with open(num_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        used_nums.add(int(line))

            # Actualizar el diccionario
            self.numbering_by_type[element_type]["used"] = used_nums

            # Calcular siguiente número
            if used_nums:
                next_num = max(used_nums) + 1
            else:
                next_num = 1

            self.numbering_by_type[element_type]["next"] = next_num

            print(
                f"[NUMTD] {element_type}: "
                f"{len(used_nums)} números cargados. "
                f"Próximo: {next_num}"
            )

        except Exception as e:
            print(f"[NUMTD] Error cargando archivo de numeración para {element_type}: {e}")

    def _save_numbering_file(self):
        """Guarda todos los números asignados en archivos separados por tipo de elemento"""
        try:
            total_saved = 0
            for element_type, data in self.numbering_by_type.items():
                num_file = self._get_numbering_file_path(element_type)
                if not num_file:
                    continue

                # Ordenar los números y guardarlos
                sorted_numbers = sorted(data["used"])
                if sorted_numbers:  # Solo guardar si hay números
                    with open(num_file, 'w') as f:
                        for num in sorted_numbers:
                            f.write(f"{num}\n")
                    print(f"[NUMTD] {element_type}: Guardados {len(sorted_numbers)} números")
                    total_saved += len(sorted_numbers)

            print(f"[NUMTD] Total guardado: {total_saved} números en {len(self.numbering_by_type)} archivos")
        except Exception as e:
            print(f"[NUMTD] Error guardando archivos de numeración: {e}")

    def _get_next_number(self, element_type: str):
        """Obtiene el siguiente número disponible para un tipo de elemento específico

        Args:
            element_type: String que identifica el tipo (ej: "Tubo_25mm", "Codo_110mm_45deg")

        Returns:
            int: Siguiente número disponible para ese tipo
        """
        # Cargar archivo si es la primera vez que se pide este tipo
        if element_type not in self.numbering_by_type:
            self._load_numbering_file(element_type)

        # Obtener el siguiente número
        num = self.numbering_by_type[element_type]["next"]

        # Marcarlo como usado y actualizar el siguiente
        self.numbering_by_type[element_type]["used"].add(num)
        self.numbering_by_type[element_type]["next"] = num + 1

        return num

    def _reset_numbering_from(self, element_type: str, start_number: int):
        """
        Elimina de la lista de usados todos los números iguales o superiores
        a 'start_number' para permitir que se vuelvan a asignar en la nueva red.
        """
        if element_type not in self.numbering_by_type:
            self._load_numbering_file(element_type)

        used = self.numbering_by_type[element_type]["used"]
        # Filtramos: nos quedamos solo con los números menores al punto de corte
        new_used = {n for n in used if n < start_number}

        self.numbering_by_type[element_type]["used"] = new_used
        self.numbering_by_type[element_type]["next"] = start_number

        # Guardamos inmediatamente para que el archivo TXT refleje el hueco
        self._save_numbering_file()
        print(f"[NUMTD] Reset en {element_type}: Volviendo a empezar desde {start_number}")

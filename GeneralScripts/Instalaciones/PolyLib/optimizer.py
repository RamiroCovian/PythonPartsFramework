# -*- coding: utf-8 -*-
"""
PolyLib – Optimizer module.

Encapsula el pipeline completo de optimización de caminos:

    PolylineInteractor → PolylineOptimizer.run() → Caminos_Optimos_Lib (subprocess) → restored polyline

Uso desde el interactor::

    self.optimizer = PolylineOptimizer(self)
    self.optimizer.run(tipo_instalacion="Electricidad")

Uso desde script_object (si se prefiere instanciar allí)::

    self.optimizer = PolylineOptimizer(self.script_object_interactor)
"""

from __future__ import annotations

import json
import os
import uuid

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from .interactor import PolylineInteractor

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BaseElements as AllplanBaseElements
    import NemAll_Python_BasisElements as AllplanBasisElements
    import NemAll_Python_Utility as PythonUtility
    _ALLPLAN_AVAILABLE = True
except Exception:
    _ALLPLAN_AVAILABLE = False

from .models import OptimizerNode
from .optimizer_adapter import build_optimizer_input, parse_optimizer_output
from .optimizer_runner import run_optimizer


class PolylineOptimizer:
    """Gestiona el pipeline completo de optimización de caminos para PolyLib.

    Se instancia con una referencia al :class:`PolylineInteractor` activo.
    Accede al estado compartido a través de ``interactor.script_object``.

    Args:
        interactor: Instancia activa del interactor de polilínea.
    """

    def __init__(self, interactor: "PolylineInteractor") -> None:
        self._interactor = interactor

    # ------------------------------------------------------------------
    # Propiedad de conveniencia
    # ------------------------------------------------------------------
    @property
    def _so(self):
        """Acceso directo al ScriptObject (fuente de estado compartido)."""
        return self._interactor.script_object

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def run(
        self,
        tipo_instalacion: str = "",
        timeout: int = 250,
    ) -> bool:
        """Ejecuta el pipeline completo de optimización y carga el resultado.

        Cuando los caminos tienen distintos tipos de instalación (``inst_type``),
        agrupa los caminos por tipo y lanza una ejecución del optimizador por
        cada grupo (un JSON distinto por tipo), evitando que el último tipo
        sobreescriba a los anteriores.

        Args:
            tipo_instalacion: Tipo de instalación de fallback cuando un camino
                no tiene ``inst_type`` propio.
            mock_config: Overrides para el adapter (techo, obstáculos, etc.).
            timeout: Segundos máximos de espera por subproceso.

        Returns:
            ``True`` si al menos un camino optimizado se cargó correctamente.
        """
        # 0. Si hay un tramo activo en create_mode, guardarlo antes de optimizar
        self._flush_active_polyline()

        # ── Test override (inyectado por inject_test_points) ─────────────────
        test_override = getattr(self._interactor, "_test_input_override", None)
        if test_override is not None:
            n_cam = len(test_override.get("caminos", []))
            print(f"[Optimizer] Usando test_input_override ({n_cam} camino(s))")
            try:
                input_path = self._write_temp_json(build_optimizer_input(test_override))
            except Exception as ex:
                self._show_dialog(error=f"Error escribiendo input: {ex}")
                return False
            try:
                grafo = run_optimizer(input_json_path=input_path, timeout=timeout)
            except (TimeoutError, RuntimeError, FileNotFoundError) as ex:
                print(f"[Optimizer] Subproceso fallido: {ex}")
                self._show_dialog(error=str(ex))
                return False
            paths = parse_optimizer_output(grafo)
            if not paths:
                msg = "El optimizador no devolvió caminos válidos."
                print(f"[Optimizer] {msg}")
                self._show_dialog(error=msg)
                return False
            per_types = [tipo_instalacion] * len(paths)
            try:
                self._restore_result(paths, per_types)
                self._show_dialog(num_paths=len(paths), total_points=sum(len(p) for p in paths))
                return True
            except Exception as ex:
                print(f"[Optimizer] Error restaurando resultado: {ex}")
                self._show_dialog(error=str(ex))
                return False

        # ── Flujo normal: agrupar caminos por tipo de instalación ────────────
        nodo_list: List[List[OptimizerNode]] = getattr(self._so, "nodo_list", None) or []
        camino_inst_types: List[str] = list(getattr(self._so, "camino_inst_types", None) or [])

        active   = self._so.active_paths or []
        n_nodos  = sum(len(g) for g in nodo_list)
        print(
            f"[Optimizer] active_paths={len(active)} path(s), "
            f"{sum(len(p) for p in active)} punto(s) | nodo_list={n_nodos} nodo(s)"
        )

        if not nodo_list:
            msg = (
                "No hay nodos para optimizar.\n\n"
                f"{n_nodos} nodo(s).\n"
                "Asegúrese de haber insertado al menos 2 nodos de ruta\n"
                "y estar en modo Automático antes de ejecutar el optimizador."
            )
            print(f"[Optimizer] {msg}")
            self._show_dialog(error=msg)
            return False

        # Resolver el tipo de cada camino (camino_inst_types tiene precedencia)
        resolved: List[str] = [
            (camino_inst_types[i] if i < len(camino_inst_types) and camino_inst_types[i]
             else tipo_instalacion)
            for i in range(len(nodo_list))
        ]

        # Agrupar índices de camino por tipo, preservando el orden de inserción
        type_groups: Dict[str, List[Tuple[int, List[OptimizerNode]]]] = {}
        for i, nodos_grupo in enumerate(nodo_list):
            key = resolved[i] or ""
            type_groups.setdefault(key, []).append((i, nodos_grupo))

        print(
            f"[Optimizer] Grupos por tipo: "
            + ", ".join(f"'{k}'={len(v)} camino(s)" for k, v in type_groups.items())
        )

        # Ejecutar el optimizador por cada grupo y recolectar resultados con
        # su índice original para poder reordenarlos al final
        all_results: List[Tuple[int, List[List[float]], str]] = []
        for inst_key, entries in type_groups.items():
            group_caminos = self._build_group_caminos(entries, inst_key)
            if not group_caminos:
                print(f"[Optimizer] Grupo '{inst_key}': sin caminos válidos (< 2 nodos), omitido.")
                continue

            group_dict = {
                "id":      f"proyecto-{uuid.uuid4().hex[:8]}",
                "tipo":    inst_key,
                "caminos": group_caminos,
            }
            # Incluir datos reales del ElementSelector si están disponibles
            selector_mock: Dict[str, Any] = {}
            techos = getattr(self._so, "techos_is", None) or []
            subdivisiones = getattr(self._so, "subdivisiones_is", None) or []
            tubos = getattr(self._so, "tubos_is", None) or []
            obstaculos = getattr(self._so, "obstaculos", None) or []
            if techos:
                selector_mock["techo"] = techos
            if subdivisiones:
                selector_mock["subdivisiones_is"] = subdivisiones
            if tubos:
                selector_mock["tubos_is"] = tubos
            if obstaculos:
                selector_mock["obstaculos"] = obstaculos
            if selector_mock:
                print(
                    f"[Optimizer] Usando datos del selector: "
                    f"{len(techos)} techo(s), {len(subdivisiones)} subdiv., "
                    f"{len(tubos)} tubo(s), {len(obstaculos)} obstáculo(s)"
                )
            optimizer_input = build_optimizer_input(group_dict, mock_config=selector_mock or None)
            print(f"[Optimizer] Grupo '{inst_key}': {len(group_caminos)} camino(s) → ejecutando optimizador...")

            try:
                input_path = self._write_temp_json(optimizer_input)
            except Exception as ex:
                print(f"[Optimizer] Error escribiendo JSON para '{inst_key}': {ex}")
                continue

            try:
                grafo = run_optimizer(input_json_path=input_path, timeout=timeout)
            except (TimeoutError, RuntimeError, FileNotFoundError) as ex:
                err_text = "El optimizador finalizo pero no se encontró el archivo _grafo.json"
                print(f"[Optimizer] Subproceso fallido para '{inst_key}': {ex}")
                self._show_dialog(error=err_text)
                return False

            group_paths = parse_optimizer_output(grafo)
            if not group_paths:
                print(f"[Optimizer] Grupo '{inst_key}': optimizador sin resultados válidos.")
                continue

            for local_idx, path in enumerate(group_paths):
                orig_idx = entries[local_idx][0] if local_idx < len(entries) else (len(all_results) + local_idx)
                all_results.append((orig_idx, path, inst_key))
            print(f"[Optimizer] Grupo '{inst_key}': {len(group_paths)} camino(s) obtenidos.")

        if not all_results:
            msg = "El optimizador no devolvió caminos válidos."
            print(f"[Optimizer] {msg}")
            self._show_dialog(error=msg)
            return False

        # Ordenar por índice original para mantener el orden de los caminos
        all_results.sort(key=lambda x: x[0])
        ordered_paths = [p for _, p, _ in all_results]
        ordered_types = [t for _, _, t in all_results]

        try:
            self._restore_result(ordered_paths, ordered_types)
            num_paths = len(ordered_paths)
            total_pts = sum(len(p) for p in ordered_paths)
            print(f"[Optimizer] Polilínea optimizada: {num_paths} camino(s), {total_pts} puntos")
            self._show_dialog(num_paths=num_paths, total_points=total_pts)
            return True
        except Exception as ex:
            print(f"[Optimizer] Error restaurando resultado: {ex}")
            self._show_dialog(error=str(ex))
            return False

    # ------------------------------------------------------------------
    # Construcción del input
    # ------------------------------------------------------------------
    def _build_group_caminos(
        self,
        entries: List[Tuple[int, List[OptimizerNode]]],
        inst_type: str,
    ) -> List[Dict[str, Any]]:
        """Construye la lista de caminos para un subgrupo del mismo tipo de instalación.

        Args:
            entries: Lista de ``(orig_idx, nodos_grupo)`` del mismo ``inst_type``.
            inst_type: Tipo de instalación para todos los caminos de este grupo.

        Returns:
            Lista de dicts ``{"id", "tipo", "nodos"}`` lista para pasar a
            ``build_optimizer_input``.
        """
        caminos: List[Dict[str, Any]] = []
        for _, nodos_grupo in entries:
            if len(nodos_grupo) < 2:
                continue
            nodos_dict = [nd.to_dict() for nd in nodos_grupo]
            for i, nd_dict in enumerate(nodos_dict):
                nd_dict["anteriores"] = [nodos_dict[i - 1]["id"]] if i > 0 else []
                nd_dict["siguientes"] = [nodos_dict[i + 1]["id"]] if i < len(nodos_dict) - 1 else []
            caminos.append({
                "id":    f"camino-{uuid.uuid4().hex[:8]}",
                "tipo":  inst_type,
                "nodos": nodos_dict,
            })
        return caminos

    def _build_camino_dict(self, tipo_instalacion: str = "") -> Dict[str, Any]:
        """Construye el dict de entrada al optimizador desde ``script_object.nodo_list``.

        ``nodo_list`` es ``List[List[OptimizerNode]]`` generado por
        ``PointInput._rebuild_nodo_list``: cada sublista agrupa los nodos del
        mismo ``color_id`` (un color = un camino independiente).

        Dentro de cada camino, los nodos ``inicio`` / ``orden_obligatorio`` /
        ``fin`` se encadenan en orden de inserción vía
        ``anteriores``/``siguientes``. Los ``orden_libre`` flotan (listas vacías).

        Returns:
            Dict con clave ``"caminos"`` lista de caminos, compatible con
            ``optimizer_adapter.build_optimizer_input``:
            ``{"id": str, "tipo": str, "caminos": [{"id", "tipo", "nodos"}, ...]}``.
        """
        # nodo_list es List[List[OptimizerNode]]: cada sublista = un camino
        nodo_list: List[List[OptimizerNode]] = getattr(self._so, "nodo_list", None) or []
        print("[Optimizer] nodo_list:", nodo_list)
        if not nodo_list:
            print("[Optimizer] nodo_list vacío — sin nodos para optimizar.")
            return {"id": f"proyecto-{uuid.uuid4().hex[:8]}", "tipo": tipo_instalacion, "caminos": []}

        caminos_out: List[Dict[str, Any]] = []
        camino_inst_types: List[str] = list(getattr(self._so, "camino_inst_types", None) or [])

        for camino_idx, nodos_grupo in enumerate(nodo_list):
            if len(nodos_grupo) < 2:
                continue

            nodos_dict = [nd.to_dict() for nd in nodos_grupo]

            # Encadenar todos los nodos en orden de inserción.
            # El tipo (orden_libre / orden_obligatorio) ya indica al optimizador
            # el nivel de constraint; no hay nodos flotantes.
            for i, nd_dict in enumerate(nodos_dict):
                nd_dict["anteriores"] = [nodos_dict[i - 1]["id"]] if i > 0 else []
                nd_dict["siguientes"] = [nodos_dict[i + 1]["id"]] if i < len(nodos_dict) - 1 else []

            # Tipo de instalación específico del camino (por color_id), con fallback
            camino_tipo = (
                camino_inst_types[camino_idx]
                if camino_idx < len(camino_inst_types) and camino_inst_types[camino_idx]
                else tipo_instalacion
            )
            caminos_out.append({
                "id":    f"camino-{uuid.uuid4().hex[:8]}",
                "tipo":  camino_tipo,
                "nodos": nodos_dict,
            })

        if not caminos_out:
            return {"id": f"proyecto-{uuid.uuid4().hex[:8]}", "tipo": tipo_instalacion, "caminos": []}

        result = {
            "id":      f"proyecto-{uuid.uuid4().hex[:8]}",
            "tipo":    tipo_instalacion,
            "caminos": caminos_out,
        }
        print(
            f"[Optimizer] _build_camino_dict: {len(caminos_out)} camino(s), "
            f"{sum(len(c['nodos']) for c in caminos_out)} nodos totales."
        )
        return result

    # ------------------------------------------------------------------
    # Escritura del JSON temporal
    # ------------------------------------------------------------------
    def _write_temp_json(self, optimizer_input: Dict[str, Any]) -> str:
        """Escribe el dict de input en un archivo JSON temporal.

        El archivo se crea en ``<Libreria>/optimizer_temp/<timestamp>/``.

        Returns:
            Ruta absoluta al archivo JSON creado.

        Raises:
            OSError: Si no se puede crear el directorio o escribir el archivo.
        """
        lib_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(lib_dir, "optimizer_temp")

        if os.path.isdir(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        input_dir = os.path.join(temp_dir, stamp)
        os.makedirs(input_dir, exist_ok=True)
        input_path = os.path.join(input_dir, f"input_{stamp}.json")

        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(optimizer_input, f, ensure_ascii=False, indent=2)

        print(f"[Optimizer] Input escrito en: {input_path}")
        return input_path

    # ------------------------------------------------------------------
    # Restauración del resultado
    # ------------------------------------------------------------------
    def _restore_result(
        self,
        paths: List[List[List[float]]],
        per_path_types: List[str],
    ) -> None:
        """Convierte los caminos optimizados en Point3D y los carga al estado.

        Escribe el resultado en ``script_object.saved_optimized_paths``
        (nunca en ``saved_paths``, que es exclusivo del modo Manual).
        Finalmente llama a ``_draw_preview`` para reflejar el cambio.

        Args:
            paths: Lista de caminos, cada uno lista de ``[x, y, z]``.
            per_path_types: Tipo de instalación para cada camino (mismo orden
                que ``paths``). Puede ser una lista vacía si no se conoce.
        """
        new_saved_paths: List[List[Any]] = []
        for path in paths:
            if len(path) < 2:
                continue
            pts = [AllplanGeo.Point3D(float(p[0]), float(p[1]), float(p[2])) for p in path]
            new_saved_paths.append(pts)

        self._so.saved_optimized_paths = new_saved_paths

        # Registrar el tipo de instalación por camino desde per_path_types
        _fallback = getattr(self._so, "selected_inst_type", None) or ""
        self._so.path_inst_types_auto = {
            i: (per_path_types[i] if i < len(per_path_types) and per_path_types[i] else _fallback)
            for i in range(len(new_saved_paths))
            if (i < len(per_path_types) and per_path_types[i]) or _fallback
        }

        # last_points: igual que create_mode al guardar un camino
        for path in new_saved_paths:
            self._interactor.last_points.extend(path)

        # Limpiar overlay / estado de test
        self._interactor._free_points             = []
        self._interactor._free_point_roles        = []
        self._interactor._optimizer_preview_elems = []
        self._interactor._test_input_override     = None

        # Fusión cross-mode: si un camino optimizado comparte extremo con uno
        # manual, se fusionan en saved_paths y el auto desaparece.
        try:
            self._interactor._try_merge_across_modes()
        except Exception as ex:
            print(f"[Optimizer] _try_merge_across_modes: {ex}")

        # Sincronizar self.data y segment_groups con los nuevos caminos optimizados
        # para que _create_elements_preview pueda generar el 3D correcto (Bug 1 fix).
        try:
            self._interactor.get_segments()
        except Exception as ex:
            print(f"[Optimizer] get_segments: {ex}")
        try:
            self._interactor._update_segment_groups()
        except Exception as ex:
            print(f"[Optimizer] _update_segment_groups: {ex}")
        try:
            self._so._create_elements_preview()
            self._interactor.saved_elements = True
        except Exception as ex:
            print(f"[Optimizer] _create_elements_preview: {ex}")

        # Refrescar preview
        try:
            last_pt = getattr(self._interactor, "_last_preview_point", None)
            self._interactor._draw_preview(last_pt)
        except Exception as ex:
            print(f"[Optimizer] Aviso: no se pudo refrescar preview: {ex}")

    def _sync_as_create_mode(self) -> None:
        """Sincroniza ``saved_optimized_paths`` → ``saved_paths`` y limpia.

        Mueve los caminos optimizados a ``saved_paths`` para que se
        comporten como caminos dibujados manualmente, y luego vacía
        ``saved_optimized_paths``.

        Replica la secuencia que ejecuta el interactor al finalizar un tramo::

            get_segments() → _update_segment_groups() → _create_elements_preview()
            → saved_elements = True
        """
        opt_paths = getattr(self._so, "saved_optimized_paths", None) or []
        if not opt_paths:
            return

        inter = self._interactor
        # self._so.saved_paths.extend(opt_paths)
        self._so.saved_optimized_paths = []
        try:
            inter.get_segments()
        except Exception as ex:
            print(f"[Optimizer] get_segments: {ex}")
        try:
            inter._update_segment_groups()
        except Exception as ex:
            print(f"[Optimizer] _update_segment_groups: {ex}")
        try:
            self._so._create_elements_preview()
        except Exception as ex:
            print(f"[Optimizer] _create_elements_preview: {ex}")
        inter.saved_elements = True
        inter.saved_segments = getattr(self._so, "saved_segments", [])
        print(
            f"[Optimizer] Sync completo: {len(self._so.saved_paths)} caminos "
            f"(optimizados fusionados)."
        )

    # ------------------------------------------------------------------
    # Diálogo de resultado
    # ------------------------------------------------------------------
    def _show_dialog(
        self,
        num_paths: int = 0,
        total_points: int = 0,
        error: Optional[str] = None,
    ) -> None:
        """Muestra un MessageBox con el resultado de la optimización."""
        try:
            techos        = getattr(self._so, "techos_is",       None) or []
            subdivisiones = getattr(self._so, "subdivisiones_is", None) or []
            tubos         = getattr(self._so, "tubos_is",        None) or []
            obstaculos    = getattr(self._so, "obstaculos",      None) or []
            nodo_list     = getattr(self._so, "nodo_list",       None) or []
            total_nodos   = sum(len(g) for g in nodo_list)

            info = (
                f"\n\n─────────────────────────\n"
                f"Techos        : {len(techos)}\n"
                f"Subdivisiones : {len(subdivisiones)}\n"
                f"Tubos         : {len(tubos)}\n"
                f"Obstáculos    : {len(obstaculos)}\n"
                f"Nodos         : {total_nodos}"
            )

            if error:
                PythonUtility.ShowMessageBox(
                    f"Error en optimización:\n\n{error}{info}",
                    PythonUtility.MB_OK,
                )
            else:
                PythonUtility.ShowMessageBox(
                    f"Camino óptimo generado correctamente.\n\n"
                    f"Caminos : {num_paths}\n"
                    f"Puntos  : {total_points}"
                    f"{info}",
                    PythonUtility.MB_OK,
                )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Helpers de estado del interactor
    # ------------------------------------------------------------------
    def _flush_active_polyline(self) -> None:
        """Guarda el tramo activo si el interactor está en create_mode.

        Si el usuario pulsó el botón sin haber finalizado el tramo con
        doble-click/ESC, los puntos están en ``interactor.points`` y no
        en ``active_paths``. Este método llama a ``_save_current_polyline``
        para moverlos antes de construir el input del optimizador.

        Nota: ``_save_current_polyline`` escribe en ``active_paths``, que en
        modo Automático apunta a ``saved_optimized_paths`` y en modo Manual
        apunta a ``saved_paths``. No hay referencia directa a ninguna de las
        dos variables; el enrutamiento lo gestiona la propiedad ``active_paths``.
        """
        create_mode = getattr(self._interactor, "create_mode", False)
        points = getattr(self._interactor, "points", [])
        if create_mode and len(points) >= 2:
            print(f"[Optimizer] Guardando tramo activo ({len(points)} puntos) antes de optimizar.")
            try:
                self._interactor._save_current_polyline()
            except Exception as ex:
                print(f"[Optimizer] Aviso: no se pudo guardar tramo activo: {ex}")

    def inject_test_points(
        self,
        n_caminos: int = 2,
        n_points: int = 5,
        z: float = 2947.5,
        step_mm: float = 5000.0,
        allow_diagonal: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        """Genera N caminos con puntos aleatorios y ángulos válidos.

        Construye el input completo del optimizador (formato ``Caminos_Optimos_Lib``)
        y lo almacena en ``_test_input_override`` para que ``run()`` lo use
        directamente, omitiendo el pipeline normal de ``saved_paths``.

        Estrategia de generación:
        - Cada camino parte de un origen espaciado para evitar solapamientos.
        - Los segmentos son ortogonales (0°/90°, siempre válidos). Con
          ``allow_diagonal=True`` se añaden también segmentos a 45°.
        - No se permite inversión de dirección (segmento de vuelta).
        - Roles: primer nodo = ``inicio``, último = ``fin``,
          intermedios = mezcla aleatoria de ``orden_obligatorio`` y ``orden_libre``.
        - Los nodos ``orden_obligatorio``/``inicio``/``fin`` se encadenan
          en orden (anteriores/siguientes). Los ``orden_libre`` flotan.

        Args:
            n_caminos: Número de caminos a generar (default 2).
            n_points: Nodos por camino incluyendo inicio y fin (mínimo 2).
            z: Altura Z en mm para todos los nodos (default 2947.5).
            step_mm: Longitud base de cada segmento en mm (default 5000).
            allow_diagonal: Si True, añade direcciones diagonales (45°/135°).
                Experimental — validar que el subtipo_tuberia los acepte.
            seed: Semilla aleatoria para resultados reproducibles (None = aleatorio).
        """
        import random

        if not _ALLPLAN_AVAILABLE:
            print("[Optimizer] inject_test_points: Allplan no disponible, omitiendo.")
            return

        rng = random.Random(seed)
        n_points = max(2, n_points)

        # Direcciones ortogonales garantizadas válidas (0°/90°).
        # Con allow_diagonal=True se añaden 45° (experimental).
        ORTHO = [(1, 0), (0, 1), (-1, 0), (0, -1)]          # E N W S
        DIAG  = [(1, 1), (-1, 1), (1, -1), (-1, -1)]         # NE NW SE SW
        DIRS  = ORTHO + (DIAG if allow_diagonal else [])
        N_DIR = len(DIRS)

        all_caminos_opt: List[Dict[str, Any]] = []
        all_preview_pts: List[Any] = []

        for ci in range(n_caminos):
            camino_id = f"camino_{ci}"

            # Origen: caminos separados en X para no solaparse
            spread = step_mm * (n_points + 2)
            ox = ci * spread
            oy = 0.0

            # ── Generar ruta aleatoria válida ────────────────────────────────
            # Regla: en cada paso se FUERZA un giro (izquierda o derecha).
            # Esto garantiza:
            #   1. Sin nodos colineales → sin ángulos 180°.
            #   2. Sin retrocesos      → sin ángulos 0°.
            #   3. Cada enlace de la cadena es ortogonal al anterior.
            pts: List[List[float]] = [[ox, oy]]
            dir_idx = rng.randint(0, N_DIR - 1)

            for _ in range(n_points - 1):
                # Forzar giro: solo ±1 (izq/der), nunca recto ni reversa.
                dir_idx = (dir_idx + rng.choice([-1, 1])) % N_DIR
                dx, dy = DIRS[dir_idx]
                length = step_mm * rng.uniform(1.0, 2.0)
                prev = pts[-1]
                pts.append([prev[0] + dx * length, prev[1] + dy * length])

            # ── Asignar roles: todos obligatorio (garantiza chain ortogonal) ─
            # Los nodos libre flotantes causarían links diagonales en el chain.
            roles_opt: List[str] = []
            for i in range(len(pts)):
                if i == 0:
                    roles_opt.append("inicio")
                elif i == len(pts) - 1:
                    roles_opt.append("fin")
                else:
                    roles_opt.append("orden_obligatorio")

            # ── Construir nodos y encadenar todos ────────────────────────────
            nodos: List[Dict[str, Any]] = []
            nids: List[str] = []

            for i, (pt, tipo) in enumerate(zip(pts, roles_opt)):
                nid = f"{camino_id}-N{i}"
                nids.append(nid)
                nodos.append({
                    "id": nid,
                    "tipo": tipo,
                    "coordenadas": {"x": round(pt[0], 1), "y": round(pt[1], 1), "z": z},
                    "anteriores": [],
                    "siguientes": [],
                })

            # Encadenar: inicio → obligatorio → … → fin
            nodo_by_id = {nd["id"]: nd for nd in nodos}
            for i, nid in enumerate(nids):
                nd = nodo_by_id[nid]
                if i > 0:
                    nd["anteriores"] = [nids[i - 1]]
                if i < len(nids) - 1:
                    nd["siguientes"] = [nids[i + 1]]

            all_caminos_opt.append({"id": camino_id, "nombre": camino_id, "nodos": nodos})

            for pt in pts:
                all_preview_pts.append(AllplanGeo.Point3D(pt[0], pt[1], z))

        # ── Techo automático a partir de bounding box ────────────────────────
        all_nodos_flat = [nd for cam in all_caminos_opt for nd in cam["nodos"]]
        techo = self._auto_techo(all_nodos_flat, z_fallback=z)

        # ── Input completo del optimizador ───────────────────────────────────
        optimizer_input: Dict[str, Any] = {
            "id": "test_generado",
            "nombre": f"Test {n_caminos} caminos × {n_points} nodos",
            "techo": techo,
            "subdivisiones_is": [],
            "tubos_is": [],
            "caminos": all_caminos_opt,
            "obstaculos": [],
            "configuracion": {
                "subtipo_tuberia": "extraccion_impulsion",
                "estrategia_colision": [], # "saltar"
            },
        }

        # ── Persistir override y puntos de preview ───────────────────────────
        self._interactor._test_input_override = optimizer_input
        self._interactor._free_points = all_preview_pts
        self._interactor._free_point_roles = []  # no se usan en modo override

        total_pts = sum(len(cam["nodos"]) for cam in all_caminos_opt)
        print(
            f"[Optimizer] inject_test_points: {n_caminos} camino(s), "
            f"{total_pts} nodos totales — mueve el mouse para ver los puntos."
        )
        self._draw_free_points_preview()

    def _draw_free_points_preview(self) -> None:
        """Construye las cruces y las persiste en ``_optimizer_preview_elems``.

        Los elementos NO se dibujan directamente aquí — el preview de Allplan
        se borra en el siguiente tick del mouse si se llama desde un evento.
        El patrón correcto (igual que soportes) es guardar los elementos en
        ``interactor._optimizer_preview_elems`` y dejar que ``_draw_preview``
        los renderice como overlay en cada ``OnMouseMove``.
        """
        if not _ALLPLAN_AVAILABLE:
            return

        free_pts = getattr(self._interactor, "_free_points", [])

        if not free_pts:
            self._interactor._optimizer_preview_elems = []
            return

        try:
            prop = AllplanBaseElements.CommonProperties()
            prop.GetGlobalProperties()
            prop.Color = 7          # magenta
            prop.ColorByLayer = False
            prop.Pen = 3
            prop.PenByLayer = False

            elems = []
            size = 500.0
            half = size * 0.5
            for pt in free_pts:
                px, py, pz = float(pt.X), float(pt.Y), float(pt.Z)
                elems += [
                    AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(
                        AllplanGeo.Point3D(px - half, py, pz),
                        AllplanGeo.Point3D(px + half, py, pz),
                    )),
                    AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(
                        AllplanGeo.Point3D(px, py - half, pz),
                        AllplanGeo.Point3D(px, py + half, pz),
                    )),
                    AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(
                        AllplanGeo.Point3D(px, py, pz - half),
                        AllplanGeo.Point3D(px, py, pz + half),
                    )),
                ]

            # Persistir → _draw_preview los renderiza en cada OnMouseMove
            self._interactor._optimizer_preview_elems = elems
            print(f"[Optimizer] {len(free_pts)} cruces listas — mueve el mouse para verlas.")
        except Exception as ex:
            print(f"[Optimizer] Error construyendo cruces: {ex}")
            self._interactor._optimizer_preview_elems = []

    # ------------------------------------------------------------------

    @staticmethod
    def _auto_techo(nodos: List[Dict[str, Any]], z_fallback: float = 2947.5) -> List[Dict[str, Any]]:
        """Genera un techo plano rectangular a partir del bounding box de los nodos.

        Usa directamente la altura Z de los nodos sin aplicar ningún offset.
        Se añade un margen de 2000 mm en XY alrededor para que el optimizador
        tenga espacio.

        Args:
            nodos: Lista de nodos con ``coordenadas`` en formato ``{"x", "y", "z"}``.
            z_fallback: Z a usar si no hay nodos (default 2947.5).

        Returns:
            Lista con un dict de techo rectangular compatible con el optimizador.
        """
        xs, ys, zs = [], [], []
        for nd in nodos:
            c = nd.get("coordenadas", {})
            if isinstance(c, dict):
                xs.append(c.get("x", 0))
                ys.append(c.get("y", 0))
                zs.append(c.get("z", z_fallback))

        if not xs:
            z_val = z_fallback
            return [{"id": "techo_auto", "vertices": [
                {"x": -2000, "y": -2000, "z": z_val},
                {"x": 20000, "y": -2000, "z": z_val},
                {"x": 20000, "y": 20000, "z": z_val},
                {"x": -2000, "y": 20000, "z": z_val},
            ]}]

        margin = 2000
        z_val = min(zs)
        return [{"id": "techo_auto", "vertices": [
            {"x": min(xs) - margin, "y": min(ys) - margin, "z": z_val},
            {"x": max(xs) + margin, "y": min(ys) - margin, "z": z_val},
            {"x": max(xs) + margin, "y": max(ys) + margin, "z": z_val},
            {"x": min(xs) - margin, "y": max(ys) + margin, "z": z_val},
        ]}]

    @staticmethod
    def _extract_xyz(pt: Any) -> Tuple[float, float, float]:
        """Extrae (x, y, z) de un Point3D de Allplan o de una lista/tupla."""
        if hasattr(pt, "X") and hasattr(pt, "Y") and hasattr(pt, "Z"):
            return float(pt.X), float(pt.Y), float(pt.Z)
        if isinstance(pt, (list, tuple)) and len(pt) >= 3:
            return float(pt[0]), float(pt[1]), float(pt[2])
        return 0.0, 0.0, 0.0

    @staticmethod
    def _pt_key(pt: Any) -> Tuple[float, float, float]:
        """Clave redondeada a 0.1 mm para comparar posiciones de puntos."""
        if hasattr(pt, "X") and hasattr(pt, "Y") and hasattr(pt, "Z"):
            return (round(pt.X, 1), round(pt.Y, 1), round(pt.Z, 1))
        if isinstance(pt, (list, tuple)) and len(pt) >= 3:
            return (round(pt[0], 1), round(pt[1], 1), round(pt[2], 1))
        return (0.0, 0.0, 0.0)

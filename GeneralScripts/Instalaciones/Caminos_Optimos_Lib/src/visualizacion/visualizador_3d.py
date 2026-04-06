"""
Modulo de visualizacion 3D para el sistema de tuberias.

Utiliza plotly para generar graficos 3D interactivos.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..modelos.punto import Punto3D
from ..modelos.techo import Techo
from ..modelos.tuberia import Tuberia, SegmentoTuberia, SubtipoTuberia
from ..modelos.obstaculo import Obstaculo
from ..etiquetas import label_sub as _label_sub


class Visualizador3D:
    """
    Visualizador 3D interactivo para el sistema de tuberias.
    
    Permite visualizar:
    - Techos inclinados con vertices IS
    - Puntos de conexion (obligatorios y libres)
    - Tuberias con sus dimensiones
    - Obstaculos
    """
    
    # Colores segun imagen de referencia
    COLORES = {
        'techo': 'rgba(220, 220, 220, 0.15)',
        'techo_borde': 'rgb(150, 150, 150)',
        'is_subdivision': 'rgb(148, 103, 189)',  # Purpura para IS
        'punto_inicio': 'rgb(0, 200, 83)',       # Verde triangulo arriba
        'punto_fin': 'rgb(213, 0, 0)',           # Rojo triangulo abajo
        'punto_obligatorio': 'rgb(255, 152, 0)', # Naranja cuadrado
        'punto_libre': 'rgb(33, 150, 243)',      # Azul circulo
        'camino_techo': 'rgb(244, 67, 54)',      # Rojo
        'camino_pared': 'rgb(33, 150, 243)',     # Azul
        'camino_suelo': 'rgb(76, 175, 80)',      # Verde
        'obstaculo': 'rgba(255, 152, 0, 0.7)',   # Naranja
        'obstaculo_borde': 'rgb(230, 126, 34)',
        'punto_union': 'rgb(255, 105, 180)',        # Rosa para puntos U
        'tubo_is': 'rgb(255, 140, 0)',                  # Naranja para tubos IS
        'soporte_estandar': 'rgb(0, 180, 0)',           # Verde para soportes OMEGA
        'soporte_varifix': 'rgb(220, 50, 50)',           # Rojo para soportes ZETA
    }
    
    def __init__(self, titulo: str = "Visualizacion de Tuberias"):
        """
        Inicializa el visualizador.
        
        Args:
            titulo: Titulo de la visualizacion
        """
        self.titulo = titulo
        self.figura = go.Figure()
        # Ancla invisible en (0,0,0) para que aspectmode='data' incluya el origen
        self.figura.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers', marker=dict(size=0, opacity=0),
            showlegend=False, hoverinfo='skip'
        ))
        self._configurar_layout()
    
    def _configurar_layout(self) -> None:
        """Configura el layout de la figura con botones de vistas."""
        self.figura.update_layout(
            title=dict(
                text=self.titulo,
                font=dict(size=20, color='white', family='Arial Black'),
                x=0.5,
                xanchor='center',
                y=0.98,
                yanchor='top'
            ),
            scene=dict(
                xaxis_title='X (mm)',
                yaxis_title='Y (mm)',
                zaxis_title='Z (mm)',
                aspectmode='data',  # Escala 1:1:1 real (1000mm = 1000mm en todos los ejes)
                camera=dict(
                    eye=dict(x=1.5, y=-1.5, z=1.0),
                    up=dict(x=0, y=0, z=1),
                    projection=dict(type='orthographic')
                ),
                xaxis=dict(
                    gridcolor='rgba(80, 80, 80, 0.6)', 
                    showbackground=True, 
                    backgroundcolor='rgb(30, 30, 30)',
                    rangemode='tozero',
                    tickangle=0,
                    tickfont=dict(color='rgb(200, 200, 200)'),
                    title=dict(font=dict(color='rgb(200, 200, 200)'))
                ),
                yaxis=dict(
                    gridcolor='rgba(80, 80, 80, 0.6)', 
                    showbackground=True, 
                    backgroundcolor='rgb(30, 30, 30)',
                    rangemode='tozero',
                    tickangle=0,
                    tickfont=dict(color='rgb(200, 200, 200)'),
                    title=dict(font=dict(color='rgb(200, 200, 200)'))
                ),
                zaxis=dict(
                    gridcolor='rgba(80, 80, 80, 0.6)', 
                    showbackground=True, 
                    backgroundcolor='rgb(30, 30, 30)',
                    rangemode='tozero',
                    tickangle=0,
                    tickfont=dict(color='rgb(200, 200, 200)'),
                    title=dict(font=dict(color='rgb(200, 200, 200)'))
                ),
            ),
            showlegend=True,
            legend=dict(
                title=dict(text='Elementos del Camino', font=dict(size=12, color='rgb(200, 200, 200)')),
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(30, 30, 30, 0.9)',
                bordercolor='rgb(80, 80, 80)',
                borderwidth=1,
                font=dict(color='rgb(200, 200, 200)')
            ),
            margin=dict(l=0, r=0, t=60, b=60),
            paper_bgcolor='rgb(20, 20, 20)',
            # Botones en la parte INFERIOR - 7 vistas con vector UP para alinear ejes
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=[
                        dict(
                            args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": 2.5},
                                   "scene.camera.up": {"x": 0, "y": 1, "z": 0},
                                   "scene.camera.projection.type": "orthographic"}],
                            label="Superior",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": -2.5},
                                   "scene.camera.up": {"x": 0, "y": 1, "z": 0},
                                   "scene.camera.projection.type": "orthographic"}],
                            label="Inferior",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": 0, "y": -2.5, "z": 0},
                                   "scene.camera.up": {"x": 0, "y": 0, "z": 1},
                                   "scene.camera.projection.type": "orthographic"}],
                            label="Frontal",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": 0, "y": 2.5, "z": 0},
                                   "scene.camera.up": {"x": 0, "y": 0, "z": 1},
                                   "scene.camera.projection.type": "orthographic"}],
                            label="Posterior",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": -2.5, "y": 0, "z": 0},
                                   "scene.camera.up": {"x": 0, "y": 0, "z": 1},
                                   "scene.camera.projection.type": "orthographic"}],
                            label="Lat. Izq",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": 2.5, "y": 0, "z": 0},
                                   "scene.camera.up": {"x": 0, "y": 0, "z": 1},
                                   "scene.camera.projection.type": "orthographic"}],
                            label="Lat. Der",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": 1.5, "y": -1.5, "z": 1.0},
                                   "scene.camera.up": {"x": 0, "y": 0, "z": 1},
                                   "scene.camera.projection.type": "orthographic"}],
                            label="Isometrica",
                            method="relayout"
                        ),
                    ],
                    pad={"r": 5, "t": 5},
                    showactive=True,
                    x=0.5,
                    xanchor="center",
                    y=0.02,
                    yanchor="bottom",
                    font=dict(size=9),
                    bgcolor='rgba(240,240,240,0.9)'
                ),
            ]
        )
    
    def agregar_techo(
        self, 
        techo: Techo,
        nombre: str = "Techo",
        mostrar_vertices: bool = True,
        color_superficie: Optional[str] = None,
        color_borde: Optional[str] = None
    ) -> 'Visualizador3D':
        """
        Agrega un techo a la visualizacion.
        
        Args:
            techo: Techo a visualizar
            nombre: Nombre para la leyenda
            mostrar_vertices: Si mostrar etiquetas de vertices IS
            color_superficie: Color de la superficie
            color_borde: Color del borde
        
        Returns:
            self para encadenamiento
        """
        if len(techo.vertices) < 3:
            return self
        
        color_sup = color_superficie or self.COLORES['techo']
        color_brd = color_borde or self.COLORES['techo_borde']
        
        # Obtener coordenadas
        xs = [v.punto.x for v in techo.vertices]
        ys = [v.punto.y for v in techo.vertices]
        zs = [v.punto.z for v in techo.vertices]
        
        # Cerrar el poligono
        xs.append(xs[0])
        ys.append(ys[0])
        zs.append(zs[0])
        
        # Superficie del techo (mesh3d)
        if len(techo.vertices) >= 4:
            self.figura.add_trace(go.Mesh3d(
                x=[v.punto.x for v in techo.vertices],
                y=[v.punto.y for v in techo.vertices],
                z=[v.punto.z for v in techo.vertices],
                color=color_sup,
                opacity=0.3,
                name=f"{nombre} (superficie)",
                showlegend=True,
                i=[0, 0],
                j=[1, 2],
                k=[2, 3]
            ))
        
        # Bordes del techo
        self.figura.add_trace(go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode='lines',
            line=dict(color=color_brd, width=3),
            name=f"{nombre} (borde)",
            showlegend=False
        ))
        
        # Etiquetas de vertices IS
        if mostrar_vertices:
            for vertice in techo.vertices:
                self.figura.add_trace(go.Scatter3d(
                    x=[vertice.punto.x],
                    y=[vertice.punto.y],
                    z=[vertice.punto.z + 50],  # Elevar etiqueta
                    mode='text',
                    text=[vertice.id],
                    textposition='top center',
                    textfont=dict(size=12, color='black'),
                    showlegend=False
                ))
        
        return self
    
    def agregar_is_subdivision(
        self,
        techo: Techo,
        nombre: str = "IS (subdivision)"
    ) -> 'Visualizador3D':
        """
        Agrega los IS como lineas discontinuas purpuras (estilo de referencia).
        """
        if len(techo.vertices) < 4:
            return self
        
        color_is = self.COLORES['is_subdivision']
        
        # Dibujar bordes del IS con linea discontinua
        vertices = techo.vertices
        for i in range(len(vertices)):
            v1 = vertices[i].punto
            v2 = vertices[(i + 1) % len(vertices)].punto
            
            self.figura.add_trace(go.Scatter3d(
                x=[v1.x, v2.x],
                y=[v1.y, v2.y],
                z=[v1.z, v2.z],
                mode='lines',
                line=dict(color=color_is, width=3, dash='dash'),
                name=nombre if i == 0 else None,
                showlegend=(i == 0),
                legendgroup='is'
            ))
        
        # Etiquetas de vertices IS
        for vertice in vertices:
            self.figura.add_trace(go.Scatter3d(
                x=[vertice.punto.x],
                y=[vertice.punto.y],
                z=[vertice.punto.z + 80],
                mode='text',
                text=[vertice.id],
                textposition='top center',
                textfont=dict(size=11, color=color_is),
                showlegend=False
            ))
        
        return self
    
    def agregar_punto_inicio(
        self,
        punto: Punto3D,
        nombre: str = "Punto A (Inicio)",
        camino_idx: int = None
    ) -> 'Visualizador3D':
        """Agrega punto de inicio con triangulo verde hacia arriba."""
        etiq = _label_sub('A', camino_idx) if camino_idx else (punto.id or 'A')
        self.figura.add_trace(go.Scatter3d(
            x=[punto.x],
            y=[punto.y],
            z=[punto.z],
            mode='markers',
            marker=dict(
                size=8,
                color=self.COLORES['punto_inicio'],
                symbol='diamond',
                line=dict(color='black', width=1)
            ),
            name=nombre,
            text=f"{etiq}<br>X: {punto.x:.0f}<br>Y: {punto.y:.0f}<br>Z: {punto.z:.0f}",
            hoverinfo='text'
        ))
        # Etiqueta visible
        self.figura.add_trace(go.Scatter3d(
            x=[punto.x], y=[punto.y], z=[punto.z + 70],
            mode='text',
            text=[etiq],
            textfont=dict(size=20, color=self.COLORES['punto_inicio']),
            showlegend=False
        ))
        return self
    
    def agregar_punto_fin(
        self,
        punto: Punto3D,
        nombre: str = "Punto B (Fin)",
        camino_idx: int = None
    ) -> 'Visualizador3D':
        """Agrega punto final con triangulo rojo hacia abajo."""
        etiq = _label_sub('B', camino_idx) if camino_idx else (punto.id or 'B')
        self.figura.add_trace(go.Scatter3d(
            x=[punto.x],
            y=[punto.y],
            z=[punto.z],
            mode='markers',
            marker=dict(
                size=8,
                color=self.COLORES['punto_fin'],
                symbol='diamond',
                line=dict(color='black', width=1)
            ),
            name=nombre,
            text=f"{etiq}<br>X: {punto.x:.0f}<br>Y: {punto.y:.0f}<br>Z: {punto.z:.0f}",
            hoverinfo='text'
        ))
        # Etiqueta visible
        self.figura.add_trace(go.Scatter3d(
            x=[punto.x], y=[punto.y], z=[punto.z + 70],
            mode='text',
            text=[etiq],
            textfont=dict(size=20, color=self.COLORES['punto_fin']),
            showlegend=False
        ))
        return self
    
    def agregar_puntos_intermedios(
        self,
        puntos_obligatorios: List[Punto3D] = None,
        puntos_libres: List[Punto3D] = None,
        puntos_conexion: List[Punto3D] = None,
        mostrar_etiquetas: bool = True,
        camino_idx: int = None
    ) -> 'Visualizador3D':
        """
        Agrega los 3 tipos de puntos intermedios:
        - Obligatorios: cuadrado naranja, etiqueta O₁, O₂...
        - Libres: circulo azul, etiqueta L (sin numero)
        - Conexion/Modelo: x morada pequena, etiqueta M₁, M₂...
        
        Si un punto del modelo coincide con uno libre, prevalece el libre.
        """
        puntos_obligatorios = puntos_obligatorios or []
        puntos_libres = puntos_libres or []
        puntos_conexion = puntos_conexion or []
        
        # Filtrar puntos del modelo que coinciden con libres (prevalece libre)
        def punto_coincide(p1, p2, tolerancia=50):
            return (abs(p1.x - p2.x) < tolerancia and 
                    abs(p1.y - p2.y) < tolerancia and 
                    abs(p1.z - p2.z) < tolerancia)
        
        puntos_modelo_filtrados = []
        for pm in puntos_conexion:
            coincide = any(punto_coincide(pm, pl) for pl in puntos_libres)
            if not coincide:
                puntos_modelo_filtrados.append(pm)
        puntos_conexion = puntos_modelo_filtrados
        
        # Puntos obligatorios - cuadrados naranjas
        if puntos_obligatorios:
            etiquetas_o = [_label_sub('O', camino_idx, i + 1) for i in range(len(puntos_obligatorios))]
            self.figura.add_trace(go.Scatter3d(
                x=[p.x for p in puntos_obligatorios],
                y=[p.y for p in puntos_obligatorios],
                z=[p.z for p in puntos_obligatorios],
                mode='markers',
                marker=dict(
                    size=10,
                    color=self.COLORES['punto_obligatorio'],
                    symbol='square',
                    line=dict(color='black', width=1)
                ),
                name='Pto. Obligatorio (O)',
                hoverinfo='text',
                text=[f"{etiquetas_o[i]}<br>X:{p.x:.0f} Y:{p.y:.0f} Z:{p.z:.0f}" 
                      for i, p in enumerate(puntos_obligatorios)]
            ))
        
        # Puntos libres - circulos azules
        if puntos_libres:
            etiquetas_l = [_label_sub('L', camino_idx, i + 1) for i in range(len(puntos_libres))]
            self.figura.add_trace(go.Scatter3d(
                x=[p.x for p in puntos_libres],
                y=[p.y for p in puntos_libres],
                z=[p.z for p in puntos_libres],
                mode='markers',
                marker=dict(
                    size=8,
                    color=self.COLORES['punto_libre'],
                    symbol='circle',
                    line=dict(color='white', width=1)
                ),
                name='Pto. Libre (L)',
                hoverinfo='text',
                text=[f"{etiquetas_l[i]}<br>X:{p.x:.0f} Y:{p.y:.0f} Z:{p.z:.0f}" 
                      for i, p in enumerate(puntos_libres)]
            ))
        
        # Puntos de conexion/modelo - x morada MAS PEQUENA
        if puntos_conexion:
            etiquetas_m = [_label_sub('M', camino_idx, i + 1) for i in range(len(puntos_conexion))]
            self.figura.add_trace(go.Scatter3d(
                x=[p.x for p in puntos_conexion],
                y=[p.y for p in puntos_conexion],
                z=[p.z for p in puntos_conexion],
                mode='markers',
                marker=dict(
                    size=5,  # Mas pequeno que libres
                    color='rgb(156, 39, 176)',  # Morado
                    symbol='x',
                    line=dict(color='white', width=1)
                ),
                name='Pto. Modelo (M)',
                hoverinfo='text',
                text=[f"{etiquetas_m[i]}<br>X:{p.x:.0f} Y:{p.y:.0f} Z:{p.z:.0f}" 
                      for i, p in enumerate(puntos_conexion)]
            ))
        
        # Etiquetas con subindices
        if mostrar_etiquetas:
            # Obligatorios
            for i, p in enumerate(puntos_obligatorios):
                etiq = _label_sub('O', camino_idx, i + 1)
                self.figura.add_trace(go.Scatter3d(
                    x=[p.x], y=[p.y], z=[p.z + 60],
                    mode='text',
                    text=[etiq],
                    textfont=dict(size=20, color=self.COLORES['punto_obligatorio']),
                    showlegend=False
                ))
            # Libres
            for i, p in enumerate(puntos_libres):
                etiq = _label_sub('L', camino_idx, i + 1)
                self.figura.add_trace(go.Scatter3d(
                    x=[p.x], y=[p.y], z=[p.z + 60],
                    mode='text',
                    text=[etiq],
                    textfont=dict(size=20, color=self.COLORES['punto_libre']),
                    showlegend=False
                ))
            # Modelo
            for i, p in enumerate(puntos_conexion):
                etiq = _label_sub('M', camino_idx, i + 1)
                self.figura.add_trace(go.Scatter3d(
                    x=[p.x], y=[p.y], z=[p.z + 60],
                    mode='text',
                    text=[etiq],
                    textfont=dict(size=20, color='rgb(156, 39, 176)'),
                    showlegend=False
                ))
        
        return self
    
    def agregar_borde_techo(
        self,
        vertices_techo: List[List[float]],
        nombre: str = "Techo (borde)"
    ) -> 'Visualizador3D':
        """
        Agrega el borde del techo con color naranja.
        
        Args:
            vertices_techo: Lista de vertices [[x,y,z], ...]
        """
        if len(vertices_techo) < 3:
            return self
        
        # Cerrar el poligono
        xs = [v[0] for v in vertices_techo] + [vertices_techo[0][0]]
        ys = [v[1] for v in vertices_techo] + [vertices_techo[0][1]]
        zs = [v[2] for v in vertices_techo] + [vertices_techo[0][2]]
        
        # Borde marron solido
        self.figura.add_trace(go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode='lines',
            line=dict(color='rgb(139, 69, 19)', width=4),  # Marron
            name=nombre
        ))
        
        return self
    
    def agregar_plano_tuberia(
        self,
        vertices_techo: List[List[float]],
        distancia_techo_mm: float,
        nombre: str = "Cota"
    ) -> 'Visualizador3D':
        """
        Agrega un plano gris semi-transparente paralelo al techo,
        desplazado distancia_techo_mm a lo largo de la normal del techo.
        Representa el plano donde circulan las tuberías y se ubican los obstáculos.
        """
        if len(vertices_techo) < 3:
            return self
        
        # Calcular normal del techo
        v0 = np.array(vertices_techo[0])
        v1 = np.array(vertices_techo[1])
        v2 = np.array(vertices_techo[2])
        normal = np.cross(v1 - v0, v2 - v0)
        norma = np.linalg.norm(normal)
        if norma > 0.001:
            normal = normal / norma
        if normal[2] < 0:
            normal = -normal
        
        # Desplazar cada vértice del techo a lo largo de la normal
        offset = normal * distancia_techo_mm
        vertices_plano = [
            [v[0] + offset[0], v[1] + offset[1], v[2] + offset[2]]
            for v in vertices_techo
        ]
        
        # Superficie (Mesh3d)
        xs = [v[0] for v in vertices_plano]
        ys = [v[1] for v in vertices_plano]
        zs = [v[2] for v in vertices_plano]
        
        n = len(vertices_plano)
        if n >= 3:
            # Triangulación fan desde el vértice 0
            i_list = [0] * (n - 2)
            j_list = list(range(1, n - 1))
            k_list = list(range(2, n))
            
            self.figura.add_trace(go.Mesh3d(
                x=xs, y=ys, z=zs,
                i=i_list, j=j_list, k=k_list,
                color='rgba(144, 238, 144, 0.35)',
                opacity=0.35,
                name=nombre,
                showlegend=True
            ))
        
        # Borde del plano (línea gris discontinua)
        bx = xs + [xs[0]]
        by = ys + [ys[0]]
        bz = zs + [zs[0]]
        self.figura.add_trace(go.Scatter3d(
            x=bx, y=by, z=bz,
            mode='lines',
            line=dict(color='rgb(100, 200, 100)', width=2),
            name=f"{nombre} (borde)",
            showlegend=False
        ))
        
        return self
    
    def agregar_subdivisiones_is(
        self,
        lista_is: List[dict],
        color: Optional[str] = None
    ) -> 'Visualizador3D':
        """
        Agrega las subdivisiones IS dentro del techo.
        
        Args:
            lista_is: Lista de dicts con 'id' y 'vertices' [[x,y,z], ...]
        """
        color = color or self.COLORES['is_subdivision']
        
        for i, is_data in enumerate(lista_is):
            vertices = is_data.get('vertices', [])
            is_id = is_data.get('id', f'IS{i+1}')
            
            if len(vertices) < 4:
                continue
            
            # Cerrar el poligono
            xs = [v[0] for v in vertices] + [vertices[0][0]]
            ys = [v[1] for v in vertices] + [vertices[0][1]]
            zs = [v[2] for v in vertices] + [vertices[0][2]]
            
            # Linea discontinua purpura
            self.figura.add_trace(go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode='lines',
                line=dict(color=color, width=2, dash='dash'),
                name='IS (subdivision)' if i == 0 else None,
                showlegend=(i == 0),
                legendgroup='is_sub'
            ))
            
            # Etiqueta del IS
            centro_x = sum(v[0] for v in vertices) / len(vertices)
            centro_y = sum(v[1] for v in vertices) / len(vertices)
            centro_z = sum(v[2] for v in vertices) / len(vertices)
            
            self.figura.add_trace(go.Scatter3d(
                x=[centro_x],
                y=[centro_y],
                z=[centro_z + 50],
                mode='text',
                text=[is_id],
                textfont=dict(size=10, color=color),
                showlegend=False
            ))
        
        return self
    
    def agregar_puntos_union(self, puntos_u: List[Punto3D], camino_idx: int = None) -> 'Visualizador3D':
        """Agrega puntos de union (U) entre IS como marcadores rosados."""
        if not puntos_u:
            return self
        
        color = self.COLORES['punto_union']
        xs = [p.x for p in puntos_u]
        ys = [p.y for p in puntos_u]
        zs = [p.z for p in puntos_u]
        etiquetas = [_label_sub('U', camino_idx, i + 1) for i in range(len(puntos_u))]
        textos = [f'{etiq}<br>({x:.0f}, {y:.0f}, {z:.0f})' 
                  for etiq, x, y, z in zip(etiquetas, xs, ys, zs)]
        
        nombre_leyenda = f'Union (U) cam.{camino_idx}' if camino_idx else 'Union IS (U)'
        self.figura.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode='markers+text',
            marker=dict(size=7, color=color, symbol='diamond'),
            text=etiquetas,
            textposition='top center',
            textfont=dict(size=20, color=color),
            hovertext=textos,
            hoverinfo='text',
            name=nombre_leyenda,
            showlegend=True,
            legendgroup='puntos_u'
        ))
        
        return self
    
    def _generar_cilindro(self, p1: Punto3D, p2: Punto3D, radio: float, n_lados: int = 16):
        """
        Genera los vertices e indices para un cilindro entre dos puntos.
        
        Returns:
            (x, y, z, i, j, k) para Mesh3d
        """
        import numpy as np
        
        # Vector direccion del cilindro
        d = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
        longitud = np.linalg.norm(d)
        if longitud < 0.001:
            return None
        d = d / longitud
        
        # Encontrar vectores perpendiculares
        if abs(d[2]) < 0.9:
            perp1 = np.cross(d, [0, 0, 1])
        else:
            perp1 = np.cross(d, [1, 0, 0])
        perp1 = perp1 / np.linalg.norm(perp1)
        perp2 = np.cross(d, perp1)
        
        # Generar vertices del cilindro
        vertices_x = []
        vertices_y = []
        vertices_z = []
        
        for t in [0, 1]:  # Dos tapas
            centro = np.array([p1.x, p1.y, p1.z]) + t * longitud * d
            for i in range(n_lados):
                angulo = 2 * np.pi * i / n_lados
                punto = centro + radio * (np.cos(angulo) * perp1 + np.sin(angulo) * perp2)
                vertices_x.append(punto[0])
                vertices_y.append(punto[1])
                vertices_z.append(punto[2])
        
        # Generar caras (triangulos)
        i_list, j_list, k_list = [], [], []
        
        # Caras laterales
        for idx in range(n_lados):
            next_idx = (idx + 1) % n_lados
            # Triangulo 1
            i_list.append(idx)
            j_list.append(next_idx)
            k_list.append(idx + n_lados)
            # Triangulo 2
            i_list.append(next_idx)
            j_list.append(next_idx + n_lados)
            k_list.append(idx + n_lados)
        
        return vertices_x, vertices_y, vertices_z, i_list, j_list, k_list
    
    def agregar_tuberia_3d(
        self,
        puntos: List[Punto3D],
        radio: float,
        nombre: str = "Tuberia",
        color: str = 'rgba(100, 149, 237, 0.6)'  # Azul semi-transparente
    ) -> 'Visualizador3D':
        """
        Agrega cilindros 3D representando la tuberia fisica.
        
        Args:
            puntos: Lista de puntos del camino (ejes)
            radio: Radio del tubo en mm
            nombre: Nombre para la leyenda
            color: Color del tubo
        """
        if len(puntos) < 2:
            return self
        
        # Crear un cilindro por cada segmento
        for idx in range(len(puntos) - 1):
            p1, p2 = puntos[idx], puntos[idx + 1]
            cilindro = self._generar_cilindro(p1, p2, radio)
            
            if cilindro:
                x, y, z, i, j, k = cilindro
                self.figura.add_trace(go.Mesh3d(
                    x=x, y=y, z=z,
                    i=i, j=j, k=k,
                    color=color,
                    opacity=0.6,
                    name=nombre if idx == 0 else None,
                    showlegend=(idx == 0),
                    legendgroup=nombre,
                    hoverinfo='name'
                ))
        
        return self
    
    def agregar_camino(
        self,
        puntos: List[Punto3D],
        nombre: str = "Camino",
        mostrar_vertices: bool = True,
        puntos_excluir: List[Punto3D] = None,
        color: str = None,
        camino_idx: int = None
    ) -> 'Visualizador3D':
        """
        Agrega un camino con puntos de doblez enumerados.
        
        Args:
            puntos: Lista de puntos del camino
            nombre: Nombre del camino
            mostrar_vertices: Si mostrar los vertices/codos del camino
            puntos_excluir: Puntos a excluir de las etiquetas C (ej: libres, obligatorios)
            color: Color de la linea del camino (default: azul)
        """
        if len(puntos) < 2:
            return self
        
        puntos_excluir = puntos_excluir or []
        color_linea = color or self.COLORES['camino_pared']
        
        # Funcion para verificar coincidencia
        def punto_coincide(p1, p2, tolerancia=50):
            return (abs(p1.x - p2.x) < tolerancia and 
                    abs(p1.y - p2.y) < tolerancia and 
                    abs(p1.z - p2.z) < tolerancia)
        
        # Linea del camino
        self.figura.add_trace(go.Scatter3d(
            x=[p.x for p in puntos],
            y=[p.y for p in puntos],
            z=[p.z for p in puntos],
            mode='lines',
            line=dict(color=color_linea, width=5),
            name=nombre
        ))
        
        # Vertices/codos del camino (puntos intermedios, no inicio ni fin)
        # Solo mostrar puntos donde hay un cambio de direccion real (angulo != 180°)
        if mostrar_vertices and len(puntos) > 2:
            import math as _math
            vertices = []
            for i in range(1, len(puntos) - 1):
                v = puntos[i]
                # Excluir puntos que coinciden con obligatorios/libres
                if any(punto_coincide(v, pe) for pe in puntos_excluir):
                    continue
                # Calcular angulo en este punto
                dx1 = v.x - puntos[i-1].x
                dy1 = v.y - puntos[i-1].y
                dz1 = v.z - puntos[i-1].z
                dx2 = puntos[i+1].x - v.x
                dy2 = puntos[i+1].y - v.y
                dz2 = puntos[i+1].z - v.z
                len1 = _math.sqrt(dx1**2 + dy1**2 + dz1**2)
                len2 = _math.sqrt(dx2**2 + dy2**2 + dz2**2)
                if len1 < 1 or len2 < 1:
                    continue
                cos_ang = (dx1*dx2 + dy1*dy2 + dz1*dz2) / (len1 * len2)
                cos_ang = max(-1, min(1, cos_ang))
                angulo = _math.degrees(_math.acos(cos_ang))
                # Solo mostrar si NO es linea recta (angulo entre vectores > 5°)
                if angulo > 5.0:
                    vertices.append(v)
            
            if vertices:
                # Generar etiquetas: C₍camino₋codo₎ para multi-camino, C₁ para single
                etiquetas = []
                for i in range(len(vertices)):
                    etiquetas.append(_label_sub('C', camino_idx, i + 1))
                
                # Puntos de doblez - color cyan/turquesa
                nombre_leyenda = f'Codo (C) cam.{camino_idx}' if camino_idx else 'Pto. Camino (C)'
                self.figura.add_trace(go.Scatter3d(
                    x=[p.x for p in vertices],
                    y=[p.y for p in vertices],
                    z=[p.z for p in vertices],
                    mode='markers',
                    marker=dict(
                        size=6,
                        color='rgb(0, 188, 212)',  # Cyan
                        symbol='diamond',
                        line=dict(color='white', width=1)
                    ),
                    name=nombre_leyenda,
                    hoverinfo='text',
                    text=[f"{etiq}<br>X:{p.x:.0f} Y:{p.y:.0f} Z:{p.z:.0f}" 
                          for etiq, p in zip(etiquetas, vertices)]
                ))
                
                # Etiquetas visibles
                for etiq, p in zip(etiquetas, vertices):
                    self.figura.add_trace(go.Scatter3d(
                        x=[p.x], y=[p.y], z=[p.z + 50],
                        mode='text',
                        text=[etiq],
                        textfont=dict(size=20, color='rgb(0, 188, 212)'),
                        showlegend=False
                    ))
        
        return self
    
    def agregar_etiqueta_zona(
        self,
        punto: Punto3D,
        nombre_zona: str = "Zona_A"
    ) -> 'Visualizador3D':
        """Agrega una etiqueta de zona con fondo."""
        self.figura.add_trace(go.Scatter3d(
            x=[punto.x],
            y=[punto.y],
            z=[punto.z],
            mode='text',
            text=[f"<b>{nombre_zona}</b>"],
            textfont=dict(size=14, color='black'),
            textposition='middle center',
            showlegend=False
        ))
        return self
    
    def agregar_puntos(
        self,
        puntos: List[Punto3D],
        nombre: str = "Puntos",
        color: Optional[str] = None,
        tamano: int = 8,
        simbolo: str = 'circle',
        mostrar_etiquetas: bool = True
    ) -> 'Visualizador3D':
        """
        Agrega una lista de puntos a la visualizacion.
        
        Args:
            puntos: Lista de puntos
            nombre: Nombre para la leyenda
            color: Color de los puntos
            tamano: Tamano de los marcadores
            simbolo: Simbolo del marcador
            mostrar_etiquetas: Si mostrar IDs de puntos
        
        Returns:
            self para encadenamiento
        """
        if not puntos:
            return self
        
        xs = [p.x for p in puntos]
        ys = [p.y for p in puntos]
        zs = [p.z for p in puntos]
        
        # Determinar colores individuales si hay puntos obligatorios/libres
        colores = []
        for p in puntos:
            if p.es_obligatorio:
                colores.append(self.COLORES['punto_obligatorio'])
            else:
                colores.append(color or self.COLORES['punto_libre'])
        
        # Si todos son del mismo color, simplificar
        if len(set(colores)) == 1:
            colores = colores[0]
        
        # Textos para hover
        textos = []
        for i, p in enumerate(puntos):
            texto = f"ID: {p.id or i}<br>X: {p.x:.1f}<br>Y: {p.y:.1f}<br>Z: {p.z:.1f}"
            if p.orden is not None:
                texto += f"<br>Orden: {p.orden}"
            textos.append(texto)
        
        self.figura.add_trace(go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode='markers',
            marker=dict(
                size=tamano,
                color=colores,
                symbol=simbolo,
                line=dict(color='white', width=1)
            ),
            name=nombre,
            text=textos,
            hoverinfo='text'
        ))
        
        # Etiquetas de puntos
        if mostrar_etiquetas:
            for p in puntos:
                if p.id:
                    self.figura.add_trace(go.Scatter3d(
                        x=[p.x],
                        y=[p.y],
                        z=[p.z + 30],
                        mode='text',
                        text=[p.id],
                        textposition='top center',
                        textfont=dict(size=10),
                        showlegend=False
                    ))
        
        return self
    
    def agregar_tuberia(
        self,
        tuberia: Tuberia,
        nombre: Optional[str] = None,
        color: Optional[str] = None,
        ancho_linea: int = 4,
        mostrar_cilindros: bool = False
    ) -> 'Visualizador3D':
        """
        Agrega una tuberia a la visualizacion.
        
        Args:
            tuberia: Tuberia a visualizar
            nombre: Nombre para la leyenda
            color: Color de la tuberia
            ancho_linea: Ancho de la linea
            mostrar_cilindros: Si mostrar representacion cilindrica (mas lento)
        
        Returns:
            self para encadenamiento
        """
        if not tuberia.segmentos:
            return self
        
        # Determinar color segun subtipo
        if color is None:
            clave = tuberia.subtipo.clave
            if 'extraccion' in clave:
                color = self.COLORES['tuberia_extraccion']
            elif 'aislado' in clave:
                color = self.COLORES['tuberia_aislado']
            elif 'recuperador' in clave:
                color = self.COLORES['tuberia_recuperador']
            else:
                color = 'rgb(100, 100, 100)'
        
        nombre = nombre or f"Tuberia ({tuberia.subtipo.nombre})"
        
        # Obtener todos los puntos
        puntos = tuberia.puntos
        xs = [p.x for p in puntos]
        ys = [p.y for p in puntos]
        zs = [p.z for p in puntos]
        
        # Linea de la tuberia
        self.figura.add_trace(go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode='lines+markers',
            line=dict(color=color, width=ancho_linea),
            marker=dict(size=4, color=color),
            name=nombre,
            hoverinfo='text',
            text=[f"Segmento {i}" for i in range(len(puntos))]
        ))
        
        # Si se solicitan cilindros (representacion mas realista)
        if mostrar_cilindros:
            self._agregar_cilindros_tuberia(tuberia, color)
        
        return self
    
    def _agregar_cilindros_tuberia(
        self, 
        tuberia: Tuberia, 
        color: str
    ) -> None:
        """Agrega representacion cilindrica de la tuberia."""
        radio = tuberia.subtipo.dimensiones.radio_mm
        
        for seg in tuberia.segmentos:
            # Generar puntos del cilindro
            self._agregar_cilindro(
                seg.inicio, seg.fin, radio, color
            )
    
    def _agregar_cilindro(
        self,
        p1: Punto3D,
        p2: Punto3D,
        radio: float,
        color: str,
        n_puntos: int = 16
    ) -> None:
        """Agrega un cilindro entre dos puntos."""
        # Direccion del cilindro
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dz = p2.z - p1.z
        longitud = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        if longitud < 0.001:
            return
        
        # Crear puntos del cilindro usando parametrizacion
        theta = np.linspace(0, 2*np.pi, n_puntos)
        
        # Vector direccion normalizado
        d = np.array([dx, dy, dz]) / longitud
        
        # Vectores perpendiculares
        if abs(d[2]) < 0.9:
            perp1 = np.cross(d, [0, 0, 1])
        else:
            perp1 = np.cross(d, [1, 0, 0])
        perp1 = perp1 / np.linalg.norm(perp1)
        perp2 = np.cross(d, perp1)
        
        # Generar superficie del cilindro
        xs, ys, zs = [], [], []
        for t in [0, 1]:
            centro = np.array([p1.x, p1.y, p1.z]) + t * np.array([dx, dy, dz])
            for angle in theta:
                punto = centro + radio * (np.cos(angle) * perp1 + np.sin(angle) * perp2)
                xs.append(punto[0])
                ys.append(punto[1])
                zs.append(punto[2])
        
        # Agregar como superficie
        self.figura.add_trace(go.Surface(
            x=np.array(xs).reshape(2, n_puntos),
            y=np.array(ys).reshape(2, n_puntos),
            z=np.array(zs).reshape(2, n_puntos),
            colorscale=[[0, color], [1, color]],
            showscale=False,
            opacity=0.7,
            showlegend=False
        ))
    
    def agregar_obstaculo(
        self,
        obstaculo: Obstaculo,
        nombre: Optional[str] = None,
        color: Optional[str] = None,
        opacidad: float = 0.5
    ) -> 'Visualizador3D':
        """
        Agrega un obstaculo a la visualizacion.
        
        Args:
            obstaculo: Obstaculo a visualizar
            nombre: Nombre para la leyenda
            color: Color del obstaculo
            opacidad: Opacidad (0-1)
        
        Returns:
            self para encadenamiento
        """
        color = color or self.COLORES['obstaculo']
        nombre = nombre or f"Obstaculo {obstaculo.id or ''}"
        
        vertices = obstaculo.vertices
        
        # Vertices del prisma: 0-3 base inferior, 4-7 base superior
        xs = [v.x for v in vertices]
        ys = [v.y for v in vertices]
        zs = [v.z for v in vertices]
        
        # Definir caras del prisma (triangulos)
        # Base inferior: 0,1,2 y 0,2,3
        # Base superior: 4,5,6 y 4,6,7
        # Caras laterales
        i = [0, 0, 4, 4, 0, 1, 1, 2, 2, 3, 3, 0]
        j = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 0, 4]
        k = [2, 3, 6, 7, 5, 4, 6, 5, 7, 6, 4, 7]
        
        self.figura.add_trace(go.Mesh3d(
            x=xs,
            y=ys,
            z=zs,
            i=i,
            j=j,
            k=k,
            color=color,
            opacity=opacidad,
            name=nombre,
            showlegend=True,
            flatshading=True
        ))
        
        # Agregar bordes
        bordes = [
            # Base inferior
            [0, 1], [1, 2], [2, 3], [3, 0],
            # Base superior
            [4, 5], [5, 6], [6, 7], [7, 4],
            # Verticales
            [0, 4], [1, 5], [2, 6], [3, 7]
        ]
        
        for b in bordes:
            self.figura.add_trace(go.Scatter3d(
                x=[vertices[b[0]].x, vertices[b[1]].x],
                y=[vertices[b[0]].y, vertices[b[1]].y],
                z=[vertices[b[0]].z, vertices[b[1]].z],
                mode='lines',
                line=dict(color=self.COLORES['obstaculo_borde'], width=2),
                showlegend=False
            ))
        
        return self
    
    def agregar_linea(
        self,
        puntos: List[Punto3D],
        nombre: str = "Linea",
        color: str = 'blue',
        ancho: int = 2,
        estilo: str = 'solid'
    ) -> 'Visualizador3D':
        """
        Agrega una linea conectando puntos.
        
        Args:
            puntos: Lista de puntos a conectar
            nombre: Nombre para la leyenda
            color: Color de la linea
            ancho: Ancho de la linea
            estilo: 'solid', 'dash', 'dot'
        
        Returns:
            self para encadenamiento
        """
        if len(puntos) < 2:
            return self
        
        xs = [p.x for p in puntos]
        ys = [p.y for p in puntos]
        zs = [p.z for p in puntos]
        
        self.figura.add_trace(go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode='lines',
            line=dict(color=color, width=ancho, dash=estilo),
            name=nombre
        ))
        
        return self
    
    def agregar_texto(
        self,
        punto: Punto3D,
        texto: str,
        color: str = 'black',
        tamano: int = 12
    ) -> 'Visualizador3D':
        """
        Agrega un texto en una posicion 3D.
        
        Args:
            punto: Posicion del texto
            texto: Texto a mostrar
            color: Color del texto
            tamano: Tamano de fuente
        
        Returns:
            self para encadenamiento
        """
        self.figura.add_trace(go.Scatter3d(
            x=[punto.x],
            y=[punto.y],
            z=[punto.z],
            mode='text',
            text=[texto],
            textposition='top center',
            textfont=dict(size=tamano, color=color),
            showlegend=False
        ))
        
        return self
    
    def agregar_tubos_is(self, tubos_is) -> 'Visualizador3D':
        """Agrega tubos de IS como líneas naranja gruesas.
        
        Args:
            tubos_is: Lista de TuboIS (de src.modelos.soporte)
        """
        color = self.COLORES['tubo_is']
        
        for i, tubo in enumerate(tubos_is):
            p1 = tubo.punto_inicio
            p2 = tubo.punto_fin
            
            self.figura.add_trace(go.Scatter3d(
                x=[p1.x, p2.x],
                y=[p1.y, p2.y],
                z=[p1.z, p2.z],
                mode='lines',
                line=dict(color=color, width=6),
                name='Tubos IS' if i == 0 else None,
                showlegend=(i == 0),
                legendgroup='tubos_is',
                hovertext=f'{tubo.id} ({tubo.is_id})',
                hoverinfo='text',
            ))
        
        return self
    
    def agregar_soportes(self, soportes) -> 'Visualizador3D':
        """Agrega soportes de ventilación a la visualización 3D.
        
        Cada soporte se dibuja como un bracket:
        - Línea base entre posicion1 y posicion2 (sobre IS)
        - Dos líneas verticales de altura cota_a (110 mm)
        - Línea superior conectando las patas
        
        Color por subtipo:
            Ventilación (estándar, 2 tubos) → Verde
            VARIFIX     (especial, 1 tubo)  → Rojo
        
        Args:
            soportes: Lista de Soporte (de src.modelos.soporte)
        """
        first_shown = {}
        
        for sp in soportes:
            es_estandar = sp.subtipo == 'Ventilación'
            color = self.COLORES['soporte_estandar'] if es_estandar else self.COLORES['soporte_varifix']
            grupo = f'Soporte {sp.orientacion}'
            show = grupo not in first_shown
            if show:
                first_shown[grupo] = True
            
            p1 = sp.posicion1
            p2 = sp.posicion2
            z_base1 = p1.z
            z_base2 = p2.z
            z_top1 = z_base1 + sp.cota_a
            z_top2 = z_base2 + sp.cota_a
            
            hover = (f'{sp.id}: {sp.orientacion} ({sp.tipo}/{sp.subtipo})<br>'
                     f'B={sp.cota_b:.0f}mm  A={sp.cota_a:.0f}mm')
            
            self.figura.add_trace(go.Scatter3d(
                x=[p1.x, p2.x], y=[p1.y, p2.y], z=[z_base1, z_base2],
                mode='lines', line=dict(color=color, width=3),
                name=grupo if show else None, showlegend=show,
                legendgroup=grupo, hovertext=hover, hoverinfo='text',
            ))
            self.figura.add_trace(go.Scatter3d(
                x=[p1.x, p1.x], y=[p1.y, p1.y], z=[z_base1, z_top1],
                mode='lines', line=dict(color=color, width=2),
                showlegend=False, legendgroup=grupo, hoverinfo='skip',
            ))
            self.figura.add_trace(go.Scatter3d(
                x=[p2.x, p2.x], y=[p2.y, p2.y], z=[z_base2, z_top2],
                mode='lines', line=dict(color=color, width=2),
                showlegend=False, legendgroup=grupo, hoverinfo='skip',
            ))
            self.figura.add_trace(go.Scatter3d(
                x=[p1.x, p2.x], y=[p1.y, p2.y], z=[z_top1, z_top2],
                mode='lines', line=dict(color=color, width=3),
                showlegend=False, legendgroup=grupo, hoverinfo='skip',
            ))
        
        return self
    
    def mostrar(self) -> None:
        """Muestra la visualizacion en el navegador."""
        self.figura.show()
    
    def guardar_html(self, ruta: str) -> None:
        """
        Guarda la visualizacion como archivo HTML.
        
        Args:
            ruta: Ruta del archivo de salida
        """
        html_content = self.figura.to_html(full_html=True, include_plotlyjs='cdn')
        # Inyectar CSS oscuro en el <head> para eliminar borde blanco del body
        dark_style = '<style>html,body{background-color:rgb(20,20,20);margin:0;padding:0;overflow:hidden;}</style>'
        html_content = html_content.replace('</head>', dark_style + '</head>', 1)
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def guardar_imagen(
        self, 
        ruta: str, 
        ancho: int = 1200, 
        alto: int = 800
    ) -> None:
        """
        Guarda la visualizacion como imagen.
        
        Args:
            ruta: Ruta del archivo de salida
            ancho: Ancho en pixeles
            alto: Alto en pixeles
        """
        self.figura.write_image(ruta, width=ancho, height=alto)
    
    def limpiar(self) -> 'Visualizador3D':
        """Limpia todos los trazos de la figura."""
        self.figura.data = []
        return self
    
    def obtener_figura(self) -> go.Figure:
        """Retorna la figura de plotly para personalizacion avanzada."""
        return self.figura


def crear_visualizacion_ejemplo() -> Visualizador3D:
    """
    Crea una visualizacion de ejemplo con datos de prueba.
    
    Returns:
        Visualizador3D con elementos de ejemplo
    """
    vis = Visualizador3D("Ejemplo de Visualizacion")
    
    # Crear techo de ejemplo (inclinado)
    techo = Techo.desde_vertices([
        [0, 0, 0],
        [3000, 0, 200],
        [3000, 2000, 200],
        [0, 2000, 0]
    ], id="Techo1")
    
    vis.agregar_techo(techo)
    
    # Agregar algunos puntos
    puntos = [
        Punto3D(x=500, y=500, z=techo.calcular_z_en_plano(500, 500), 
                id="P1", es_obligatorio=True, orden=1),
        Punto3D(x=1500, y=1000, z=techo.calcular_z_en_plano(1500, 1000), 
                id="P2", es_obligatorio=False),
        Punto3D(x=2500, y=1500, z=techo.calcular_z_en_plano(2500, 1500), 
                id="P3", es_obligatorio=True, orden=2)
    ]
    
    vis.agregar_puntos(puntos, "Puntos de Conexion")
    
    # Agregar un obstaculo
    obstaculo = Obstaculo(
        centro=Punto3D(x=1500, y=500, z=100),
        ancho_mm=400,
        largo_mm=400,
        alto_mm=200,
        id="Viga1"
    )
    
    vis.agregar_obstaculo(obstaculo)
    
    return vis

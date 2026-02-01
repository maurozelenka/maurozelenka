import os
import numpy as np
import matplotlib.pyplot as plt
from github import Github
from collections import defaultdict
import google.generativeai as genai
import json
import random

# --- CONFIGURACIÓN ---
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    user = g.get_user() # Para leer eventos globales
except Exception as e:
    print(f"Error config: {e}")
    exit(1)

# --- 1. OBTENER ACTIVIDAD (CON MODO DEMO) ---
def get_activity():
    try:
        events = user.get_events()
        materials = defaultdict(int)
        commits_text = []
        total_commits = 0
        
        print("Buscando actividad real...")
        for e in events:
            if e.type == "PushEvent":
                repo_lang = e.repo.language
                if repo_lang: 
                    materials[repo_lang] += len(e.payload.commits)
                for c in e.payload.commits:
                    commits_text.append(c.message)
                total_commits += len(e.payload.commits)
            if total_commits > 50: break
        
        # --- AQUÍ ESTÁ EL TRUCO (MODO DEMO) ---
        # Si no hay materiales reales, INVENTAMOS UNA METRÓPOLIS
        if not materials:
            print("⚠️ No hay actividad real. ACTIVANDO MODO DEMO (Simulación de Ciudad).")
            # Simulamos que has programado como una bestia
            materials = {
                'Python': 25,
                'JavaScript': 18,
                'TypeScript': 15,
                'Rust': 10,
                'Go': 8,
                'CSS': 12,
                'HTML': 5
            }
            # Simulamos mensajes para que la IA elija un tema guapo
            fake_msgs = [
                "refactor critical backend microservices",
                "optimize neural network layers",
                "fix memory leak in production",
                "deploy kubernetes cluster",
                "implement ray tracing engine",
                "redesign ui components with glassmorphism"
            ]
            return materials, " | ".join(fake_msgs)
            
        return materials, " | ".join(commits_text)
    except Exception as e:
        print(f"Error leyendo actividad: {e}")
        return None, ""

# --- 2. EL CEREBRO DE DISEÑO (GEMINI 2.0) ---
def get_ai_theme(text):
    print("Gemini está decidiendo el estilo de la ciudad...")
    prompt = f"""
    Actúa como un Arquitecto de Arte Generativo. Analiza el "vibe" de estos commits: "{text}".
    
    Elige un TEMA VISUAL IMPRESIONANTE para una ciudad 3D.
    
    Devuelve un JSON estricto con esta estructura (usa colores HEX vibrantes):
    {{
      "theme_name": "Nombre (ej: Neon Cyberpunk, Volcanic, Deep Ocean, Matrix)",
      "ground_color": "#HEX (color oscuro para fondo, ej: #0d1117, #000000)",
      "building_colors": ["#HEX1", "#HEX2", "#HEX3", "#HEX4", "#HEX5"],
      "edge_color": "#HEX (color borde bloques, suele quedar bien negro o blanco)"
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except:
            return {
                "theme_name": "Emergency Backup",
                "ground_color": "#0d1117",
                "building_colors": ['#FF00FF', '#00FFFF', '#FFFF00', '#FF0000'],
                "edge_color": "#FFFFFF"
            }

# --- 3. CONSTRUCTOR 3D ---
def build_city(materials, theme):
    print(f"Construyendo ciudad estilo: {theme.get('theme_name', 'Default')}")
    
    map_size = 12 # Hacemos el mapa un poco más grande
    voxels = np.zeros((map_size, map_size, map_size), dtype=bool)
    colors = np.empty(voxels.shape, dtype=object)
    
    palette = theme.get('building_colors', ['#333'])
    
    # Función hash pseudo-aleatoria pero determinista para colocar edificios
    def get_coords(name):
        h = sum(ord(c) for c in name) * 7
        return h % map_size, (h // map_size) % map_size

    if materials:
        for i, (lang, count) in enumerate(materials.items()):
            # Altura exagerada para que impresione (máximo 10 bloques)
            h_val = min(int(np.ceil(count / 1.5)), map_size - 2)
            if h_val < 2: h_val = 2 # Mínimo 2 pisos para que se vea
            
            x, y = get_coords(lang)
            
            # Aseguramos que no se salga del mapa
            if x >= map_size: x = map_size - 1
            if y >= map_size: y = map_size - 1
            
            color = palette[i % len(palette)]
            
            # Construimos la torre
            for z in range(h_val):
                voxels[x, y, z] = True
                colors[x, y, z] = color
                
            # A veces añadimos un "edificio satélite" al lado si la torre es muy alta
            if h_val > 5:
                if x+1 < map_size: 
                    voxels[x+1, y, 0] = True
                    colors[x+1, y, 0] = color
                    voxels[x+1, y, 1] = True
                    colors[x+1, y, 1] = color

    # Render
    fig = plt.figure(figsize=(10, 10)) # Imagen más grande
    ax = fig.add_subplot(projection='3d')
    
    bg_color = theme.get('ground_color', '#0d1117')
    ax.set_facecolor(bg_color) 
    fig.patch.set_facecolor(bg_color)

    edge = theme.get('edge_color', 'k')
    
    # Dibujamos con sombra
    ax.voxels(voxels, facecolors=colors, edgecolor=edge, linewidth=0.5, shade=True)
    
    # Ángulo perfecto para ver la ciudad
    ax.view_init(elev=35, azim=-45)
    ax.set_box_aspect(None, zoom=1.2)
    ax.axis('off')

    if not os.path.exists('assets'): os.makedirs('assets')
    plt.savefig('assets/city_view.png', facecolor=bg_color, bbox_inches='tight', pad_inches=0)
    print("¡Ciudad Generada con éxito!")

# EJECUCIÓN
mats, text = get_activity()
estilo = get_ai_theme(text)
build_city(mats, estilo)

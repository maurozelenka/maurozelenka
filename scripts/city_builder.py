import os
import numpy as np
import matplotlib.pyplot as plt
from github import Github
from collections import defaultdict
import google.generativeai as genai
import json

# --- CONFIGURACIÓN ---
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
except Exception as e:
    print(f"Error config: {e}")
    exit(1)

# --- 1. OBTENER ACTIVIDAD ---
def get_activity():
    try:
        events = repo.get_events()
        materials = defaultdict(int)
        commits_text = []
        total_commits = 0
        
        for e in events:
            if e.type == "PushEvent":
                repo_lang = e.repo.language
                # Guardamos info para construir
                if repo_lang: materials[repo_lang] += len(e.payload.commits)
                # Guardamos texto para la IA
                for c in e.payload.commits:
                    commits_text.append(c.message)
                total_commits += len(e.payload.commits)
            if total_commits > 50: break
            
        return materials, " | ".join(commits_text)
    except: return None, ""

# --- 2. EL CEREBRO DE DISEÑO (GEMINI 2.0) ---
def get_ai_theme(text):
    print("Gemini está decidiendo el estilo de la ciudad...")
    prompt = f"""
    Actúa como un Arquitecto de Arte Generativo. Analiza el "sentimiento" de estos commits: "{text}".
    
    Elige un TEMA VISUAL para una ciudad voxel basado en si los mensajes denotan estrés, calma, velocidad o bugs.
    
    Devuelve un JSON estricto con esta estructura (usa colores HEX):
    {{
      "theme_name": "Nombre (ej: Magma, Zen, Cyberpunk, Ice)",
      "ground_color": "#HEX (color de fondo/suelo)",
      "building_colors": ["#HEX1", "#HEX2", "#HEX3", "#HEX4"],
      "edge_color": "#HEX (color borde bloques)"
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except:
        # Fallback a 1.5 si falla la 2.0
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except:
            # Fallback manual por si todo falla
            return {
                "theme_name": "Default Blue",
                "ground_color": "#0d1117",
                "building_colors": ['#3572A5', '#2b7489', '#4F5D95'],
                "edge_color": "#000000"
            }

# --- 3. CONSTRUCTOR 3D ---
def build_city(materials, theme):
    print(f"Construyendo ciudad estilo: {theme.get('theme_name', 'Default')}")
    
    map_size = 10
    voxels = np.zeros((map_size, map_size, map_size), dtype=bool)
    colors = np.empty(voxels.shape, dtype=object)
    
    palette = theme.get('building_colors', ['#333'])
    
    def get_coords(name):
        h = sum(ord(c) for c in name)
        return h % map_size, (h // map_size) % map_size

    if materials:
        for i, (lang, count) in enumerate(materials.items()):
            # Altura (máximo 8 bloques)
            h_val = min(int(np.ceil(count / 1.5)), map_size - 2)
            if h_val < 1: h_val = 1
            x, y = get_coords(lang)
            
            color = palette[i % len(palette)]
            
            for z in range(h_val):
                voxels[x, y, z] = True
                colors[x, y, z] = color
    else:
        # Base pequeña si no hay commits
        voxels[4:6, 4:6, 0] = True
        colors[4:6, 4:6, 0] = palette[0]

    # Render
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(projection='3d')
    
    bg_color = theme.get('ground_color', '#0d1117')
    ax.set_facecolor(bg_color) 
    fig.patch.set_facecolor(bg_color)

    edge = theme.get('edge_color', 'k')
    ax.voxels(voxels, facecolors=colors, edgecolor=edge, linewidth=0.5, shade=True)
    
    ax.view_init(elev=40, azim=-45)
    ax.set_box_aspect(None, zoom=1.1)
    ax.axis('off')

    if not os.path.exists('assets'): os.makedirs('assets')
    plt.savefig('assets/city_view.png', facecolor=bg_color, bbox_inches='tight', pad_inches=0)
    print("¡Ciudad Generada!")

# EJECUCIÓN
mats, text = get_activity()
estilo = get_ai_theme(text)
build_city(mats, estilo)

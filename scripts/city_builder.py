import os
import numpy as np
import matplotlib.pyplot as plt
from github import Github
import google.generativeai as genai
import json
import random

# --- CONFIGURACIÓN ---
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except:
    print("Error config Gemini")

# --- 1. DATOS FALSOS MASIVOS (PARA QUE SALGA SI O SI) ---
def get_activity():
    # Nos inventamos los datos directamente. No leemos GitHub.
    print("⚡ FORZANDO MODO DEMO MASIVO ⚡")
    materials = {
        'Python': 45,      # Rascacielos
        'JavaScript': 30,  # Edificios medios
        'TypeScript': 25,
        'Rust': 15,
        'Go': 20,
        'CSS': 10,
        'HTML': 5,
        'C++': 12,
        'Java': 8
    }
    # Texto falso para que la IA se inspire
    fake_msgs = "build cyberpunk neural network AI matrix system override protocol high tech neon lights glow dark mode production deploy"
    return materials, fake_msgs

# --- 2. GEMINI ELIGE EL TEMA ---
def get_ai_theme(text):
    print("Gemini eligiendo tema...")
    prompt = f"""
    Eres un diseñador experto en Voxel Art.
    Crea un esquema de colores para una ciudad futurista basado en estas palabras: "{text}".
    
    Dame un JSON estricto:
    {{
      "ground_color": "#HEX (fondo oscuro, ej #050505)",
      "building_colors": ["#HEX1", "#HEX2", "#HEX3", "#HEX4", "#HEX5"],
      "edge_color": "#HEX (borde, ej #FFFFFF o #000000)"
    }}
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except:
        # Si falla la IA, usamos este tema CYBERPUNK fijo
        return {
            "ground_color": "#050510",
            "building_colors": ['#FF00FF', '#00FFFF', '#7F00FF', '#0000FF', '#FFFFFF'],
            "edge_color": "#000000"
        }

# --- 3. CONSTRUCTOR 3D ---
def build_city(materials, theme):
    print("Levantando la ciudad...")
    map_size = 14 # Mapa grande
    voxels = np.zeros((map_size, map_size, map_size), dtype=bool)
    colors = np.empty(voxels.shape, dtype=object)
    
    palette = theme.get('building_colors', ['#FFF'])
    
    # Algoritmo de dispersión
    def get_coords(name, offset):
        h = sum(ord(c) for c in name) * (offset + 1)
        return h % map_size, (h // map_size) % map_size

    # Construimos MUCHOS edificios
    index = 0
    for lang, count in materials.items():
        # Repetimos el edificio varias veces para llenar el mapa
        for i in range(2): 
            h_val = min(int(count / 3), map_size - 1)
            if h_val < 3: h_val = 3 # Mínimo 3 pisos
            
            x, y = get_coords(lang, i + index)
            
            # Limites
            x = x % map_size
            y = y % map_size
            
            color = palette[index % len(palette)]
            
            # Torre principal
            for z in range(h_val):
                voxels[x, y, z] = True
                colors[x, y, z] = color
            
            index += 1

    # RENDERIZADO
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(projection='3d')
    
    bg = theme.get('ground_color', '#000')
    ax.set_facecolor(bg) 
    fig.patch.set_facecolor(bg)

    edge = theme.get('edge_color', 'k')
    
    ax.voxels(voxels, facecolors=colors, edgecolor=edge, linewidth=0.5, shade=True)
    
    ax.view_init(elev=45, azim=-45)
    ax.set_box_aspect(None, zoom=1.3)
    ax.axis('off')

    if not os.path.exists('assets'): os.makedirs('assets')
    plt.savefig('assets/city_view.png', facecolor=bg, bbox_inches='tight', pad_inches=0)
    print("¡CIUDAD GENERADA!")

# EJECUCIÓN
mats, text = get_activity()
estilo = get_ai_theme(text)
build_city(mats, estilo)

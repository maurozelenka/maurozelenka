import os
import random
from github import Github, Auth

# --- CONFIGURACIÓN ---
username = "ANONYMOUS"
events = []

try:
    repo_full_name = os.getenv("GITHUB_REPOSITORY", "usuario/repo")
    username = repo_full_name.split("/")[0]

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        auth = Auth.Token(token)
        g = Github(auth=auth)
        user_obj = g.get_user(username)
        events = user_obj.get_public_events()
except Exception as e:
    print(f"Modo offline: {e}")

# --- 1. OBTENER DATOS CRUDOS ---
def get_raw_data():
    data_lines = []
    try:
        for e in events:
            if e.type == "PushEvent":
                for c in e.payload.commits:
                    data_lines.append(c.sha)
            if len(data_lines) >= 14: break
    except:
        pass
    
    while len(data_lines) < 16: # Necesitamos unas 16 líneas
        fake_hash = ''.join(random.choices('0123456789abcdef', k=40))
        data_lines.append(fake_hash)
        
    return data_lines[:16]

# --- 2. FORMATEAR A BINARIO PURO (0s y 1s) ---
def format_as_binary(raw_lines):
    binary_lines = []
    for line in raw_lines:
        # Convertimos el hash hex a un número gigante
        hex_int = int(line, 16)
        # Lo convertimos a string binario (quitando el '0b' inicial)
        bin_str = bin(hex_int)[2:]
        # Rellenamos con ceros a la izquierda si hace falta
        bin_str = bin_str.zfill(160)
        
        # Cogemos los primeros 64 bits para que quepa en pantalla
        chunk = bin_str[:64]
        # Añadimos un espacio cada 8 bits para que sea legible
        formatted_chunk = " ".join(chunk[i:i+8] for i in range(0, len(chunk), 8))
        binary_lines.append(formatted_chunk)
        
    return binary_lines

# --- 3. GENERAR TERMINAL SVG (BUCLE INFINITO) ---
def create_svg_terminal(lines, user_display):
    height = 60 + (len(lines) * 20)
    
    # CSS PARA BUCLE INFINITO TIPO "ESCRITURA"
    css = """
    <style>
        .term-text { 
            font-family: 'Courier New', Courier, monospace; 
            font-size: 13px; 
            fill: #33ff00; 
            text-shadow: 0 0 4px #33ff00;
            font-weight: bold;
            opacity: 0; /* Empiezan invisibles */
        }
        .cursor { 
            fill: #33ff00; 
            text-shadow: 0 0 4px #33ff00;
            animation: blink 0.8s infinite; 
        }
        
        /* La animación: Aparece de golpe, espera, desaparece */
        @keyframes typeLoop { 
            0% { opacity: 0; }
            1% { opacity: 1; }   /* Aparece */
            95% { opacity: 1; }  /* Se mantiene */
            100% { opacity: 0; } /* Se borra para reiniciar */
        }
        
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    """
    
    # Duración total del ciclo antes de reiniciarse (12 segundos)
    cycle_duration = 12
    
    for i in range(len(lines) + 1):
        # Cada línea aparece 0.3s después de la anterior
        delay = i * 0.3
        css += f"#L{i} {{ animation: typeLoop {cycle_duration}s infinite steps(1) {delay}s; }}\n"
    
    css += "</style>"
    
    svg_content = ""
    # Cabecera
    svg_content += f'<text id="L0" x="15" y="55" class="term-text">INITIATING BINARY STREAM FOR: [{user_display.upper()}]</text>\n'
    
    # Líneas de ceros y unos
    for i, line in enumerate(lines):
        svg_content += f'<text id="L{i+1}" x="15" y="{80 + (i * 20)}" class="term-text">{line}</text>\n'

    full_svg = f"""
    <svg width="650" height="{height}" viewBox="0 0 650 {height}" xmlns="http://www.w3.org/2000/svg">
        {css}
        <rect x="0" y="0" width="650" height="{height}" rx="6" fill="#050505" stroke="#333"/>
        <rect x="0" y="0" width="650" height="25" rx="6" fill="#1a1a1a"/>
        <rect x="0" y="15" width="650" height="10" fill="#1a1a1a"/>
        <text x="325" y="17" text-anchor="middle" fill="#888" font-family="Arial, sans-serif" font-size="10">/dev/urandom - binary mode</text>
        <circle cx="20" cy="12" r="5" fill="#ff5f56"/>
        <circle cx="40" cy="12" r="5" fill="#ffbd2e"/>
        <circle cx="60" cy="12" r="5" fill="#27c93f"/>
        {svg_content}
        <rect x="15" y="{80 + (len(lines) * 20)}" width="8" height="15" class="cursor" id="L{len(lines)+1}"/>
    </svg>
    """
    
    if not os.path.exists('assets'): os.makedirs('assets')
    with open('assets/binary_dump.svg', 'w', encoding='utf-8') as f:
        f.write(full_svg)
    print("¡Stream binario infinito generado!")

# EJECUCIÓN
raw = get_raw_data()
binary_data = format_as_binary(raw)
create_svg_terminal(binary_data, username)

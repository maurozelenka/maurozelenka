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

# --- 1. OBTENER DATOS ---
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
    
    while len(data_lines) < 14: # Usaremos 14 líneas
        fake_hash = ''.join(random.choices('0123456789abcdef', k=40))
        data_lines.append(fake_hash)
        
    return data_lines[:14]

# --- 2. FORMATEAR A BINARIO ---
def format_as_binary(raw_lines):
    binary_lines = []
    for line in raw_lines:
        hex_int = int(line, 16)
        bin_str = bin(hex_int)[2:].zfill(160)
        # 64 caracteres de ancho y grupos de 8
        chunk = bin_str[:64]
        formatted_chunk = " ".join(chunk[i:i+8] for i in range(0, len(chunk), 8))
        binary_lines.append(formatted_chunk)
    return binary_lines

# --- 3. GENERAR SVG CON EFECTO "MÁQUINA DE ESCRIBIR" ---
def create_svg_terminal(lines, user_display):
    line_height = 20
    start_y = 80
    height = start_y + (len(lines) * line_height) + 20
    
    # Configuración de la animación
    time_per_line = 2.5 # Segundos que tarda en escribirse una línea (LENTO)
    total_lines = len(lines)
    typing_duration = total_lines * time_per_line
    pause_duration = 5 # Segundos de pausa al final antes de reiniciar
    total_cycle_time = typing_duration + pause_duration

    # Calculamos porcentajes para los keyframes de CSS
    # El momento en que termina de escribir todo y empieza la pausa
    finish_typing_pct = (typing_duration / total_cycle_time) * 100
    # El momento justo antes de reiniciar (para borrar la pantalla)
    reset_pct = 99.5 

    css = f"""
    <style>
        .term-text {{ 
            font-family: 'Courier New', Courier, monospace; 
            font-size: 13px; 
            fill: #33ff00; /* Verde Hacker */
            text-shadow: 0 0 4px #33ff00; /* Brillo Neón */
            font-weight: bold;
        }}
        .cursor {{ 
            fill: #33ff00; 
            text-shadow: 0 0 4px #33ff00;
            animation: blink 0.8s infinite; 
        }}
        
        /* Animación de la máscara reveladora */
        @keyframes reveal {{ 
            0% {{ width: 0; }}
            {finish_typing_pct}% {{ width: 630px; }} /* Ancho total alcanzado */
            {reset_pct}% {{ width: 630px; }} /* Se mantiene visible durante la pausa */
            100% {{ width: 0; }} /* Se reinicia de golpe */
        }}
        
        @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    """
    
    # Generamos los delays para cada línea
    for i in range(total_lines):
        # Cada línea empieza exactamente cuando termina la anterior
        delay = i * time_per_line
        # Usamos 'steps(60)' para que el movimiento sea a trompicones, como escribiendo
        css += f"#maskRect{i} {{ animation: reveal {total_cycle_time}s linear infinite steps(60) {delay}s; }}\n"
    
    css += "</style>"
    
    # Definiciones de las máscaras (clip-paths)
    defs_content = "<defs>\n"
    for i in range(total_lines):
        y_pos = start_y + (i * line_height) - 15 # Ajuste fino para cubrir el texto
        # El rectángulo que crecerá
        defs_content += f'<clipPath id="cp{i}"><rect id="maskRect{i}" x="15" y="{y_pos}" height="20" width="0" /></clipPath>\n'
    defs_content += "</defs>\n"
    
    # Contenido de texto (aplicando las máscaras)
    svg_text_content = ""
    # Cabecera fija
    svg_text_content += f'<text x="15" y="55" class="term-text">INITIATING SLOW-TYPE BINARY STREAM FOR: [{user_display.upper()}]</text>\n'
    
    for i, line in enumerate(lines):
        y_pos = start_y + (i * line_height)
        # Aplicamos el clip-path correspondiente a cada línea de texto
        svg_text_content += f'<text clip-path="url(#cp{i})" x="15" y="{y_pos}" class="term-text">{line}</text>\n'

    full_svg = f"""
    <svg width="650" height="{height}" viewBox="0 0 650 {height}" xmlns="http://www.w3.org/2000/svg">
        {css}
        {defs_content}
        <rect x="0" y="0" width="650" height="{height}" rx="6" fill="#050505" stroke="#333"/>
        <rect x="0" y="0" width="650" height="25" rx="6" fill="#1a1a1a"/>
        <rect x="0" y="15" width="650" height="10" fill="#1a1a1a"/>
        <text x="325" y="17" text-anchor="middle" fill="#888" font-family="Arial, sans-serif" font-size="10">/dev/urandom - slow type mode</text>
        <circle cx="20" cy="12" r="5" fill="#ff5f56"/>
        <circle cx="40" cy="12" r="5" fill="#ffbd2e"/>
        <circle cx="60" cy="12" r="5" fill="#27c93f"/>
        
        {svg_text_content}
        
        <rect x="15" y="{height - 25}" width="8" height="15" class="cursor"/>
    </svg>
    """
    
    if not os.path.exists('assets'): os.makedirs('assets')
    with open('assets/binary_dump.svg', 'w', encoding='utf-8') as f:
        f.write(full_svg)
    print("¡Stream binario de escritura lenta generado!")

# EJECUCIÓN
raw = get_raw_data()
binary_data = format_as_binary(raw)
create_svg_terminal(binary_data, username)

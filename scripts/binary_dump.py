import os
from github import Github

# --- CONFIGURACIÓN ---
try:
    # Usamos el token para leer datos reales
    g = Github(os.environ["GITHUB_TOKEN"])
    user = g.get_user()
    # Obtenemos eventos recientes para sacar datos "frescos"
    events = user.get_public_events()
except:
    print("Error de conexión. Usando datos offline.")
    events = []

# --- 1. OBTENER DATOS CRUDOS (TUS COMMITS REALES) ---
def get_raw_data():
    data_lines = []
    commits_found = 0
    
    # Buscamos los hashes de los commits recientes
    for e in events:
        if e.type == "PushEvent":
            for c in e.payload.commits:
                # El hash (sha) es perfecto para esto (ej: 6dcb09b5b57875f334f61aebed695e2e4193db5e)
                data_lines.append(c.sha)
                commits_found += 1
        if commits_found >= 14: break # Necesitamos unas 14 líneas para llenar la pantalla
    
    # Si no hay suficientes datos recientes, rellenamos con "ruido" estético
    while len(data_lines) < 14:
        import random
        fake_hash = ''.join(random.choices('0123456789abcdef', k=40))
        data_lines.append(fake_hash)
        
    return data_lines[:14]

# --- 2. FORMATEAR COMO "VOLCADO HEXADECIMAL" ---
def format_as_hexdump(raw_lines):
    formatted_lines = []
    address = 0x08048000 # Una dirección de memoria inicial típica de Linux

    for line in raw_lines:
        # Cogemos los primeros 32 caracteres del hash
        hex_data = line[:32]
        # Los agrupamos de 2 en 2 para que parezcan bytes (AA BB CC...)
        hex_pairs = " ".join(hex_data[i:i+2] for i in range(0, len(hex_data), 2)).upper()
        
        # Formato: DIRECCIÓN: DATOS
        formatted_line = f"0x{address:08X}:  {hex_pairs}"
        formatted_lines.append(formatted_line)
        address += 16 # Incrementamos dirección
        
    return formatted_lines

# --- 3. GENERAR LA TERMINAL SVG ANIMADA ---
def create_svg_terminal(lines):
    height = 50 + (len(lines) * 20) # Altura dinámica
    
    # CSS para la animación de "escritura" rápida
    css = """
    <style>
        @font-face {
            font-family: 'HackFont';
            src: url('https://cdnjs.cloudflare.com/ajax/libs/hack-font/3.3.0/webfonts/hack-regular.woff2') format('woff2');
        }
        .term-text { 
            font-family: 'HackFont', 'Courier New', monospace; 
            font-size: 13px; 
            fill: #33ff00; /* Verde hacker */
            opacity: 0; 
        }
        .cursor { 
            fill: #33ff00; 
            animation: blink 0.8s infinite; 
        }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        @keyframes appear { to { opacity: 1; } }
    """
    
    # Generar delays para que aparezcan línea a línea muy rápido
    for i in range(len(lines) + 1):
        # Aparece una línea cada 0.1 segundos
        css += f"#L{i} {{ animation: appear 0.1s steps(1) forwards {i * 0.1}s; }}\n"
    css += "</style>"
    
    # Crear los elementos de texto SVG
    svg_content = ""
    # Línea 0: cabecera del sistema
    svg_content += f'<text id="L0" x="15" y="50" class="term-text">CORE DUMP INITIATED FOR USER: [{user.login.upper()}]</text>\n'
    
    for i, line in enumerate(lines):
        # i+1 porque la L0 ya la usamos
        svg_content += f'<text id="L{i+1}" x="15" y="{75 + (i * 20)}" class="term-text">{line}</text>\n'

    # Plantilla SVG final
    full_svg = f"""
    <svg width="650" height="{height}" viewBox="0 0 650 {height}" xmlns="http://www.w3.org/2000/svg">
        {css}
        <rect x="0" y="0" width="650" height="{height}" rx="6" fill="#0c0c0c" stroke="#333"/>
        <rect x="0" y="0" width="650" height="25" rx="6" fill="#1f1f1f"/>
        <rect x="0" y="15" width="650" height="10" fill="#1f1f1f"/> <text x="325" y="17" text-anchor="middle" fill="#666" font-family="Arial" font-size="11">/dev/mem - raw dump</text>
        {svg_content}
        <rect x="15" y="{75 + (len(lines) * 20)}" width="8" height="15" class="cursor" id="L{len(lines)+1}"/>
    </svg>
    """
    
    if not os.path.exists('assets'): os.makedirs('assets')
    with open('assets/binary_dump.svg', 'w', encoding='utf-8') as f:
        f.write(full_svg)
    print("¡Volcado binario generado!")

# EJECUCIÓN
raw = get_raw_data()
formatted = format_as_hexdump(raw)
create_svg_terminal(formatted)

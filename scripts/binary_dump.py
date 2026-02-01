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
    
    while len(data_lines) < 14:
        fake_hash = ''.join(random.choices('0123456789abcdef', k=40))
        data_lines.append(fake_hash)
        
    return data_lines[:14]

# --- 2. FORMATEAR ---
def format_as_hexdump(raw_lines):
    formatted_lines = []
    address = 0x08048000 

    for line in raw_lines:
        hex_data = line[:32]
        hex_pairs = " ".join(hex_data[i:i+2] for i in range(0, len(hex_data), 2)).upper()
        formatted_line = f"0x{address:08X}:  {hex_pairs}"
        formatted_lines.append(formatted_line)
        address += 16
        
    return formatted_lines

# --- 3. GENERAR TERMINAL SVG (SIN FUENTES EXTERNAS) ---
def create_svg_terminal(lines, user_display):
    height = 60 + (len(lines) * 20)
    
    # CAMBIO IMPORTANTE: Usamos 'Courier New' y quitamos @font-face
    css = """
    <style>
        .term-text { 
            font-family: 'Courier New', Courier, monospace; 
            font-size: 13px; 
            fill: #33ff00; 
            text-shadow: 0 0 4px #33ff00;
            font-weight: bold;
            opacity: 0; 
        }
        .cursor { 
            fill: #33ff00; 
            text-shadow: 0 0 4px #33ff00;
            animation: blink 0.8s infinite; 
        }
        .header { fill: #888; font-family: Arial, sans-serif; font-size: 10px; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        @keyframes appear { to { opacity: 1; } }
    """
    
    for i in range(len(lines) + 1):
        css += f"#L{i} {{ animation: appear 0.05s steps(1) forwards {i * 0.05}s; }}\n"
    css += "</style>"
    
    svg_content = ""
    svg_content += f'<text id="L0" x="15" y="55" class="term-text">CORE DUMP INITIATED FOR TARGET: [{user_display.upper()}]</text>\n'
    
    for i, line in enumerate(lines):
        svg_content += f'<text id="L{i+1}" x="15" y="{80 + (i * 20)}" class="term-text">{line}</text>\n'

    full_svg = f"""
    <svg width="650" height="{height}" viewBox="0 0 650 {height}" xmlns="http://www.w3.org/2000/svg">
        {css}
        <rect x="0" y="0" width="650" height="{height}" rx="6" fill="#050505" stroke="#333"/>
        <rect x="0" y="0" width="650" height="25" rx="6" fill="#1a1a1a"/>
        <rect x="0" y="15" width="650" height="10" fill="#1a1a1a"/>
        <text x="325" y="17" text-anchor="middle" class="header">/bin/xxd -r /dev/mem</text>
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
    print("¡Volcado binario generado (Compatible con GitHub)!")

# EJECUCIÓN
raw = get_raw_data()
formatted = format_as_hexdump(raw)
create_svg_terminal(formatted, username)

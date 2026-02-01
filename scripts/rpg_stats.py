import os
import matplotlib.pyplot as plt
import numpy as np
from github import Github
import google.generativeai as genai

try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
except Exception as e:
    print(f"Error: {e}")
    exit(1)

def get_daily_activity():
    try:
        events = repo.get_events()
        commits = []
        for e in events:
            if e.type == "PushEvent":
                for c in e.payload.commits:
                    commits.append(c.message)
            if len(commits) > 15: break
        
        if not commits:
            return "Hoy no hubo actividad. Día de descanso."
        return " ".join(commits)
    except:
        return "Actividad desconocida."

def get_ai_score(text):
    prompt = f"""
    Actúa como un sistema de estadísticas RPG. Analiza estos commits de programación: "{text}".
    
    Asigna una puntuación del 1 al 10 para estos 5 atributos:
    1. LÓGICA (Backend, Algoritmos, Matemáticas, Bases de datos)
    2. ARTE (Frontend, CSS, Diseño, Animaciones, UI/UX)
    3. ESTABILIDAD (Tests, Bugfixes, Refactor, Seguridad, Types)
    4. VELOCIDAD (Productividad, Commits frecuentes, Features rápidas)
    5. SABIDURÍA (Documentación, Readme, Configuración, CI/CD, Arquitectura)
    
    IMPORTANTE: 
    - Si el texto dice "descanso", devuelve 1,1,1,1,1.
    - Responde ÚNICAMENTE con los 5 números separados por comas.
    - Ejemplo: 8,2,5,9,1
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        clean_text = response.text.strip().replace('\n', '').replace('`', '').replace('json', '')
        return list(map(int, clean_text.split(',')))
    except Exception:
        try:
             model_old = genai.GenerativeModel('gemini-1.5-flash')
             response = model_old.generate_content(prompt)
             clean_text = response.text.strip().replace('\n', '').replace('`', '')
             return list(map(int, clean_text.split(',')))
        except:
             return [5, 5, 5, 5, 5]

def draw_chart(stats):
    labels = ['LÓGICA', 'ARTE', 'ESTABILIDAD', 'VELOCIDAD', 'SABIDURÍA']
    
    stats_c = stats + [stats[0]]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += [angles[0]]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#0d1117') 
    ax.set_facecolor('#0d1117')
    
    ax.plot(angles, stats_c, color='#39ff14', linewidth=2)
    ax.fill(angles, stats_c, color='#39ff14', alpha=0.25)
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='white', size=10, weight='bold')
    
    ax.grid(color='#30363d', linestyle='--')
    ax.spines['polar'].set_visible(False)

    if not os.path.exists('assets'):
        os.makedirs('assets')
        
    plt.savefig('assets/rpg_stats.png', facecolor='#0d1117', edgecolor='none')

actividad = get_daily_activity()
print(actividad)
puntos = get_ai_score(actividad)
print(puntos)
draw_chart(puntos)

"""CopySpell AI - Launcher pentru executabil"""
import os
import sys
import webbrowser
import threading
import time

# Adauga directorul curent in path
if getattr(sys, 'frozen', False):
    # Rulam ca executabil
    base_path = sys._MEIPASS
else:
    # Rulam ca script
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)

# Verifica update-uri la pornire
try:
    from updater import check_and_update
    check_and_update()
except Exception as e:
    print(f"Nu s-a putut verifica update-ul: {e}")

# Nu setăm API keys în launcher pentru a evita blocarea de către GitHub
# API keys sunt gestionate separat în fișiere de configurare

from web_app import app

def open_browser():
    """Deschide browserul automat dupa 2 secunde"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

def main():
    """Functia principala"""
    print("=" * 60)
    print("  CopySpell AI - Smart Copywriting Generator")
    print("=" * 60)
    print()
    print("Pornesc serverul...")
    print("API-uri configurate: DeepSeek, Groq, OpenRouter")
    print()
    print("Aplicatia se va deschide automat in browser")
    print("Sau acceseaza manual: http://127.0.0.1:5000")
    print()
    print("Apasa CTRL+C pentru a opri")
    print("=" * 60)
    print()
    
    # Porneste browserul in thread separat
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Porneste Flask
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    main()
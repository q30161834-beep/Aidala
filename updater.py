"""Auto-updater pentru CopySpell AI"""
import os
import sys
import json
import urllib.request
import urllib.error
import hashlib
import shutil
from pathlib import Path

# Configuratie GitHub
GITHUB_REPO = "q30161834-beep/Aidala"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"

# Fisierele care trebuie actualizate - se citesc din manifest.json de pe GitHub
# Daca manifest.json nu exista, se foloseste lista default
DEFAULT_UPDATE_FILES = [
    "web_app.py",
    "launcher.py",
    "updater.py",
    "config/settings.py",
    "config/prompts.py",
    "core/content_generator.py",
    "core/ai_router.py",
    "providers/base.py",
    "providers/deepseek.py",
    "providers/groq.py",
    "providers/openrouter.py",
    "templates/index.html"
]

class Updater:
    def __init__(self):
        self.base_path = self._get_base_path()
        self.version_file = Path(self.base_path) / "version.json"
        self.current_version = self._get_current_version()
        
    def _get_base_path(self):
        """Obtine calea de baza"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    
    def _get_current_version(self):
        """Obtine versiunea curenta"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('version', '1.0.0')
            except:
                pass
        return '1.0.0'
    
    def _save_version(self, version):
        """Salveaza versiunea"""
        with open(self.version_file, 'w') as f:
            json.dump({'version': version}, f)
    
    def check_for_update(self):
        """Verifica daca exista update disponibil"""
        try:
            # Obtine ultima versiune de pe GitHub
            req = urllib.request.Request(
                GITHUB_API_URL,
                headers={'User-Agent': 'CopySpell-AI-Updater'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get('tag_name', 'v1.0.0').lstrip('v')
                
                # Compara versiunile
                if self._version_compare(latest_version, self.current_version) > 0:
                    return {
                        'available': True,
                        'version': latest_version,
                        'url': data.get('html_url', ''),
                        'notes': data.get('body', 'No release notes')
                    }
        except Exception as e:
            print(f"Eroare la verificarea update-ului: {e}")
        
        return {'available': False}
    
    def _version_compare(self, v1, v2):
        """Compara doua versiuni"""
        def normalize(v):
            return [int(x) for x in v.split('.')]
        
        n1 = normalize(v1)
        n2 = normalize(v2)
        
        for i in range(max(len(n1), len(n2))):
            x1 = n1[i] if i < len(n1) else 0
            x2 = n2[i] if i < len(n2) else 0
            if x1 > x2:
                return 1
            elif x1 < x2:
                return -1
        return 0
    
    def download_file(self, file_path, target_path):
        """Descarca un fisier de pe GitHub"""
        url = f"{GITHUB_RAW_URL}/{file_path}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'CopySpell-AI-Updater'})
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                
            # Creeaza directorul daca nu exista
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Salveaza fisierul
            with open(target_path, 'wb') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Eroare la descarcarea {file_path}: {e}")
            return False
    
    def get_update_files(self):
        """Obtine lista de fisiere de actualizat din manifest sau default"""
        try:
            url = f"{GITHUB_RAW_URL}/manifest.json"
            req = urllib.request.Request(url, headers={'User-Agent': 'CopySpell-AI-Updater'})
            with urllib.request.urlopen(req, timeout=10) as response:
                manifest = json.loads(response.read().decode())
                files = manifest.get('files', DEFAULT_UPDATE_FILES)
                print(f"Manifest gasit: {len(files)} fisiere de actualizat")
                return files
        except:
            print(f"Folosim lista default: {len(DEFAULT_UPDATE_FILES)} fisiere")
            return DEFAULT_UPDATE_FILES
    
    def update(self, new_version):
        """Actualizeaza aplicatia"""
        print(f"Actualizare de la {self.current_version} la {new_version}...")
        
        # Obtine lista de fisiere
        update_files = self.get_update_files()
        
        print("Se descarca fisierele...")
        success = True
        updated_files = []
        
        for file_path in update_files:
            target_path = os.path.join(self.base_path, file_path)
            print(f"  Descarc {file_path}...", end=' ')
            
            if self.download_file(file_path, target_path):
                print("OK")
                updated_files.append(file_path)
            else:
                print("ESUAT")
                success = False
        
        if success:
            self._save_version(new_version)
            print(f"\nActualizare completa! Versiunea curenta: {new_version}")
            return True
        else:
            print("\nActualizare partiala. Unele fisiere nu au putut fi actualizate.")
            return False
    
    def force_update(self):
        """Force update - descarca toate fisierele indiferent de versiune"""
        print("Force update - se descarca toate fisierele de pe GitHub...")
        return self.update("latest")

def check_and_update():
    """Verifica si aplica update-uri la pornire"""
    updater = Updater()
    
    print(f"Versiune curenta: {updater.current_version}")
    print("Se verifica actualizari...")
    
    update_info = updater.check_for_update()
    
    if update_info['available']:
        print(f"\nUpdate disponibil: {update_info['version']}")
        print(f"Release notes: {update_info['notes'][:200]}...")
        
        response = input("\nDoresti sa actualizezi acum? (y/n): ").lower()
        if response in ['y', 'yes', 'da']:
            if updater.update(update_info['version']):
                print("\nReporneste aplicatia pentru a folosi noua versiune.")
                input("Apasa Enter pentru a iesi...")
                sys.exit(0)
            else:
                input("Apasa Enter pentru a continua cu versiunea curenta...")
        else:
            print("Actualizare amanata.")
    else:
        print("Aplicatia este la zi.")

if __name__ == '__main__':
    check_and_update()
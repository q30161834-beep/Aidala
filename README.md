# CopySpell AI

Generator de copywriting persuasiv cu AI.

## Configurare Auto-Update

### 1. Obtine GitHub Token
1. Mergi la: https://github.com/settings/tokens
2. Click: "Generate new token (classic)"
3. Selecteaza scope: **repo**
4. Copiaza tokenul

### 2. Configureaza Upload Script
Editeaza `upload_to_github.py` si lipeste tokenul:
```python
GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"  # TOKENUL TAU AICI
```

### 3. Creaza Repository pe GitHub
- Nume: `Aidala`
- Owner: `q30161834-beep`
- Public sau Private

### 4. Upload Fisiere
```bash
python upload_to_github.py
```

### 5. Update Versiune
Cand faci modificari:
1. Editeaza `version.json` - incrementeaza versiunea
2. Ruleaza `python upload_to_github.py`
3. Scriptul creeaza automat release nou

## Structura Repository

```
Aidala/
├── web_app.py              # Flask app
├── launcher.py             # Entry point cu auto-update
├── updater.py              # Logica update
├── version.json            # Versiune curenta
├── config/                 # Configurari
├── core/                   # Logica business
├── providers/              # Provideri AI
├── models/                 # Modele date
└── templates/              # HTML templates
```

## API Keys (deja configurate)
- DeepSeek
- Groq
- OpenRouter

## Cum functioneaza Auto-Update
1. La pornire, aplicatia verifica `version.json` de pe GitHub
2. Daca versiunea e mai noua, descarca fisierele actualizate
3. Utilizatorul e intrebat daca vrea sa actualizeze
4. Daca accepta, fisierele se inlocuiesc automat
"""CopySpell AI - Web Version (Flask)"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from config.settings import settings
from core.content_generator import ContentGenerator
from models import AUDIENCES, TONES, CONTENT_TYPES, FRAMEWORKS

app = Flask(__name__)
generator = ContentGenerator()


def get_options():
    """Get all options for the form."""
    return {
        "audiences": [{"id": a.id, "name": a.name} for a in AUDIENCES],
        "tones": [{"id": t.id, "name": t.name} for t in TONES],
        "content_types": [{"id": ct.id, "name": ct.name} for ct in CONTENT_TYPES],
        "frameworks": list(FRAMEWORKS.keys()),
        "providers": ["deepseek", "groq", "openrouter"]
    }


@app.route("/")
def index():
    """Main page."""
    options = get_options()
    has_keys = settings.has_any_api_key()
    return render_template("index.html", options=options, has_keys=has_keys)


@app.route("/api/generate", methods=["POST"])
def generate():
    """Generate content endpoint."""
    if not settings.has_any_api_key():
        return jsonify({"error": "No API keys configured"}), 400
    
    data = request.json
    
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generator.generate(
            keywords=data.get("keywords", ""),
            content_type_id=data.get("content_type", "facebook_post"),
            framework=data.get("framework", "AIDA"),
            audience_id=data.get("audience", "weight_loss_seeker"),
            tone_id=data.get("tone", "empathetic"),
            additional_context=data.get("additional_context", ""),
            preferred_provider=data.get("provider") or None
        ))
        loop.close()
        
        if result.success:
            return jsonify({
                "success": True,
                "content": result.content,
                "provider": result.provider_used,
                "model": result.model_used,
                "tokens": result.tokens_used
            })
        else:
            return jsonify({
                "success": False,
                "error": "\n".join(result.errors) if result.errors else "Unknown error"
            }), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/history")
def get_history():
    """Get generation history."""
    return jsonify(generator.get_history())


@app.route("/api/config", methods=["GET", "POST"])
def config():
    """Get or save API configuration."""
    if request.method == "GET":
        return jsonify({
            "deepseek": bool(settings.deepseek_api_key),
            "groq": bool(settings.groq_api_key),
            "openrouter": bool(settings.openrouter_api_key)
        })
    
    elif request.method == "POST":
        data = request.json
        settings.deepseek_api_key = data.get("deepseek", "").strip() or None
        settings.groq_api_key = data.get("groq", "").strip() or None
        settings.openrouter_api_key = data.get("openrouter", "").strip() or None
        settings.save_api_keys()
        
        # Reinitialize generator
        global generator
        generator = ContentGenerator()
        
        return jsonify({"success": True})


if __name__ == "__main__":
    print(f"Starting {settings.app_name}...")
    print(f"Open browser at: http://localhost:5000")
    app.run(debug=True, port=5000)
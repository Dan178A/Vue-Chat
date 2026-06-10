"""
Vue-Chat Backend - Servidor seguro con soporte para ChatGPT y Ollama
====================================================================
Características:
- Autenticación JWT
- Rate limiting
- CORS restrictivo
- Validación de entrada
- Soporte dual: OpenAI y Ollama
- Logging seguro
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from loguru import logger
import os
import secrets
import time
from functools import wraps
from typing import Dict, List, Optional
import json

# ================================================
# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
# ================================================

def load_env():
    """Carga configuración desde variables de entorno"""
    from dotenv import load_dotenv
    load_dotenv()

load_env()

# Configuración del servidor
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
HOST = os.getenv("SERVER_HOST", "127.0.0.1")
PORT = int(os.getenv("SERVER_PORT", "5000"))

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", lambda: secrets.token_hex(32))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "200"))

# Seguridad
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))


# ================================================
# INICIALIZACIÓN DE FLASK
# ================================================

app = Flask(__name__)
app.config.from_object(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# CORS restrictivo - solo orígenes permitidos
CORS(app,
     resources={r"/api/*": {"origins": CORS_ORIGINS}},
     supports_credentials=True,
     methods=["GET", "POST"],
     allow_headers=["Content-Type", "Authorization"])


# ================================================
# CONFIGURACIÓN DE LOGGING SEGURO
# ================================================

logger.add(
    "./log/run.log",
    encoding="utf-8",
    format="{level} | {time:YYYY-MM-DD HH:mm:ss} | {file} | {line} | {message}",
    retention="30 days",
    rotation="500 MB"
)

# Filtrar información sensible de logs
class SensitiveFilter:
    def __init__(self):
        self.sensitive_keys = ['api_key', 'token', 'password', 'secret', 'authorization']

    def filter(self, record):
        message = str(record["message"])
        for key in self.sensitive_keys:
            if key.lower() in message.lower():
                record["message"] = message.replace(key.upper(), "***REDACTED***")
        return record

logger.add(SensitiveFilter(), format="{level} | {time} | {message}")


# ================================================
# UTILIDADES DE SEGURIDAD
# ================================================

class RateLimiter:
    """Rate limiting en memoria"""

    def __init__(self):
        self.requests_per_minute: Dict[str, List[float]] = {}
        self.requests_per_hour: Dict[str, List[float]] = {}

    def is_allowed(self, identifier: str) -> bool:
        """Verifica si el request está dentro del límite"""
        now = time.time()

        # Limpiar requests antiguos (más de 1 minuto)
        self.requests_per_minute[identifier] = [
            t for t in self.requests_per_minute.get(identifier, [])
            if now - t < 60
        ]

        # Limpiar requests antiguos (más de 1 hora)
        self.requests_per_hour[identifier] = [
            t for t in self.requests_per_hour.get(identifier, [])
            if now - t < 3600
        ]

        # Verificar límites
        if len(self.requests_per_minute.get(identifier, [])) >= RATE_LIMIT_PER_MINUTE:
            return False
        if len(self.requests_per_hour.get(identifier, [])) >= RATE_LIMIT_PER_HOUR:
            return False

        # Registrar request
        self.requests_per_minute.setdefault(identifier, []).append(now)
        self.requests_per_hour.setdefault(identifier, []).append(now)

        return True

rate_limiter = RateLimiter()


def rate_limit_decorator(f):
    """Decorador para aplicar rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Usar IP del cliente como identificador
        identifier = request.remote_addr

        if not rate_limiter.is_allowed(identifier):
            logger.warning(f"Rate limit exceeded for IP: {identifier}")
            return jsonify({
                "status": "error",
                "message": "Too many requests. Please try again later."
            }), 429

        return f(*args, **kwargs)
    return decorated_function


def validate_input(data: dict, required_fields: List[str]) -> Optional[str]:
    """Valida que los campos requeridos existan y no estén vacíos"""
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
        if not data[field] or not str(data[field]).strip():
            return f"Invalid value for field: {field}"
    return None


def sanitize_input(text: str) -> str:
    """Sanitiza entrada del usuario"""
    if not text:
        return ""
    # Limitar longitud
    text = text[:MAX_CONTENT_LENGTH]
    # Remover caracteres potencialmente problemáticos
    text = text.replace("\x00", "")
    return text.strip()


# ================================================
# AUTENTICACIÓN JWT
# ================================================

import jwt
from datetime import datetime, timedelta

def generate_token(user_id: str) -> str:
    """Genera un token JWT"""
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None

def jwt_required(f):
    """Decorador para requerir autenticación JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "status": "error",
                "message": "Authorization header missing"
            }), 401

        try:
            # Formato: "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({
                    "status": "error",
                    "message": "Invalid authorization header format"
                }), 401

            token = parts[1]
            payload = verify_token(token)

            if not payload:
                return jsonify({
                    "status": "error",
                    "message": "Invalid or expired token"
                }), 401

            # Guardar info del usuario en g
            g.user_id = payload.get("user_id")

        except Exception as e:
            logger.error(f"Auth error: {e}")
            return jsonify({
                "status": "error",
                "message": "Authentication failed"
            }), 401

        return f(*args, **kwargs)
    return decorated


# ================================================
# GESTIÓN DE CONVERSACIONES
# ================================================

class ConversationManager:
    """Gestiona el historial de mensajes por bot y sesión"""

    def __init__(self):
        self.conversations: Dict[str, Dict[str, List[dict]]] = {}

    def get_messages(self, session_id: str, bot_name: str) -> List[dict]:
        """Obtiene mensajes para una sesión y bot específicos"""
        key = f"{session_id}:{bot_name}"
        return self.conversations.get(key, []).copy()

    def add_message(self, session_id: str, bot_name: str, message: dict):
        """Añade un mensaje al historial"""
        key = f"{session_id}:{bot_name}"
        if key not in self.conversations:
            self.conversations[key] = []
        self.conversations[key].append(message)

    def clear_conversation(self, session_id: str, bot_name: str):
        """Limpia el historial de una conversación"""
        key = f"{session_id}:{bot_name}"
        if key in self.conversations:
            del self.conversations[key]

    def set_system_prompt(self, session_id: str, bot_name: str, system_prompt: str):
        """Establece el prompt del sistema inicial"""
        key = f"{session_id}:{bot_name}"
        self.conversations[key] = [{
            "role": "system",
            "content": system_prompt
        }]

conv_manager = ConversationManager()


# ================================================
# INTEGRACIONES CON LLM
# ================================================

class LLMProvider:
    """Proveedor base para modelos de lenguaje"""

    def __init__(self, provider_type: str, config: dict):
        self.provider_type = provider_type
        self.config = config

    def chat(self, messages: List[dict]) -> dict:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """Proveedor para OpenAI (ChatGPT)"""

    def __init__(self, api_key: str):
        super().__init__("openai", {"api_key": api_key})
        self.api_key = api_key

    def chat(self, messages: List[dict]) -> dict:
        try:
            import openai
            openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "provider": "openai"
            }
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "openai"
            }


class OllamaProvider(LLMProvider):
    """Proveedor para Ollama (modelos locales)"""

    def __init__(self, base_url: str, default_model: str):
        super().__init__("ollama", {"base_url": base_url, "default_model": default_model})
        self.base_url = base_url
        self.default_model = default_model

    def chat(self, messages: List[dict], model: str = None) -> dict:
        try:
            import requests

            model = model or self.default_model

            # Convertir mensajes al formato de Ollama
            ollama_messages = []
            for msg in messages:
                if msg.get("role") == "system":
                    ollama_messages.append({
                        "role": "system",
                        "content": msg.get("content", "")
                    })
                else:
                    ollama_messages.append(msg)

            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": ollama_messages,
                    "stream": False
                },
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data.get("message", {}).get("content", ""),
                    "provider": "ollama",
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama error: {response.status_code}",
                    "provider": "ollama"
                }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to Ollama. Is it running?",
                "provider": "ollama"
            }
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "ollama"
            }


# Inicializar proveedores
def get_llm_provider(provider: str):
    """Factory para obtener el proveedor de LLM"""
    if provider == "openai":
        return OpenAIProvider(OPENAI_API_KEY)
    elif provider == "ollama":
        return OllamaProvider(OLLAMA_BASE_URL, OLLAMA_DEFAULT_MODEL)
    else:
        # Por defecto usar Ollama
        return OllamaProvider(OLLAMA_BASE_URL, OLLAMA_DEFAULT_MODEL)


# ================================================
# RUTAS DE LA API
# ================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Endpoint de salud del servidor"""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/api/auth/login", methods=["POST"])
@rate_limit_decorator
def login():
    """Endpoint de login - genera token JWT"""
    data = request.get_json()

    # Validar entrada
    error = validate_input(data, ["username"])
    if error:
        return jsonify({"status": "error", "message": error}), 400

    username = sanitize_input(data["username"])

    # En producción, verificar contra base de datos
    # Por ahora, generar token simple
    token = generate_token(username)

    logger.info(f"User logged in: {username}")

    return jsonify({
        "status": "success",
        "token": token,
        "user": username,
        "expires_in": JWT_EXPIRE_MINUTES * 60
    })


@app.route("/api/chat", methods=["POST"])
@jwt_required
@rate_limit_decorator
def chat():
    """Endpoint principal de chat"""
    data = request.get_json()

    # Validar entrada
    error = validate_input(data, ["message", "bot"])
    if error:
        return jsonify({"status": "error", "message": error}), 400

    message = sanitize_input(data["message"])
    bot_name = sanitize_input(data["bot"])
    provider = data.get("provider", "ollama")  # openai, ollama
    model = data.get("model")  # opcional para Ollama
    session_id = data.get("session_id", "default")
    clear_context = data.get("clear_context", False)

    # Obtener init_prompt del bot si es primera vez
    if clear_context or not conv_manager.get_messages(session_id, bot_name):
        init_prompt = data.get("init_prompt", "")
        if init_prompt:
            conv_manager.set_system_prompt(session_id, bot_name, init_prompt)

    # Añadir mensaje del usuario
    conv_manager.add_message(session_id, bot_name, {
        "role": "user",
        "content": message
    })

    # Obtener historial de conversación
    messages = conv_manager.get_messages(session_id, bot_name)

    logger.info(f"Chat request from {g.user_id} to {bot_name} via {provider}")

    # Obtener proveedor y hacer la llamada
    llm_provider = get_llm_provider(provider)

    if provider == "ollama":
        response = llm_provider.chat(messages, model)
    else:
        response = llm_provider.chat(messages)

    if response["success"]:
        # Añadir respuesta al historial
        conv_manager.add_message(session_id, bot_name, {
            "role": "assistant",
            "content": response["content"]
        })

        return jsonify({
            "status": "success",
            "answer": response["content"],
            "provider": response.get("provider"),
            "model": response.get("model")
        })
    else:
        return jsonify({
            "status": "error",
            "message": response.get("error", "Failed to get response")
        }), 500


@app.route("/api/chat/clear", methods=["POST"])
@jwt_required
def clear_chat():
    """Limpia el historial de una conversación"""
    data = request.get_json()

    session_id = data.get("session_id", "default")
    bot_name = data.get("bot")

    if not bot_name:
        return jsonify({"status": "error", "message": "bot parameter required"}), 400

    conv_manager.clear_conversation(session_id, bot_name)

    logger.info(f"Conversation cleared for {g.user_id}, bot: {bot_name}")

    return jsonify({
        "status": "success",
        "message": "Conversation cleared"
    })


@app.route("/api/models", methods=["GET"])
def list_models():
    """Lista los modelos disponibles"""
    models = {
        "openai": ["gpt-3.5-turbo", "gpt-4"],
        "ollama": []
    }

    # Intentar obtener modelos de Ollama
    try:
        import requests
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            ollama_models = response.json().get("models", [])
            models["ollama"] = [m.get("name", "").split(":")[0] for m in ollama_models]
    except:
        pass

    return jsonify({
        "status": "success",
        "models": models
    })


# ================================================
# MANEJO DE ERRORES
# ================================================

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"status": "error", "message": "Bad request"}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"status": "error", "message": "Unauthorized"}), 401

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Not found"}), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({"status": "error", "message": "Too many requests"}), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {e}")
    return jsonify({"status": "error", "message": "Internal server error"}), 500


# ================================================
# INICIO DEL SERVIDOR
# ================================================

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Vue-Chat Server v2.0.0 - Starting...")
    logger.info(f"Host: {HOST}:{PORT}")
    logger.info(f"Debug: {DEBUG}")
    logger.info(f"JWT Expire: {JWT_EXPIRE_MINUTES} minutes")
    logger.info(f"CORS Origins: {CORS_ORIGINS}")
    logger.info("=" * 50)

    app.run(host=HOST, port=PORT, debug=DEBUG)
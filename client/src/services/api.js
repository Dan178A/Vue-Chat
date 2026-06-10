/**
 * API Service - Capa de comunicación con el backend
 * Maneja autenticación, tokens, errores y validación
 */

import axios from 'axios';

// ================================================
// CONFIGURACIÓN BASE
// ================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Crear instancia de axios
const api = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    timeout: 120000, // 2 minutos para respuestas largas
    headers: {
        'Content-Type': 'application/json',
    },
});

// ================================================
// GESTIÓN DE TOKEN
// ================================================

const TokenService = {
    // Clave para localStorage
    TOKEN_KEY: 'vue_chat_token',
    USER_KEY: 'vue_chat_user',

    // Obtener token
    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    },

    // Guardar token
    setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    },

    // Eliminar token
    removeToken() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
    },

    // Obtener usuario
    getUser() {
        return localStorage.getItem(this.USER_KEY);
    },

    // Guardar usuario
    setUser(user) {
        localStorage.setItem(this.USER_KEY, user);
    },

    // Verificar si hay sesión activa
    isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;

        // Verificar expiración del token (opcional - el backend valida)
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 > Date.now();
        } catch {
            return false;
        }
    },
};

// ================================================
// INTERCEPTORS DE AXIOS
// ================================================

// Request interceptor - agregar token
api.interceptors.request.use(
    (config) => {
        const token = TokenService.getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor - manejar errores globales
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const { response } = error;

        if (response) {
            switch (response.status) {
                case 401:
                    // Token expirado o inválido
                    TokenService.removeToken();
                    window.location.href = '/login';
                    break;
                case 429:
                    console.error('Rate limit exceeded. Please wait.');
                    break;
                case 500:
                    console.error('Server error. Please try again later.');
                    break;
            }
        } else {
            console.error('Network error. Please check your connection.');
        }

        return Promise.reject(error);
    }
);

// ================================================
// SERVICIOS DE API
// ================================================

export const AuthService = {
    /**
     * Iniciar sesión
     * @param {string} username - Nombre de usuario
     * @returns {Promise} - Token y datos del usuario
     */
    async login(username) {
        const response = await api.post('/auth/login', { username });
        const { token, user } = response.data;

        TokenService.setToken(token);
        TokenService.setUser(user);

        return response.data;
    },

    /**
     * Cerrar sesión
     */
    logout() {
        TokenService.removeToken();
    },

    /**
     * Verificar si está autenticado
     */
    isAuthenticated() {
        return TokenService.isAuthenticated();
    },

    /**
     * Obtener usuario actual
     */
    getCurrentUser() {
        return TokenService.getUser();
    },
};

export const ChatService = {
    /**
     * Enviar mensaje al chat
     * @param {object} params - Parámetros del mensaje
     * @param {string} params.message - Mensaje del usuario
     * @param {string} params.bot - Nombre del bot
     * @param {string} params.provider - Proveedor (openai/ollama)
     * @param {string} params.model - Modelo específico (opcional)
     * @param {string} params.session_id - ID de sesión
     * @param {string} params.init_prompt - Prompt inicial
     * @param {boolean} params.clear_context - Limpiar contexto
     * @returns {Promise} - Respuesta del asistente
     */
    async sendMessage({
        message,
        bot,
        provider = 'ollama',
        model = null,
        session_id = 'default',
        init_prompt = '',
        clear_context = false,
    }) {
        const response = await api.post('/chat', {
            message,
            bot,
            provider,
            model,
            session_id,
            init_prompt,
            clear_context,
        });
        return response.data;
    },

    /**
     * Limpiar conversación
     * @param {string} bot - Nombre del bot
     * @param {string} session_id - ID de sesión
     */
    async clearChat(bot, session_id = 'default') {
        const response = await api.post('/chat/clear', {
            bot,
            session_id,
        });
        return response.data;
    },
};

export const ModelService = {
    /**
     * Obtener lista de modelos disponibles
     */
    async listModels() {
        const response = await api.get('/models');
        return response.data;
    },
};

export const HealthService = {
    /**
     * Verificar estado del servidor
     */
    async checkHealth() {
        const response = await api.get('/health');
        return response.data;
    },
};

// ================================================
// EXPORTAR INSTANCIA API Y SERVICIOS
// ================================================

export { api, TokenService };
export default api;
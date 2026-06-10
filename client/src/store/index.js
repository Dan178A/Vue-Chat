// ================================================
// Vue-Chat Store - Gestión de estado global
// ================================================

import Vue from 'vue';
import Vuex from 'vuex';
import util from '@/common/util';
import { AuthService, ChatService, ModelService, TokenService } from '@/services/api';

Vue.use(Vuex);

// ================================================
// STATE
// ================================================

const state = {
    // Autenticación
    isAuthenticated: TokenService.isAuthenticated(),
    currentUser: TokenService.getUser(),
    token: TokenService.getToken(),

    // Chat
    currentBotIndex: 0,
    bots: [],
    isLoading: false,
    error: null,

    // Modelos
    availableModels: {
        openai: [],
        ollama: [],
    },
    currentProvider: 'ollama', // openai | ollama

    // UI
    theme: 'dark', // dark | light
    streaming: false,
};

// ================================================
// MUTATIONS
// ================================================

const mutations = {
    // Autenticación
    SET_AUTH(state, { token, user }) {
        state.isAuthenticated = true;
        state.currentUser = user;
        state.token = token;
    },

    CLEAR_AUTH(state) {
        state.isAuthenticated = false;
        state.currentUser = null;
        state.token = null;
    },

    // Bots
    SET_BOTS(state, bots) {
        state.bots = bots;
    },

    SET_CURRENT_BOT(state, index) {
        state.currentBotIndex = index;
    },

    // Mensajes
    ADD_MESSAGE(state, payload) {
        const { botName, message } = payload;
        const bot = state.bots.find(b => b.name === botName);
        if (bot) {
            bot.messages.push(message);
        }
    },

    CLEAR_BOT_MESSAGES(state, botName) {
        const bot = state.bots.find(b => b.name === botName);
        if (bot) {
            bot.messages = [];
        }
    },

    // Estado de carga
    SET_LOADING(state, loading) {
        state.isLoading = loading;
    },

    // Error
    SET_ERROR(state, error) {
        state.error = error;
    },

    CLEAR_ERROR(state) {
        state.error = null;
    },

    // Provider
    SET_PROVIDER(state, provider) {
        state.currentProvider = provider;
    },

    // Modelos
    SET_MODELS(state, models) {
        state.availableModels = models;
    },

    // Streaming
    SET_STREAMING(state, streaming) {
        state.streaming = streaming;
    },

    // Tema
    SET_THEME(state, theme) {
        state.theme = theme;
    },
};

// ================================================
// ACTIONS
// ================================================

const actions = {
    // Cargar bots desde JSON
    async fetchBots({ commit }) {
        try {
            const response = await fetch('bots.json');
            const data = await response.json();
            const botsArray = [];

            for (const [botName, initPrompt] of Object.entries(data)) {
                botsArray.push({
                    name: botName,
                    avatar: `assets/${Math.floor(Math.random() * 10)}.png`,
                    initPrompt: initPrompt,
                    messages: [],
                    provider: 'ollama', // Por defecto
                    model: null,
                });
            }

            commit('SET_BOTS', botsArray);
            return botsArray;
        } catch (error) {
            console.error('Error fetching bots:', error);
            commit('SET_ERROR', 'Failed to load bots');
        }
    },

    // Login
    async login({ commit }, username) {
        commit('SET_LOADING', true);
        commit('CLEAR_ERROR');

        try {
            const result = await AuthService.login(username);
            commit('SET_AUTH', { token: result.token, user: result.user });
            return result;
        } catch (error) {
            const message = error.response?.data?.message || 'Login failed';
            commit('SET_ERROR', message);
            throw error;
        } finally {
            commit('SET_LOADING', false);
        }
    },

    // Logout
    logout({ commit }) {
        AuthService.logout();
        commit('CLEAR_AUTH');
    },

    // Enviar mensaje
    async sendMessage({ commit, state }, { message, botName, provider, model, initPrompt }) {
        const bot = state.bots.find(b => b.name === botName);
        if (!bot) return;

        commit('SET_LOADING', true);
        commit('CLEAR_ERROR');

        // Agregar mensaje del usuario
        const userMessage = {
            content: message,
            sender: 'user',
            receiver: botName,
            time: util.formatDate.format(new Date(), 'yyyy-MM-dd HH:mm:ss'),
        };
        commit('ADD_MESSAGE', { botName, message: userMessage });

        try {
            const response = await ChatService.sendMessage({
                message,
                bot: botName,
                provider: provider || bot.provider || 'ollama',
                model: model || bot.model,
                session_id: 'default',
                init_prompt: initPrompt || bot.initPrompt,
                clear_context: false,
            });

            if (response.status === 'success') {
                const botMessage = {
                    content: response.answer,
                    sender: botName,
                    receiver: 'user',
                    time: util.formatDate.format(new Date(), 'yyyy-MM-dd HH:mm:ss'),
                };
                commit('ADD_MESSAGE', { botName, message: botMessage });
                return response;
            } else {
                throw new Error(response.message || 'Failed to get response');
            }
        } catch (error) {
            const errorMessage = {
                content: `Error: ${error.response?.data?.message || error.message}`,
                sender: botName,
                receiver: 'user',
                time: util.formatDate.format(new Date(), 'yyyy-MM-dd HH:mm:ss'),
            };
            commit('ADD_MESSAGE', { botName, message: errorMessage });
            commit('SET_ERROR', error.message);
            throw error;
        } finally {
            commit('SET_LOADING', false);
        }
    },

    // Limpiar conversación
    async clearConversation({ commit }, botName) {
        try {
            await ChatService.clearChat(botName);
            commit('CLEAR_BOT_MESSAGES', botName);
        } catch (error) {
            console.error('Error clearing conversation:', error);
        }
    },

    // Cargar modelos disponibles
    async loadModels({ commit }) {
        try {
            const response = await ModelService.listModels();
            if (response.status === 'success') {
                commit('SET_MODELS', response.models);
            }
        } catch (error) {
            console.error('Error loading models:', error);
        }
    },

    // Cambiar provider
    setProvider({ commit }, provider) {
        commit('SET_PROVIDER', provider);
    },
};

// ================================================
// GETTERS
// ================================================

const getters = {
    currentBot(state) {
        return state.bots[state.currentBotIndex] || null;
    },

    currentBotMessages(state) {
        const bot = state.bots[state.currentBotIndex];
        return bot ? bot.messages : [];
    },

    isLoggedIn(state) {
        return state.isAuthenticated;
    },

    ollamaModels(state) {
        return state.availableModels.ollama || [];
    },

    openaiModels(state) {
        return state.availableModels.openai || [];
    },
};

// ================================================
// EXPORT STORE
// ================================================

export default new Vuex.Store({
    state,
    mutations,
    actions,
    getters,
});
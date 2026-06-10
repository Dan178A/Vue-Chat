<template>
    <div class="login-container">
        <div class="login-glass">
            <div class="login-header">
                <div class="logo">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h1>Vue-Chat</h1>
                <p class="subtitle">Conecta con IA de forma segura</p>
            </div>

            <form @submit.prevent="handleLogin" class="login-form">
                <div class="input-group">
                    <label for="username">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M8 12C9.10457 12 10 11.1046 10 10C10 8.89543 9.10457 8 8 8C6.89543 8 6 8.89543 6 10C6 11.1046 6.89543 12 8 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M20 8C18.6739 8.47815 17.4021 9.32799 16.2965 10.4929C15.191 11.6578 14.2821 13.1141 13.6265 14.7556C12.9708 16.3971 12.5843 18.1866 12.4966 20.005" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M16 12C17.1046 12 18 11.1046 18 10C18 8.89543 17.1046 8 16 8C14.8954 8 14 8.89543 14 10C14 11.1046 14.8954 12 16 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </label>
                    <input
                        id="username"
                        v-model="username"
                        type="text"
                        placeholder="Ingresa tu nombre de usuario"
                        :disabled="loading"
                        autocomplete="username"
                    />
                </div>

                <div class="provider-select">
                    <label>Selecciona el modelo de IA</label>
                    <div class="provider-buttons">
                        <button
                            type="button"
                            :class="['provider-btn', { active: provider === 'ollama' }]"
                            @click="provider = 'ollama'"
                        >
                            <span class="provider-icon">🦙</span>
                            <span>Ollama</span>
                            <span class="provider-badge">Local</span>
                        </button>
                        <button
                            type="button"
                            :class="['provider-btn', { active: provider === 'openai' }]"
                            @click="provider = 'openai'"
                        >
                            <span class="provider-icon">🤖</span>
                            <span>ChatGPT</span>
                            <span class="provider-badge">Cloud</span>
                        </button>
                    </div>
                </div>

                <button type="submit" class="login-btn" :disabled="loading || !username.trim()">
                    <span v-if="!loading">Iniciar Sesión</span>
                    <span v-else class="loading-spinner"></span>
                </button>

                <p v-if="error" class="error-message">{{ error }}</p>
            </form>

            <div class="login-footer">
                <p>🔒 Autenticación segura con JWT</p>
            </div>
        </div>

        <!-- Background decoration -->
        <div class="bg-shapes">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
        </div>
    </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
    name: 'LoginView',
    data() {
        return {
            username: '',
            provider: 'ollama',
        };
    },
    computed: {
        ...mapState({
            loading: 'isLoading',
            error: 'error',
        }),
    },
    methods: {
        async handleLogin() {
            if (!this.username.trim()) return;

            try {
                await this.$store.dispatch('login', this.username);
                this.$store.dispatch('setProvider', this.provider);
                this.$router.push('/chat');
            } catch (error) {
                console.error('Login failed:', error);
            }
        },
    },
    mounted() {
        // Si ya está autenticado, redirigir al chat
        if (this.$store.getters.isLoggedIn) {
            this.$router.push('/chat');
        }
    },
};
</script>

<style lang="scss" scoped>
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    position: relative;
    overflow: hidden;
}

.login-glass {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 3rem;
    width: 100%;
    max-width: 420px;
    position: relative;
    z-index: 10;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.login-header {
    text-align: center;
    margin-bottom: 2.5rem;

    .logo {
        width: 64px;
        height: 64px;
        margin: 0 auto 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);

        svg {
            width: 36px;
            height: 36px;
            color: white;
        }
    }

    h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: white;
        margin: 0 0 0.5rem;
        background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .subtitle {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.875rem;
        margin: 0;
    }
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.input-group {
    position: relative;

    label {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        color: rgba(255, 255, 255, 0.5);
        pointer-events: none;
        transition: all 0.3s ease;

        svg {
            width: 20px;
            height: 20px;
        }
    }

    input {
        width: 100%;
        padding: 1rem 1rem 1rem 3rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
        font-size: 1rem;
        transition: all 0.3s ease;

        &::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }

        &:focus {
            outline: none;
            border-color: #667eea;
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);

            & + label,
            & ~ label {
                left: 0.75rem;
                top: -0.5rem;
                font-size: 0.75rem;
                color: #667eea;
            }
        }

        &:not(:placeholder-shown) + label,
        &:not(:placeholder-shown) ~ label {
            left: 0.75rem;
            top: -0.5rem;
            font-size: 0.75rem;
            color: #667eea;
        }
    }
}

.provider-select {
    label {
        display: block;
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.875rem;
        margin-bottom: 0.75rem;
    }
}

.provider-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.provider-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    transition: all 0.3s ease;

    .provider-icon {
        font-size: 1.5rem;
    }

    .provider-badge {
        font-size: 0.625rem;
        padding: 0.125rem 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 999px;
    }

    &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
    }

    &.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: transparent;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);

        .provider-badge {
            background: rgba(255, 255, 255, 0.2);
        }
    }
}

.login-btn {
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 12px;
    color: white;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 52px;

    &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }

    &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
}

.loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.error-message {
    color: #f87171;
    font-size: 0.875rem;
    text-align: center;
    margin: 0;
    padding: 0.75rem;
    background: rgba(248, 113, 113, 0.1);
    border-radius: 8px;
    border: 1px solid rgba(248, 113, 113, 0.2);
}

.login-footer {
    margin-top: 2rem;
    text-align: center;

    p {
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.75rem;
        margin: 0;
    }
}

// Background shapes
.bg-shapes {
    position: absolute;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
}

.shape {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.5;
}

.shape-1 {
    width: 400px;
    height: 400px;
    background: #667eea;
    top: -100px;
    right: -100px;
    animation: float 8s ease-in-out infinite;
}

.shape-2 {
    width: 300px;
    height: 300px;
    background: #764ba2;
    bottom: -50px;
    left: -50px;
    animation: float 10s ease-in-out infinite reverse;
}

.shape-3 {
    width: 200px;
    height: 200px;
    background: #f093fb;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation: pulse 6s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(30px, 30px); }
}

@keyframes pulse {
    0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
    50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.5; }
}
</style>
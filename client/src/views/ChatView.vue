<template>
    <div class="chat-view">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="logo-mini">
                    <svg viewBox="0 0 24 24" fill="none">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2"/>
                        <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
                        <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
                    </svg>
                </div>
                <span class="app-name">Vue-Chat</span>
            </div>

            <div class="bots-section">
                <h3>Asistentes</h3>
                <div class="bots-list">
                    <div
                        v-for="(bot, index) in bots"
                        :key="index"
                        :class="['bot-item', { active: currentBotIndex === index }]"
                        @click="selectBot(index)"
                    >
                        <div class="bot-avatar">
                            <img :src="bot.avatar" :alt="bot.name" />
                            <span class="status-dot"></span>
                        </div>
                        <div class="bot-info">
                            <span class="bot-name">{{ bot.name }}</span>
                            <span class="bot-preview">
                                {{ getLastMessage(bot) }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="sidebar-footer">
                <div class="provider-selector">
                    <span class="label">Proveedor:</span>
                    <select v-model="currentProvider" @change="changeProvider">
                        <option value="ollama">🦙 Ollama</option>
                        <option value="openai">🤖 ChatGPT</option>
                    </select>
                </div>

                <button class="action-btn danger" @click="handleLogout">
                    <svg viewBox="0 0 24 24" fill="none">
                        <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" stroke-width="2"/>
                        <path d="M16 17L21 12L16 7" stroke="currentColor" stroke-width="2"/>
                        <path d="M21 12H9" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Cerrar Sesión
                </button>
            </div>
        </aside>

        <!-- Chat Area -->
        <main class="chat-area">
            <!-- Header -->
            <header class="chat-header">
                <div class="header-info">
                    <div class="current-bot-avatar">
                        <img :src="currentBot?.avatar" :alt="currentBot?.name" />
                    </div>
                    <div class="header-text">
                        <h2>{{ currentBot?.name }}</h2>
                        <span class="status">
                            <span class="status-indicator"></span>
                            {{ currentProvider === 'ollama' ? 'Ollama (Local)' : 'ChatGPT (Cloud)' }}
                        </span>
                    </div>
                </div>
                <div class="header-actions">
                    <button class="icon-btn" @click="clearChat" title="Limpiar conversación">
                        <svg viewBox="0 0 24 24" fill="none">
                            <path d="M3 6H5H21" stroke="currentColor" stroke-width="2"/>
                            <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                    </button>
                </div>
            </header>

            <!-- Messages -->
            <div ref="messagesRef" class="messages-container">
                <div class="messages-wrapper">
                    <transition-group name="message">
                        <div
                            v-for="(message, index) in currentBotMessages"
                            :key="index"
                            :class="['message', message.sender === 'user' ? 'message-user' : 'message-bot']"
                        >
                            <div class="message-avatar">
                                <img
                                    :src="message.sender === 'user' ? '/assets/user.png' : currentBot?.avatar"
                                    :alt="message.sender"
                                />
                            </div>
                            <div class="message-content">
                                <div class="message-bubble" v-html="formatMessage(message.content)"></div>
                                <span class="message-time">{{ message.time }}</span>
                            </div>
                        </div>
                    </transition-group>

                    <!-- Loading indicator -->
                    <div v-if="isLoading" class="message message-bot">
                        <div class="message-avatar">
                            <img :src="currentBot?.avatar" :alt="currentBot?.name" />
                        </div>
                        <div class="message-content">
                            <div class="message-bubble loading">
                                <span class="dot"></span>
                                <span class="dot"></span>
                                <span class="dot"></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Input Area -->
            <footer class="input-area">
                <div class="input-container">
                    <textarea
                        v-model="messageInput"
                        placeholder="Escribe tu mensaje..."
                        @keydown.enter.exact.prevent="sendMessage"
                        :disabled="isLoading"
                        rows="1"
                    ></textarea>
                    <button
                        class="send-btn"
                        @click="sendMessage"
                        :disabled="!messageInput.trim() || isLoading"
                    >
                        <svg viewBox="0 0 24 24" fill="none">
                            <path d="M22 2L11 13" stroke="currentColor" stroke-width="2"/>
                            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                    </button>
                </div>
            </footer>
        </main>
    </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';

export default {
    name: 'ChatView',
    data() {
        return {
            messageInput: '',
        };
    },
    computed: {
        ...mapState({
            bots: 'bots',
            currentBotIndex: 'currentBotIndex',
            isLoading: 'isLoading',
            currentProvider: 'currentProvider',
        }),
        ...mapGetters({
            currentBot: 'currentBot',
            currentBotMessages: 'currentBotMessages',
        }),
    },
    methods: {
        selectBot(index) {
            this.$store.commit('SET_CURRENT_BOT', index);
            this.$nextTick(() => this.scrollToBottom());
        },

        async sendMessage() {
            const message = this.messageInput.trim();
            if (!message || this.isLoading) return;

            const bot = this.currentBot;
            if (!bot) return;

            this.messageInput = '';

            try {
                await this.$store.dispatch('sendMessage', {
                    message,
                    botName: bot.name,
                    provider: this.currentProvider,
                });
                this.scrollToBottom();
            } catch (error) {
                console.error('Error sending message:', error);
            }
        },

        async clearChat() {
            const bot = this.currentBot;
            if (!bot) return;

            await this.$store.dispatch('clearConversation', bot.name);
        },

        changeProvider() {
            this.$store.dispatch('setProvider', this.currentProvider);
        },

        handleLogout() {
            this.$store.dispatch('logout');
            this.$router.push('/login');
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const container = this.$refs.messagesRef;
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        },

        getLastMessage(bot) {
            if (!bot.messages || bot.messages.length === 0) {
                return 'Sin mensajes';
            }
            const lastMsg = bot.messages[bot.messages.length - 1];
            return lastMsg.content.substring(0, 30) + '...';
        },

        formatMessage(content) {
            if (!content) return '';
            // Basic markdown-like formatting
            return content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/`(.*?)`/g, '<code>$1</code>')
                .replace(/\n/g, '<br>');
        },
    },
    mounted() {
        // Verificar autenticación
        if (!this.$store.getters.isLoggedIn) {
            this.$router.push('/login');
            return;
        }

        // Cargar bots
        this.$store.dispatch('fetchBots');
        this.$store.dispatch('loadModels');

        this.scrollToBottom();
    },
};
</script>

<style lang="scss" scoped>
.chat-view {
    display: flex;
    height: 100vh;
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

// ================================================
// SIDEBAR
// ================================================

.sidebar {
    width: 280px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 10;
}

.sidebar-header {
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);

    .logo-mini {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;

        svg {
            width: 20px;
            height: 20px;
            color: white;
        }
    }

    .app-name {
        font-size: 1.125rem;
        font-weight: 600;
        color: white;
    }
}

.bots-section {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;

    h3 {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255, 255, 255, 0.4);
        margin: 0 0 1rem;
        padding-left: 0.5rem;
    }
}

.bots-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.bot-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.02);

    &:hover {
        background: rgba(255, 255, 255, 0.06);
    }

    &.active {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }

    .bot-avatar {
        position: relative;

        img {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            object-fit: cover;
        }

        .status-dot {
            position: absolute;
            bottom: -2px;
            right: -2px;
            width: 12px;
            height: 12px;
            background: #22c55e;
            border: 2px solid #0f0c29;
            border-radius: 50%;
        }
    }

    .bot-info {
        flex: 1;
        min-width: 0;

        .bot-name {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            color: white;
            margin-bottom: 0.25rem;
        }

        .bot-preview {
            display: block;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.4);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    }
}

.sidebar-footer {
    padding: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.provider-selector {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;

    .label {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    select {
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: white;
        font-size: 0.875rem;
        cursor: pointer;

        &:focus {
            outline: none;
            border-color: #667eea;
        }

        option {
            background: #1a1a2e;
            color: white;
        }
    }
}

.action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.3s ease;

    svg {
        width: 18px;
        height: 18px;
    }

    &:hover {
        background: rgba(255, 255, 255, 0.1);
    }

    &.danger {
        &:hover {
            background: rgba(239, 68, 68, 0.2);
            border-color: rgba(239, 68, 68, 0.3);
            color: #ef4444;
        }
    }
}

// ================================================
// CHAT AREA
// ================================================

.chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 5;
}

.chat-header {
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);

    .header-info {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .current-bot-avatar {
        img {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            object-fit: cover;
            border: 2px solid rgba(102, 126, 234, 0.5);
        }
    }

    .header-text {
        h2 {
            font-size: 1.125rem;
            font-weight: 600;
            color: white;
            margin: 0 0 0.25rem;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.5);

            .status-indicator {
                width: 8px;
                height: 8px;
                background: #22c55e;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
        }
    }

    .header-actions {
        display: flex;
        gap: 0.5rem;
    }

    .icon-btn {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.6);
        cursor: pointer;
        transition: all 0.3s ease;

        svg {
            width: 20px;
            height: 20px;
        }

        &:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
    }
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;

    &::-webkit-scrollbar {
        width: 6px;
    }

    &::-webkit-scrollbar-track {
        background: transparent;
    }

    &::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
}

.messages-wrapper {
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

// ================================================
// MESSAGES
// ================================================

.message {
    display: flex;
    gap: 0.75rem;
    animation: slideIn 0.3s ease;

    &.message-user {
        flex-direction: row-reverse;

        .message-content {
            align-items: flex-end;
        }

        .message-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 18px 18px 4px 18px;
        }
    }

    &.message-bot {
        .message-bubble {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px 18px 18px 4px;
        }
    }

    .message-avatar {
        flex-shrink: 0;

        img {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            object-fit: cover;
        }
    }

    .message-content {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        max-width: 70%;
    }

    .message-bubble {
        padding: 0.875rem 1rem;
        color: white;
        font-size: 0.9375rem;
        line-height: 1.5;
        word-break: break-word;

        :deep(code) {
            background: rgba(0, 0, 0, 0.3);
            padding: 0.125rem 0.375rem;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
            font-size: 0.875em;
        }

        :deep(strong) {
            font-weight: 600;
        }

        :deep(em) {
            font-style: italic;
        }

        :deep(br) {
            content: '';
            display: block;
            margin: 0.25rem 0;
        }

        &.loading {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.875rem 1.25rem;

            .dot {
                width: 8px;
                height: 8px;
                background: rgba(255, 255, 255, 0.5);
                border-radius: 50%;
                animation: bounce 1.4s infinite ease-in-out;

                &:nth-child(1) { animation-delay: 0s; }
                &:nth-child(2) { animation-delay: 0.2s; }
                &:nth-child(3) { animation-delay: 0.4s; }
            }
        }
    }

    .message-time {
        font-size: 0.6875rem;
        color: rgba(255, 255, 255, 0.3);
    }
}

// ================================================
// INPUT AREA
// ================================================

.input-area {
    padding: 1rem 1.5rem 1.5rem;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.input-container {
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    align-items: flex-end;
    gap: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 0.5rem;
    transition: all 0.3s ease;

    &:focus-within {
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    textarea {
        flex: 1;
        background: transparent;
        border: none;
        color: white;
        font-size: 0.9375rem;
        padding: 0.75rem;
        resize: none;
        max-height: 150px;
        line-height: 1.5;

        &::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }

        &:focus {
            outline: none;
        }

        &:disabled {
            opacity: 0.5;
        }
    }

    .send-btn {
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;

        svg {
            width: 20px;
            height: 20px;
        }

        &:hover:not(:disabled) {
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    }
}

// ================================================
// ANIMATIONS
// ================================================

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-6px); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.message-enter-active {
    transition: all 0.3s ease;
}

.message-leave-active {
    transition: all 0.2s ease;
}

.message-enter {
    opacity: 0;
    transform: translateY(20px);
}

.message-leave-to {
    opacity: 0;
    transform: translateX(-20px);
}
</style>
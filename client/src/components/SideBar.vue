<template>
    <div class="sidebar">
        <section class="layout-sidebar">

            <section class="list_avatar">

                <ul class="bot-list">
                    <li v-for="(bot, index) in bots" :key="index" :class="{ current: currentBotIndex === index }"
                        @click="selectBot(index)">
                        <div class="bot-avatar">
                            <img :src="bot.avatar" alt="bot avatar" />
                            <h6 style="white-space: nowrap;">{{ bot.name }}</h6>
                        </div>
                        <div class="bot-info">
                            <p class="last-message">{{ bot.messages[bot.messages.length - 1].content }}</p>
                            <p class="chat-time">{{ bot.messages[bot.messages.length - 1].time }}</p>
                        </div>
                        <span class="break"></span>
                    </li>
                </ul>
            </section>
            <section class="actions_btn">
                <span class="btn_action">
                    <span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24" fill="none">
                            <path d="M3 6H5H21" stroke="#F5F5F5" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" />
                            <path
                                d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z"
                                stroke="#F5F5F5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                            <path d="M10 11V17" stroke="#F5F5F5" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" />
                            <path d="M14 11V17" stroke="#F5F5F5" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" />
                        </svg>
                    </span>
                    <p>Borrar Conversación</p>
                </span>
                <span class="btn_action">
                    <span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24" fill="none">
                            <path
                                d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9"
                                stroke="#F5F5F5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                            <path d="M16 17L21 12L16 7" stroke="#F5F5F5" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" />
                            <path d="M21 12H9" stroke="#F5F5F5" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" />
                        </svg>
                    </span>
                    <p>Cerrar Sesion</p>
                </span>
            </section>
        </section>

    </div>
</template>

<script>
export default {
    name: 'SideBar',
    computed: {
        bots() {
            return this.$store.state.bots
        },
        currentBotIndex() {
            return this.$store.state.currentBotIndex
        }
    },
    methods: {
        selectBot(index) {
            this.$store.commit('SET_CURRENT_BOT', index)
        },
    },
    // before the chat, use `bots.json` to load bot_name and init_prompt
    created() {
        this.$store.dispatch('fetchBots')
    }
}
</script>

<style lang="scss" scoped>
.sidebar {
    position: absolute;
    width: 20%;
    background-color: #121212;
    top: 0;
    left: 0;
    height: 100%;

    & p {
        margin: 0;
    }

    .layout-sidebar {

        display: grid;
        place-items: center;
        grid-auto-rows: 80% 20%;
        background-color: #262626;
        grid-template-areas:
            "map"
            "list_avatar"
            "actions_btn";
        height: 95%;
        width: 100%;
        margin-top: 5%;
        border-radius: 0rem 2.25rem 2.25rem 0rem;

        .map {
            width: 80%;
            height: 100%;
            padding-top: .5rem;

            & img {
                border-radius: 1.25rem; // Add this line to set the border-radius
            }
        }

        .actions_btn {
            width: 80%;
            height: 100%;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            justify-content: center;
            align-items: center;

            .btn_action:hover {
                background-color: #4b5563;
            }
            .btn_action {
                display: grid;
                align-items: center;
                grid-template-columns: 20% 80%;
                color: #F5F5F5;
                background-color: #0F969C;
                border-radius: 1.25rem;
                white-space: nowrap;
                width: 100%;
                height: 20%;
                gap: 1rem;
                cursor: pointer;

                & span {
                    display: grid;
                    place-items: center;
                }
            }
        }

        & section {
            width: 80%;
            height: 100%;
            margin-top: 13%;
        }
    }


    .list_avatar {
        display: grid;
        place-items: center;
        background-color: #4b5563;
        border-radius: 1.25rem;
        padding: 1rem;
    }

    h2 {
        margin-top: 0;
    }

    li {
        cursor: pointer;
        padding: 10px;
        border-radius: 10px;

        &.current {
            border: 0.1rem solid #e6e6e6;
        }
    }
}

.bot-list {
    list-style: none;
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    /* adjust this value to fit your layout */
    overflow-y: auto;
    gap: 1rem;
    display: flex;
    flex-direction: column;
}

.break {
    display: block;
    width: 100%;
    height: .1rem;
    background-color: #f5f5f5;
    margin-top: 0.5rem;
}

.bot-avatar {
    width: 50px;
    height: 50px;
    display: flex;
    flex-direction: row;
    align-items: center;

    img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        float: left;
        border-radius: 100%;
        margin-right: 10px;
    }

    h6 {
        white-space: nowrap;
        color: #F5F5F5;
        font-family: Inter;
        font-size: 1rem;
        font-style: normal;
        font-weight: 500;
        line-height: normal;
    }
}

.bot-info {
    flex: 1;

    h3 {
        font-size: 16px;
        font-weight: bold;
        margin: 0;
    }
}

.last-message {
    font-size: 14px;
    margin: 5px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: #f5f5f5;
}

.chat-time {
    font-size: 12px;
    color: #fff;
    margin: 0;
}
</style>

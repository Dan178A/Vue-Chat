<template>
    <div>
        <Header></Header>
        <section ref="messagesRef" class="chatList">
            <ul>
                <div v-for="(message, index) in bots[currentBotIndex].messages" :key="index">
                    <li v-if="message.sender === 'user'" class="chat-user">
                        <div class="chat-img"><img src="assets/user.png"></div>
                        <div class="time"><cite>{{ message.sender }}<i>{{ message.time }}</i></cite></div>
                        <div class="chat-content" style="white-space: pre-wrap;" v-text="message.content"></div>
                    </li>
                    <li v-if="message.sender !== 'user'" class="chat-others">
                        <div class="chat-img"><img :src="bots[currentBotIndex].avatar"></div>
                        <div class="time"><cite>{{ message.sender }}<i>{{ message.time }}</i></cite></div>
                        <div class="chat-content" style="white-space: pre-wrap;" v-text="message.content"></div>
                    </li>
                </div>
            </ul>
        </section>

        <section class="foot">
            <mt-field id="txtContent" v-model="content" class="con" placeholder="Please enter your prompt."
                style="border-radius: 1.25rem; background: #f5f5f5; color: #fff;">
            </mt-field>
            <span class="btn btn-send" v-on:click="sendMsg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M22 2L11 13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="white" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round" />
                </svg>
            </span>
        </section>
    </div>
</template>

<script>
import util from '../common/util'
import { Toast } from 'mint-ui'
import axios from 'axios'
import Header from './Header.vue'

export default {
    // eslint-disable-next-line vue/multi-word-component-names
    name: 'ChatList',
    components: {
        Header
    },
    data() {
        return {
            content: '',
            records: [], // chat record
        }
    },
    computed: {
        currentBotIndex() {
            return this.$store.state.currentBotIndex
        },
        bots() {
            return this.$store.state.bots
        }
    },
    methods: {
        sendMsg: function () {
            // save user's message
            if (this.content == '') {
                Toast('Please enter your prompt.')
                return
            }
            this.$store.commit('SEND_MESSAGE', {
                content: this.content,
                sender: 'user',
                receiver: this.bots[this.currentBotIndex].name,
                time: util.formatDate.format(new Date(), 'yyyy-MM-dd hh:mm:ss')
            })

            // Make the dialog box go to the bottom
            // Maybe it is Duplicate
            this.$nextTick(() => {
                this.$refs.messagesRef.scrollTop = this.$refs.messagesRef.scrollHeight
            })

            // make a request to server
            const param = {
                'bot': this.bots[this.currentBotIndex].name,
                'prompt': this.content,
            }
            const path = `http://${window.location.hostname}:5000/get_answer`
            axios.post(path, param)
                .then((res) => {
                    this.$store.commit('SEND_MESSAGE', {
                        content: res.data['answer'],
                        sender: this.bots[this.currentBotIndex].name,
                        receiver: 'user',
                        time: util.formatDate.format(new Date(), 'yyyy-MM-dd hh:mm:ss')
                    })
                })
                .catch((error) => {
                    this.$store.commit('SEND_MESSAGE', {
                        content: `${this.bots[this.currentBotIndex].name} happened error: ${error}`,
                        sender: this.bots[this.currentBotIndex].name,
                        receiver: 'user',
                        time: util.formatDate.format(new Date(), 'yyyy-MM-dd hh:mm:ss')
                    })
                })

            this.content = ''

            this.scrollToBottom()
            this.focusTxtContent()
        },

        // focus the input box
        focusTxtContent: function () {
            document.querySelector('#txtContent input').focus()
        },

        // Scroll bar scrolls to the bottom
        scrollToBottom: function () {
            setTimeout(function () {
                const tempChatList = document.getElementsByClassName('chatList')[0]
                tempChatList.scrollTop = tempChatList.scrollHeight
            }, 100)
        },
    },
    mounted: function () {
        this.scrollToBottom()
        this.focusTxtContent()
    }
}
</script>

<style lang="scss" scoped>
.chatList {
    position: absolute;
    top: 3.5rem;
    bottom: 0rem;
    left: 20%;
    right: 0px;
    overflow-y: auto;
    height: 90%;
    background-color: #121212;
}

.chatList ul {
    min-height: 300px;
}

.chatList ul .chat-user {
    text-align: right;
    padding-left: 0;
    padding-right: 60px;
}


.chatList ul .chat-others {
    text-align: left;
    padding-left: 60px;
    padding-right: 0;
}

.chatList ul li {
    position: relative;
    margin-bottom: 10px;
    padding-left: 60px;
    min-height: 68px;
    list-style-type: none;
}

.chat-user .chat-img {
    left: auto;
    right: 3px;
}

.chat-others .chat-img {
    left: 3px;
    right: auto;
}

.chat-img {
    position: absolute;
    left: 3px;
}

.chat-content,
.chat-img {
    display: inline-block;
    vertical-align: top;
    /*font-size: 14px;*/
}

.chat-img img {
    width: 40px;
    height: 40px;
    border-radius: 100%;
}

.time {
    width: 100%;
}

cite {
    left: auto;
    right: 60px;
    text-align: right;
}

cite {
    font-style: normal;
    line-height: 24px;
    font-size: 12px;
    white-space: nowrap;
    color: #999;
    text-align: left;
}

cite i {
    font-style: normal;
    padding-left: 5px;
    padding-right: 5px;
    font-size: 12px;
}

.chat-user .chat-content {
    margin-left: 0;
    text-align: left;
    background-color: #404040;
    color: #fff;
    border-radius: 1.25rem 0rem 1.25rem 1.25rem;
}

.chat-others .chat-content {
    margin-left: 0;
    text-align: left;
    background-color: #404040;
    color: #fff;
    border-radius: 0rem 1.25rem 1.25rem 1.25rem;
}

.chat-content {
    position: relative;
    line-height: 22px;
    padding: 10px 15px;
    background-color: #eee;
    border-radius: 3px;
    color: #333;
    word-break: break-all;
    max-width: 462px \9;
}

.chat-content,
.chat-img {
    display: inline-block;
    vertical-align: top;
    font-size: 14px;
}

.chat-content img {
    max-width: 100%;
    vertical-align: middle;
}

.chat-img {
    position: absolute;
    left: 3px;
}

.chat-content:after {
    content: '';
    position: absolute;
    left: -10px;
    top: 15px;
    width: 0;
    height: 0;
    border-style: solid dashed dashed;
    border-color: #eee transparent transparent;
    overflow: hidden;
    border-width: 10px;
}

.chat-user .chat-content:after {
    left: auto;
    right: -10px;
    border-top-color: #404040;
}

.chat-others .chat-content:after {
    left: -10px;
    right: auto;
    border-top-color: #404040;
}

.foot {
    width: 80%;
    min-height: 3rem;
    position: fixed;
    bottom: 0px;
    right: 0px;
}

.foot .con {
    position: absolute;
    left: 0px;
    right: 0px;

}

.btn {
    display: grid;
    vertical-align: top;
    font-size: 30px;
    line-height: 48px;
    /* margin-left: 5px; */
    padding: 0 0.5rem;
    background-color: #0F969C;
    color: #fff;
    border-radius: 3px;
    place-items: center;
    height: 100%;
}

.btn-send {
    position: absolute;
    right: 0px;
}
</style>

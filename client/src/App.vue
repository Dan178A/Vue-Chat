<template>
    <div class="app">
        <SideBar></SideBar>
        <ChatList></ChatList>
    </div>
</template>

<script>

import SideBar from '@/components/SideBar.vue'
import ChatList from '@/components/ChatList.vue'

export default {
    name: 'app',
    components: {
        ChatList,
        SideBar,
    }
}
</script>

<style>
.app {
    display: flex;
    flex-direction: row;
    height: 100vh;
    background-color: #121212;
}

body {
    height: 100vh;
    overflow: hidden;

    /* 156.25% */
}

p {
    color: #F5F5F5;
    font-family: Inter;
    font-size: 1rem;
    font-style: normal;
    font-weight: 500;
    line-height: 1.5625rem;
}


/* Estilos para los scroll en navegadores WebKit (Chrome, Safari) */
::-webkit-scrollbar {
    width: 8px;
    background-color: #f5f5f5;
}

::-webkit-scrollbar-thumb {
    background-color: #0a1b2d;
    border-radius: 4px;
}

/* Estilos para los scroll en navegadores Firefox */
body {
    scrollbar-width: thin;
    scrollbar-color: #ffffff #0a1b2d;
}

body::-webkit-scrollbar-track {
    background-color: #f5f5f5;
}

body::-webkit-scrollbar-thumb {
    background-color: #0a1b2d;
    border-radius: 4px;
}
</style>

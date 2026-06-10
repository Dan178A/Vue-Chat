<template>
    <div id="app">
        <router-view />
    </div>
</template>

<script>
export default {
    name: 'App',
};
</script>

<style lang="scss">
// ================================================
// ESTILOS GLOBALES
// ================================================

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    height: 100%;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f0c29;
    color: white;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

#app {
    height: 100%;
}

// ================================================
// SCROLLBAR
// ================================================

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;

    &:hover {
        background: rgba(255, 255, 255, 0.25);
    }
}

// ================================================
// SELECCIÓN
// ================================================

::selection {
    background: rgba(102, 126, 234, 0.4);
    color: white;
}

// ================================================
// FOCUS
// ================================================

:focus-visible {
    outline: 2px solid #667eea;
    outline-offset: 2px;
}
</style>
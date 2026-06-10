import Vue from 'vue';
import App from './App.vue';
import Store from '@/store';
import router from '@/router';

// ================================================
// CONFIGURACIÓN GLOBAL
// ================================================

Vue.config.productionTip = false;

// ================================================
// INICIALIZAR APP
// ================================================

new Vue({
    render: h => h(App),
    store: Store,
    router,
}).$mount('#app');
// ================================================
// Vue Router - Configuración de rutas
// ================================================

import Vue from 'vue';
import VueRouter from 'vue-router';
import { TokenService } from '@/services/api';

import LoginView from '@/views/LoginView.vue';
import ChatView from '@/views/ChatView.vue';

Vue.use(VueRouter);

// ================================================
// RUTAS
// ================================================

const routes = [
    {
        path: '/',
        redirect: '/login',
    },
    {
        path: '/login',
        name: 'Login',
        component: LoginView,
        meta: { requiresAuth: false },
    },
    {
        path: '/chat',
        name: 'Chat',
        component: ChatView,
        meta: { requiresAuth: true },
    },
];

// ================================================
// CREATE ROUTER
// ================================================

const router = new VueRouter({
    mode: 'history',
    routes,
});

// ================================================
// GUARD - PROTECCIÓN DE RUTAS
// ================================================

router.beforeEach((to, from, next) => {
    const isAuthenticated = TokenService.isAuthenticated();

    if (to.meta.requiresAuth && !isAuthenticated) {
        // No está autenticado, redirigir a login
        next('/login');
    } else if (to.path === '/login' && isAuthenticated) {
        // Ya está autenticado, redirigir a chat
        next('/chat');
    } else {
        next();
    }
});

export default router;
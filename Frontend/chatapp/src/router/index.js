/*import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import('../views/AboutView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router*/

import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../components/LoginPage.vue";
import HomePage from "../components/HomePage.vue";
import ChatPage from "../components/ChatPage.vue";
import GlobalChat from "../components/GlobalChat.vue";
import GroupPage from "../components/GroupPage.vue"; // Import GroupPage.vue

const routes = [
  { path: "/", name: "Login", component: LoginPage },
  { path: "/home", name: "Home", component: HomePage },
  { path: "/global-chat", name: "global-chat", component: GlobalChat },
  { 
    path: "/chat/:username", 
    name: "Chat", 
    component: ChatPage, 
    props: true // Pass username as a prop to ChatPage 
  },
  { 
    path: "/group/:groupId", 
    name: "GroupChat", 
    component: GroupPage, 
    props: true // Pass group ID as a prop to GroupPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
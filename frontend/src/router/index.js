import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '../views/MainPage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import DiagnosisPage from '../views/DiagnosisPage.vue'
import ProfilePage from '../views/ProfilePage.vue' 
import { isUserLoggedIn } from '../store/auth'

const routes = [
  { path: '/', component: MainPage },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  { path: '/diagnosis', component: DiagnosisPage ,meta: { requiresAuth: true }},
  { path: '/profile', component: ProfilePage } 
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isUserLoggedIn()) {
    next('/login')
  } else {
    next()
  }
})

export default router
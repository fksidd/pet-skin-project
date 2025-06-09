
import { createRouter, createWebHistory } from 'vue-router'
import { isUserLoggedIn } from '../store/auth'



const routes = [
  { path: '/', component: () => import('../views/MainPage.vue') },
  { path: '/login', component: () => import('../views/UserLoginPage.vue'), meta: { requiresGuest: true } },     
  { path: '/register', component: () => import('../views/UserRegisterPage.vue'), meta: { requiresGuest: true } }, 
  { path: '/diagnosis', component: () => import('../views/DiagnosisPage.vue'), meta: { requiresAuth: true } },
  { path: '/profile', component: () => import('../views/UserProfilePage.vue'), meta: { requiresAuth: true } },  
  {
    path: '/admin', 
    component: () => import('../views/AdminDashboardPage.vue'), 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  // 고객지원
  { path: '/inquiries', component: () => import('../views/UserInquiriesPage.vue'), meta: { requiresAuth: true } },
  { path: '/notices', component: () => import('../views/SystemNoticesPage.vue') },                             
  // 반려동물/진단 상세
  {
    path: '/diagnosis-history/:petId',
    component: () => import('../views/DiagnosisHistoryPage.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  { path: '/pet/:petId', component: () => import('../views/PetDetailPage.vue'), meta: { requiresAuth: true }, props: true }, 
  { path: '/diagnosis-detail/:diagnosisId', component: () => import('../views/DiagnosisDetailPage.vue'), meta: { requiresAuth: true }, props: true }, 
  // 관리자
  { 
    path: '/admin', 
    component: () => import('../views/AdminDashboardPage.vue'), 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: '/admin/users', 
    component: () => import('../views/AdminUsers.vue'), 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: '/admin/inquiries', 
    component: () => import('../views/AdminInquiries.vue'), 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: '/admin/notices', 
    component: () => import('../views/AdminNotices.vue'), 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  {
    path: '/hospitals',
    component: () => import('../views/HospitalMapPage.vue'),
    meta: { requiresAuth: true }
  }
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
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { logout } from './store/auth'

// API 기본 주소 설정
axios.defaults.baseURL = 'http://localhost:8000'

// 요청 인터셉터: 모든 요청에 액세스 토큰 추가
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 응답 인터셉터: 토큰 만료 시 자동 갱신
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    // 401 에러이고 재시도 안한 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) throw new Error('No refresh token')
        
        // 리프레시 토큰으로 새 액세스 토큰 요청
        const response = await axios.post('/api/refresh', 
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' }}
        )
        
        const newAccessToken = response.data.data.access_token
        localStorage.setItem('access_token', newAccessToken)
        axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`
        // 원래 요청 재시도
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        return axios(originalRequest)
        
      } catch (refreshError) {
        // 리프레시 토큰도 만료된 경우
        console.error('토큰 갱신 실패:', refreshError)
        logout()
        router.replace('/login')
        window.location.reload()
      }
    }
    return Promise.reject(error)
  }
)

// 앱 생성 및 마운트
createApp(App)
  .use(router)
  .mount('#app')
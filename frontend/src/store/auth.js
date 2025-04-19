// 로그인 상태와 사용자 정보를 전역에서 관리
import { ref } from 'vue'

export const isLoggedIn = ref(!!localStorage.getItem('userToken'))
export const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

export function login(token, info) {
  localStorage.setItem('userToken', token)
  localStorage.setItem('userInfo', JSON.stringify(info))
  isLoggedIn.value = true
  userInfo.value = info
}

export function logout() {
  localStorage.removeItem('userToken')
  localStorage.removeItem('userInfo')
  isLoggedIn.value = false
  userInfo.value = null
}

export function isUserLoggedIn() {
    return !!localStorage.getItem('userToken')
  }
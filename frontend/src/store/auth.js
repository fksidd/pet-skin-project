// src/store/auth.js
import { ref } from 'vue'

// userInfo 안전 파싱 함수
function safeParseUserInfo() {
  const raw = localStorage.getItem('userInfo')
  if (!raw || raw === "undefined") return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

// 로그인 상태와 사용자 정보를 전역에서 관리
export const isLoggedIn = ref(!!localStorage.getItem('access_token'))
export const userInfo = ref(safeParseUserInfo())

/**
 * 로그인 처리
 * @param {string} accessToken - 액세스 토큰
 * @param {string} refreshToken - 리프레시 토큰
 * @param {object} info - 사용자 정보 객체
 */
export function login(accessToken, refreshToken, info) {
  localStorage.setItem('access_token', accessToken)
  localStorage.setItem('refresh_token', refreshToken)
  localStorage.setItem('userInfo', JSON.stringify(info))
  isLoggedIn.value = true
  userInfo.value = info
}

/**
 * 로그아웃 처리
 */
export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('userInfo')
  isLoggedIn.value = false
  userInfo.value = null
}

/**
 * 로그인 여부 확인
 * @returns {boolean}
 */
export function isUserLoggedIn() {
  return !!localStorage.getItem('access_token')
}

/**
 * 토큰 갱신 
 * @param {string} newAccessToken - 새 액세스 토큰
 * @param {string} [newRefreshToken] - 새 리프레시 토큰(선택)
 */
export function updateTokens(newAccessToken, newRefreshToken) {
  if (newAccessToken) {
    localStorage.setItem('access_token', newAccessToken)
  }
  if (newRefreshToken) {
    localStorage.setItem('refresh_token', newRefreshToken)
  }
}

export function getAuthHeaders() {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}
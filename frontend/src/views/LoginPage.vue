<template>
  <div class="login-page">
    <h2>로그인</h2>
    <form @submit.prevent="onLogin">
      <div class="form-group">
        <label>이메일</label>
        <input v-model="email" type="email" required />
      </div>
      <div class="form-group">
        <label>비밀번호</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit" class="login-btn">로그인</button>
    </form>
    <p class="to-signup">계정이 없으신가요? <router-link to="/register">회원가입</router-link></p>
    <p v-if="error" class="error-msg">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../store/auth' 
import { fetchUserInfo } from '../api/user'

const email = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

async function onLogin() {
  error.value = ''
  try {
    // 1. 로그인 요청 (토큰 발급)
    const res = await fetch('http://localhost:8000/api/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        username: email.value,
        password: password.value
      })
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      error.value = err.detail || '로그인 실패'
      return
    }
    const data = await res.json()
    // 2. 토큰 저장
    localStorage.setItem('userToken', data.access_token)

    // 3. 전체 사용자 정보 받아오기 (user.js 활용)
    const user = await fetchUserInfo(data.access_token)
    // 4. userInfo에 전체 저장 (이름, 이메일, 전화번호 등)
    login(data.access_token, user)
    router.push('/')
  } catch (e) {
    error.value = '서버 오류가 발생했습니다.'
  }
}
</script>

<style scoped>
.login-page {
  max-width: 400px;
  margin: 3rem auto;
  padding: 2rem 1.5rem;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  background: #fff;
  text-align: center;
}
.login-page h2 {
  margin-bottom: 2rem;
  color: #7e57c2;
}
.form-group {
  margin-bottom: 1.3rem;
  text-align: left;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #444;
  font-weight: bold;
}
.form-group input {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}
.login-btn {
  background: #7e57c2;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 1rem;
  transition: background 0.2s;
}
.login-btn:hover {
  background: #5e35b1;
}
.to-signup {
  margin-top: 1.5rem;
  color: #888;
}
.error-msg {
  color: #d32f2f;
  margin-top: 1rem;
  font-size: 0.97rem;
}
</style>
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
import axios from 'axios'

const email = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

async function onLogin() {
  error.value = '';
  try {
    // 1. Axios로 POST 요청 (URLSearchParams 사용)
    const params = new URLSearchParams();
    params.append('username', email.value);
    params.append('password', password.value);

    const res = await axios.post('/api/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    // 2. 토큰 저장
    const { access_token, refresh_token } = res.data.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    // 3. 사용자 정보 조회 (user.js의 fetchUserInfo 활용)
    const user = await fetchUserInfo(access_token);

    // 4. 로그인 상태 업데이트
    login(access_token, refresh_token, user);
    router.push('/');
  } catch (err) {
    // 에러 처리
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = '아이디나 비밀번호가 틀립니다.';
    }
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
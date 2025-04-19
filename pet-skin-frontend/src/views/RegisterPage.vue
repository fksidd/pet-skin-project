<template>
  <div class="register-page">
    <h2>🐾 펫스프 회원가입</h2>
    <form @submit.prevent="onRegister">
      <div class="form-group">
        <label>이름</label>
        <input v-model="name" required />
      </div>
      <div class="form-group">
        <label>이메일</label>
        <input v-model="email" type="email" required />
      </div>
      <div class="form-group">
        <label>전화번호</label>
        <input v-model="phone" required />
      </div>
      <div class="form-group">
        <label>비밀번호</label>
        <input v-model="password" type="password" required />
      </div>
      <div class="form-group">
        <label>비밀번호 확인</label>
        <input v-model="passwordConfirm" type="password" required />
      </div>
      <button type="submit" class="register-btn">가입하기</button>
    </form>
    <p class="to-login">이미 계정이 있으신가요? <router-link to="/login">로그인</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const name = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const passwordConfirm = ref('')
const error = ref('')
const router = useRouter()

async function onRegister() {
  error.value = ''
  if (password.value !== passwordConfirm.value) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  try {
    const res = await fetch('http://localhost:8000/api/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.value,
        email: email.value,
        phone: phone.value,
        password: password.value
      })
    })
    if (res.ok) {
      alert('회원가입 성공! 로그인 해주세요.')
      router.push('/login')
    } else {
      const data = await res.json().catch(() => ({}))
      error.value = data.detail || '회원가입 실패'
    }
  } catch (e) {
    error.value = '서버 오류가 발생했습니다.'
  }
}
</script>
<style scoped>
.register-page {
  max-width: 420px;
  margin: 3rem auto;
  padding: 2rem 1.5rem;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  background: #fff;
  text-align: center;
}
.register-page h2 {
  margin-bottom: 2rem;
  color: #ffb74d;
}
.form-group {
  margin-bottom: 1.2rem;
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
.register-btn {
  background: #ffb74d;
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
.register-btn:hover {
  background: #ffa726;
}
.to-login {
  margin-top: 1.5rem;
  color: #888;
}
</style>
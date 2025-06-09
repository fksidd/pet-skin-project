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
        <input v-model="email" type="email" required :disabled="verified" />
        <button 
          type="button"
          class="verify-btn"
          @click="sendCode"
          :disabled="!email || codeSent || verified"
        >
          {{ codeSent && !verified ? '인증코드 전송' : '인증코드 전송' }}
        </button>
      </div>
      <div v-if="codeSent && !verified" class="form-group">
        <label>인증코드</label>
        <input v-model="code" maxlength="6" />
        <button 
          type="button"
          class="verify-btn"
          @click="verifyCode"
          :disabled="verified"
        >
          인증 확인
        </button>
        <span v-if="verified" class="verified-msg">✓ 인증 완료</span>
      </div>
      <div class="form-group">
        <label>전화번호</label>
        <input v-model="phone" @input="onPhoneInput" maxlength="13" required />
        <span v-if="phone && !isValidPhone" style="color:#d32f2f; font-size:0.95rem;">
          올바른 휴대전화 번호를 입력하세요 (예: 010-1234-5678)
        </span>
      </div>
      <div class="form-group">
        <label>비밀번호</label>
        <input v-model="password" type="password" required />
      </div>
      <div class="form-group">
        <label>비밀번호 확인</label>
        <input v-model="passwordConfirm" type="password" required />
      </div>
      <button 
        type="submit" 
        class="register-btn"
        :disabled="!verified"
      >가입하기</button>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>
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
const code = ref('')
const codeSent = ref(false)
const verified = ref(false)
const error = ref('')
const successMsg = ref('')
const router = useRouter()
const isValidPhone = ref(true)

function onPhoneInput(e) {
  let num = e.target.value.replace(/[^0-9]/g, '').slice(0, 11)
  if (num.length < 4) {
    phone.value = num
  } else if (num.length < 8) {
    phone.value = num.slice(0, 3) + '-' + num.slice(3)
  } else {
    phone.value = num.slice(0, 3) + '-' + num.slice(3, 7) + '-' + num.slice(7)
  }
  isValidPhone.value = /^010-\d{4}-\d{4}$/.test(phone.value)
}

// 이메일 인증코드 전송
import axios from 'axios'

async function sendCode() {
  error.value = ''
  try {
    await axios.post('/api/email/send-code', { 
      email: email.value 
    }, {
      headers: { 'Content-Type': 'application/json' }
    })
    codeSent.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || '오류 발생'
  }
}

async function verifyCode() {
  try {
    await axios.post('/api/email/verify-code', {
      email: email.value,
      code: code.value
    }, {
      headers: { 'Content-Type': 'application/json' }
    })
    verified.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || '인증 실패'
  }
}
async function onRegister() {
  error.value = ''
  successMsg.value = ''
  if (password.value !== passwordConfirm.value) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  if (!/^010-\d{4}-\d{4}$/.test(phone.value)) {
    error.value = '전화번호를 010-1234-5678 형식으로 입력하세요.'
    return
  }
  if (!verified.value) {
    error.value = '이메일 인증을 완료해주세요.'
    return
  }
  try {
    await axios.post('/api/register/', {
      name: name.value,
      email: email.value,
      phone: phone.value,
      password: password.value
    })
    alert('회원가입 성공! 로그인 해주세요.')
    router.push('/login')
  } catch (e) {
    const data = e.response?.data.data || {}
    error.value = data.detail || '회원가입 실패'
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
.verify-btn {
  background: #7e57c2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  margin-left: 0.5rem;
  cursor: pointer;
  transition: opacity 0.2s;
}
.verify-btn:disabled {
  background: #ddd;
  cursor: not-allowed;
}
.verified-msg {
  color: #4CAF50;
  margin-left: 0.5rem;
  font-weight: bold;
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
.register-btn:disabled {
  background: #ffe0b2;
  color: #aaa;
  cursor: not-allowed;
}
.register-btn:hover:enabled {
  background: #ffa726;
}
.to-login {
  margin-top: 1.5rem;
  color: #888;
}
.error-msg {
  color: #d32f2f;
  margin-top: 1rem;
  font-size: 0.97rem;
}
.success-msg {
  color: #4CAF50;
  margin-top: 1rem;
  font-size: 0.97rem;
}
</style>
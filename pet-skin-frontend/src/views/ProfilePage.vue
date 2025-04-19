<template>
    <div class="user-page">
      <h2>🐾 {{ userInfo?.name || '회원' }}님의 마이페이지</h2>
  
      <section class="user-info-section">
        <h3>📋 내 정보 </h3>
        <div class="user-info-list">
          <div class="user-info-item">
            <span class="label">이름</span>
            <span class="value">{{ userInfo?.name }}</span>
          </div>
          <div class="user-info-item">
            <span class="label">이메일</span>
            <span class="value">{{ userInfo?.email }}</span>
          </div>
          <div class="user-info-item">
            <span class="label">연락처</span>
            <span class="value">{{ userInfo?.phone || '-' }}</span>
          </div>
          <div class="user-info-item">
            <span class="label">비밀번호 변경</span>
            <button class="edit-btn" @click="onChangePassword">변경</button>
          </div>
        </div>
      </section>
  
      <section class="pet-section">
        <h3>🐶 함께하는 아이들</h3>
        <div v-if="pets && pets.length > 0">
          <div v-for="pet in pets" :key="pet.id" class="pet-card">
            <div class="pet-info">
              <span class="pet-name">🐾 {{ pet.name }}</span>
              <span class="pet-detail">({{ pet.breed }} · {{ pet.age }}살 · {{ pet.gender }})</span>
            </div>
            <button class="history-btn" @click="viewHistory(pet)">🩺 진단 이력 보기</button>
          </div>
        </div>
        <button class="add-pet-btn" @click="onAddPet">+ 반려동물 등록하기</button>
      </section>
  
      <section class="alert-section">
        <h3>🔔 알림 설정</h3>
        <div class="alert-item">
          <input type="checkbox" id="diagnosisAlert" v-model="alerts.diagnosis" />
          <label for="diagnosisAlert">진단 알림 받기</label>
        </div>
        <div class="alert-item">
          <input type="checkbox" id="newsAlert" v-model="alerts.news" />
          <label for="newsAlert">서비스 소식 받기</label>
        </div>
      </section>
  
      <section class="support-section">
        <h3>고객지원</h3>
        <button class="support-btn" @click="onViewInquiries">문의 내역 확인하기</button>
        <button class="support-btn" @click="onViewNotices">공지사항 보기</button>
        <button class="delete-btn" @click="onDeleteAccount">계정 삭제하기</button>
      </section>
    </div>
  </template>
  
  <script setup>
import { isLoggedIn, userInfo } from '../store/auth'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

if (!isLoggedIn.value) {
  router.replace('/login')
}

const pets = ref([])
const alerts = ref({ diagnosis: false, news: false })

onMounted(async () => {
  // 반려동물 목록 API 호출
  const petRes = await fetch('http://localhost:8000/api/pets', {
    headers: { Authorization: `Bearer ${localStorage.getItem('userToken')}` }
  })
  if (petRes.ok) {
    pets.value = await petRes.json()
  }

  // 알림 설정 API 호출
  const alertRes = await fetch('http://localhost:8000/api/alerts', {
    headers: { Authorization: `Bearer ${localStorage.getItem('userToken')}` }
  })
  if (alertRes.ok) {
    alerts.value = await alertRes.json()
  }
})

  
  function onChangePassword() {
    alert('비밀번호 변경 기능은 준비 중입니다.')
  }
  function onAddPet() {
    alert('반려동물 등록 기능은 준비 중입니다.')
  }
  function viewHistory(pet) {
    alert(`${pet.name}의 진단 이력 보기 (준비 중)`)
  }
  function onViewInquiries() {
    alert('문의 내역 확인 기능은 준비 중입니다.')
  }
  function onViewNotices() {
    alert('공지사항 보기 기능은 준비 중입니다.')
  }
  function onDeleteAccount() {
    if (confirm('정말로 계정을 삭제하시겠습니까?')) {
      alert('계정 삭제 기능은 준비 중입니다.')
    }
  }
  </script>
  
  <style scoped>
  .user-page {
    max-width: 540px;
    margin: 3rem auto;
    background: #fff;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    padding: 2.5rem 2rem;
    font-family: 'Noto Sans KR', sans-serif;
  }
  .user-page h2 {
    font-size: 1.7rem;
    margin-bottom: 2.2rem;
    color: #7e57c2;
    text-align: center;
  }
  section {
    margin-bottom: 2.1rem;
  }
  h3 {
    font-size: 1.1rem;
    color: #ffb74d;
    margin-bottom: 1rem;
  }
  .user-info-list {
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
  }
  .user-info-item {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 0.3rem;
  }
  .label {
    min-width: 90px;
    color: #333;
    font-weight: bold;
  }
  .value {
    color: #555;
  }
  .edit-btn {
    margin-left: 1rem;
    background: #ffb74d;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 0.3rem 1.1rem;
    font-size: 0.95rem;
    cursor: pointer;
  }
  .pet-section {
    margin-bottom: 2rem;
  }
  .pet-card {
    background: #f9fbe7;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .pet-info {
    font-size: 1.05rem;
    color: #444;
  }
  .pet-name {
    font-weight: bold;
  }
  .pet-detail {
    margin-left: 0.5rem;
    color: #888;
    font-size: 0.98rem;
  }
  .history-btn {
    background: #7e57c2;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 0.3rem 1.1rem;
    font-size: 0.95rem;
    cursor: pointer;
  }
  .add-pet-btn {
    margin-top: 0.7rem;
    background: #ffb74d;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 0.4rem 1.2rem;
    font-size: 1rem;
    cursor: pointer;
  }
  .alert-section {
    margin-bottom: 2rem;
  }
  .alert-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
    font-size: 1rem;
  }
  .support-section {
    margin-bottom: 0;
  }
  .support-btn,
  .delete-btn {
    display: block;
    width: 100%;
    margin-bottom: 0.7rem;
    background: #f1f1f1;
    color: #333;
    border: none;
    border-radius: 6px;
    padding: 0.6rem 0;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }
  .support-btn:hover {
    background: #ffe082;
  }
  .delete-btn {
    background: #fff1f0;
    color: #d32f2f;
    border: 1px solid #ffd6d6;
  }
  .delete-btn:hover {
    background: #ffd6d6;
  }
  </style>
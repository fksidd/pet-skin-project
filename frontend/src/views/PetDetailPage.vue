<template>
  <div class="pet-detail-page">
    <button class="back-btn" @click="goBack">← 목록으로</button>
    <div v-if="loading" class="loading">불러오는 중...</div>
    <div v-else-if="pet">
      <div class="pet-profile">
        <img v-if="pet.photo" :src="getPhotoUrl(pet.photo)" class="pet-photo" />
        <div v-else class="pet-photo placeholder">🐾</div>
        <div class="pet-info">
          <h2>{{ pet.name }}</h2>
          <p>품종: {{ pet.breed || '품종 미상' }}</p>
          <p>성별: {{ pet.gender }}</p>
          <p>나이: {{ pet.age ? pet.age + '살' : '미상' }}</p>
          <p>등록일: {{ formatDate(pet.created_at) }}</p>
        </div>
      </div>
      <h3>진단 이력</h3>
      <ul class="diagnosis-list">
        <li v-for="d in diagnoses" :key="d.id" @click="goToDiagnosisDetail(d.id)">
          <span class="date">{{ formatDate(d.created_at) }}</span>
          <span class="disease">{{ d.diagnosis }}</span>
          <span class="confidence">({{ (d.confidence * 100).toFixed(1) }}%)</span>
        </li>
        <li v-if="diagnoses.length === 0" class="no-diagnosis">진단 이력이 없습니다.</li>
      </ul>
    </div>
    <div v-else class="error-msg">반려동물 정보를 찾을 수 없습니다.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const petId = route.params.petId
const pet = ref(null)
const diagnoses = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    // 반려동물 정보
    const petRes = await axios.get(`/api/pets/${petId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    pet.value = petRes.data.data
    // 진단 이력
    const diagRes = await axios.get(`/api/diagnosis/history/${petId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    diagnoses.value = diagRes.data.data
  } catch (e) {
    pet.value = null
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit'})
}
function getPhotoUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  // 슬래시가 없으면 앞에 / 붙이기
  return path.startsWith('/') ? `http://localhost:8000${path}` : `http://localhost:8000/${path}`
}
function goBack() {
  router.back()
}
function goToDiagnosisDetail(diagnosisId) {
  router.push(`/diagnosis-detail/${diagnosisId}`)
}
</script>

<style scoped>
.pet-detail-page {
  max-width: 600px;
  margin: 2rem auto;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  padding: 2rem 1.5rem;
}
.pet-profile {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
}
.pet-photo {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #ffb74d;
}
.pet-photo.placeholder {
  background: #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: #bbb;
}
.pet-info h2 { margin: 0 0 1rem 0; color: #7e57c2; }
.diagnosis-list { list-style: none; padding: 0; }
.diagnosis-list li {
  padding: 0.9rem 0.5rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  display: flex;
  gap: 1rem;
  align-items: center;
  transition: background 0.2s;
}
.diagnosis-list li:hover { background: #f9fbe7; }
.date { color: #888; font-size: 0.97rem; }
.disease { font-weight: bold; color: #333; }
.confidence { color: #7e57c2; }
.no-diagnosis { color: #888; text-align: center; }
.back-btn {
  background: #f3e5f5;
  color: #7e57c2;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  cursor: pointer;
  margin-bottom: 1.5rem;
}
.loading { color: #888; text-align: center; }
.error-msg { color: #d32f2f; text-align: center; }
</style>
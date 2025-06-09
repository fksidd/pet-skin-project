<template>
  <div class="diagnosis-detail-page">
    <button class="back-btn" @click="goBack">← 목록으로</button>
    <div v-if="loading" class="loading">불러오는 중...</div>
    <div v-else-if="diagnosis">
      <h2>진단 상세 정보</h2>
      <div class="detail-section">
        <p><b>반려동물:</b> {{ diagnosis.pet_name }}</p>
        <p><b>진단명:</b> {{ diagnosis.diagnosis }}</p>
        <p><b>신뢰도:</b> {{ (diagnosis.confidence * 100).toFixed(1) }}%</p>
        <p><b>진단 일시:</b> {{ formatDateTime(diagnosis.created_at) }}</p>
        <p><b>상세 내용:</b> {{ diagnosis.details || '-' }}</p>
      </div>
    </div>
    <div v-else class="error-msg">진단 정보를 찾을 수 없습니다.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const diagnosisId = route.params.diagnosisId
const diagnosis = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    // 진단 상세 정보 가져오기
    const res = await axios.get(`/api/diagnosis/detail/${diagnosisId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    diagnosis.value = res.data.data
  } catch (e) {
    diagnosis.value = null
  } finally {
    loading.value = false
  }
})

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
function goBack() {
  router.back()
}
</script>

<style scoped>
.diagnosis-detail-page {
  max-width: 500px;
  margin: 2rem auto;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  padding: 2rem 1.5rem;
}
h2 {
  color: #7e57c2;
  margin-bottom: 1.5rem;
}
.detail-section p {
  margin: 0.7rem 0;
  font-size: 1.1rem;
}
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
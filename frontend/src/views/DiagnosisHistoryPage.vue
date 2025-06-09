<template>
  <div class="diagnosis-history">
    <div class="header">
      <h2>{{ petName }}의 진단 이력</h2>
      <button @click="goBack">← 뒤로 가기</button>
    </div>

    <!-- 통계 섹션 -->
    <div class="stats-section">
      <div class="stat-card">
        <h3>📊 총 진단 횟수</h3>
        <p class="stat-number">{{ stats.total_diagnoses }}</p>
      </div>
      <div class="stat-card">
        <h3>📅 최근 진단</h3>
        <p class="stat-value">{{ stats.latest_diagnosis || '없음' }}</p>
      </div>
      <div class="stat-card">
        <h3>🔥 최다 진단</h3>
        <p class="stat-value">{{ stats.most_common_diagnosis || '없음' }}</p>
      </div>
      <div class="stat-card">
        <h3>⭐ 평균 신뢰도</h3>
        <p class="stat-value">
          {{ stats.average_confidence ? (stats.average_confidence * 100).toFixed(1) + '%' : '-' }}
        </p>
      </div>
    </div>

    <!-- 진단 이력 테이블 (가로 스크롤 + min-width) -->
    <div class="history-table-container">
      <table class="history-table">
        <thead>
          <tr>
            <th>진단 일시</th>
            <th>질환명</th>
            <th>신뢰도</th>
            <th>상세 내용</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in diagnoses" :key="d.id">
            <td>{{ formatDate(d.created_at) }}</td>
            <td class="disease-name">{{ d.diagnosis }}</td>
            <td>
              <div class="confidence-bar">
                <div 
                  :style="{ width: ((d.confidence || 0) * 100) + '%' }"
                  :class="getConfidenceClass(d.confidence)"
                ></div>
                <span>{{ (d.confidence * 100).toFixed(1) }}%</span>
              </div>
            </td>
            <td class="details">{{ d.details || '-' }}</td>
          </tr>
          <tr v-if="diagnoses.length === 0">
            <td colspan="4" class="no-data">진단 이력이 없습니다.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 진단 분포 차트 -->
    <div class="chart-section">
      <h3>📈 질환 분포 (최근 30일)</h3>
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Chart from 'chart.js/auto'

const route = useRoute()
const router = useRouter()
const petId = route.params.petId
const petName = ref('')
const diagnoses = ref([])
const stats = ref({})
const chartCanvas = ref(null)

onMounted(async () => {
  try {
    const [historyRes, statsRes] = await Promise.all([
      axios.get(`/api/diagnosis/history/${petId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }),
      axios.get(`/api/diagnosis/stats/${petId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
    ])
    diagnoses.value = historyRes.data.data.results 
    stats.value = statsRes.data.data
    petName.value = diagnoses.value[0]?.pet_name || '반려동물'
    // 차트 필드명 수정: diagnosis_distribution
    if (stats.value.diagnosis_distribution) {
      initChart()
    }
  } catch (error) {
    console.error('데이터 로드 실패:', error)
    alert('진단 이력을 불러오는데 실패했습니다.')
  }
})

function initChart() {
  const ctx = chartCanvas.value.getContext('2d')
  // 필드명: diagnosis_distribution
  const labels = Object.keys(stats.value.diagnosis_distribution)
  const data = Object.values(stats.value.diagnosis_distribution)
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: '진단 횟수',
        data,
        backgroundColor: '#7e57c2',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      }
    }
  })
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr + 'Z') 
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getConfidenceClass(confidence) {
  if (confidence >= 0.8) return 'high'
  if (confidence >= 0.5) return 'medium'
  return 'low'
}

function goBack() {
  router.go(-1)
}
</script>

<style scoped>
.diagnosis-history {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}
.stat-card {
  background: #f9fbe7;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}
.stat-number {
  font-size: 2.5rem;
  color: #7e57c2;
  margin: 1rem 0;
}
.stat-value {
  font-size: 1.2rem;
  color: #666;
}
.history-table-container {
  overflow-x: auto;
  margin-bottom: 3rem;
}
.history-table {
  min-width: 700px;
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
}
th {
  background: #7e57c2;
  color: white;
}
.disease-name {
  font-weight: bold;
  color: #2d3a4b;
}
.confidence-bar {
  position: relative;
  height: 24px;
  background: #eee;
  border-radius: 12px;
  overflow: hidden;
}
.confidence-bar div {
  height: 100%;
  transition: width 0.3s ease;
}
.confidence-bar span {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 0.9rem;
}
.high { background: #4CAF50; }
.medium { background: #FFC107; }
.low { background: #F44336; }
.no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
}
.chart-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  margin-top: 2rem;
}
@media only screen and (max-width: 800px) {
  .diagnosis-history {
    padding: 0.5rem;
  }
  .history-table {
    font-size: 0.92rem;
    min-width: 500px;
  }
  .stats-section {
    grid-template-columns: 1fr;
  }
}
</style>
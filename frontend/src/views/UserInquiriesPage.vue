<template>
  <div class="inquiries-page">
    <h2>내 문의 내역</h2>
    <div v-if="loading" class="loading">불러오는 중...</div>
    <div v-else>
      <div v-if="inquiries?.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>등록된 문의가 없습니다.</p>
        <small>궁금한 사항이 있으시면 언제든 문의해 주세요!</small>
      </div>
      <ul v-else class="inquiry-list">
        <li v-for="inq in inquiries" :key="inq.id" class="inquiry-item">
          <div class="inquiry-content">{{ inq.content }}</div>
          <div class="inquiry-meta">
            <span class="inquiry-status" :class="getStatusClass(inq.status)">
              {{ inq.status }}
            </span>
            <span class="inquiry-date">{{ formatDate(inq.created_at) }}</span>
          </div>
          <div v-if="inq.answer" class="answer-section">
            <div class="answer-label">💬 답변</div>
            <div class="answer-content">{{ inq.answer }}</div>
          </div>
        </li>
      </ul>
    </div>
    <button class="back-btn" @click="goBack">← 마이페이지로</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const inquiries = ref([])
const loading = ref(true)
const router = useRouter()

onMounted(async () => {
  try {
    const res = await axios.get('/api/support/inquiries', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    inquiries.value = res.data.data
  } catch (e) {
    alert('문의 내역을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr + 'Z')
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit'})
}

function getStatusClass(status) {
  const classes = {
    '대기': 'status-waiting',
    '처리중': 'status-processing', 
    '완료': 'status-completed'
  }
  return classes[status] || 'status-waiting'
}

function goBack() {
  router.push('/profile')
}
</script>

<style scoped>
/* 기존 마이페이지와 동일한 스타일 */
.inquiries-page {
  max-width: 480px;
  margin: 3rem auto;
  padding: 2.5rem 2rem;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  text-align: left;
}

h2 {
  text-align: center;
  color: #7e57c2;
  margin-bottom: 2rem;
  font-size: 1.45rem;
  font-weight: bold;
}

.loading {
  color: #b39ddb;
  text-align: center;
  margin: 2rem 0;
  font-size: 1.1rem;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: #999;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state p {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  color: #666;
}

.empty-state small {
  color: #999;
  font-size: 0.95rem;
}

.inquiry-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.inquiry-item {
  background: #fafaff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  padding: 1.3rem;
  margin-bottom: 1rem;
  border-left: 4px solid #7e57c2;
  transition: box-shadow 0.2s ease;
}

.inquiry-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.inquiry-content {
  font-size: 1.05rem;
  color: #333;
  margin-bottom: 0.8rem;
  line-height: 1.5;
  word-break: break-word;
}

.inquiry-meta {
  font-size: 0.9rem;
  color: #888;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
}

.inquiry-status {
  font-weight: bold;
  padding: 0.2rem 0.8rem;
  border-radius: 12px;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.inquiry-status.status-waiting {
  background: #fff3cd;
  color: #856404;
}

.inquiry-status.status-processing {
  background: #d1ecf1;
  color: #0c5460;
}

.inquiry-status.status-completed {
  background: #d4edda;
  color: #155724;
}

.inquiry-date {
  color: #999;
  font-size: 0.9rem;
}

.answer-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 0.8rem;
  border-left: 3px solid #ffb74d;
}

.answer-label {
  font-weight: bold;
  color: #ffb74d;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.answer-content {
  color: #333;
  line-height: 1.5;
  word-break: break-word;
}

.back-btn {
  margin-top: 2rem;
  background: #f3e5f5;
  color: #7e57c2;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  cursor: pointer;
  font-weight: bold;
  width: 100%;
  font-size: 1.05rem;
  transition: background 0.2s ease;
}

.back-btn:hover {
  background: #ede7f6;
}
.inquiry-answer {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
  border-left: 3px solid #7e57c2;
}
.answer-label {
  font-weight: bold;
  color: #7e57c2;
  margin-bottom: 0.5rem;
}
.answer-content {
  color: #333;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}
.answer-date {
  font-size: 0.9rem;
  color: #666;
}
</style>
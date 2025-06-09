<template>
  <div class="notices-page">
    <h2>공지사항</h2>
    <div v-if="loading" class="loading">불러오는 중...</div>
    <div v-else>
      <div v-if="notices.length === 0" class="empty-state">
        <div class="empty-icon">📢</div>
        <p>등록된 공지사항이 없습니다.</p>
        <small>새로운 소식이 있으면 알려드리겠습니다!</small>
      </div>
      <ul v-else class="notice-list">
        <li v-for="(notice, index) in notices" :key="notice.id" 
            class="notice-item" 
            :class="{ 'latest': index === 0 }">
          <div v-if="index === 0" class="latest-badge">최신</div>
          <h3 class="notice-title">{{ notice.title }}</h3>
          <div class="notice-content">{{ notice.content }}</div>
          <div class="notice-date">{{ formatDate(notice.created_at) }}</div>
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

const notices = ref([])
const loading = ref(true)
const router = useRouter()

onMounted(async () => {
  try {
    const res = await axios.get('/api/support/notices')
    notices.value = res.data.data
  } catch (e) {
    alert('공지사항을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr + 'Z')
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit'})
}

function goBack() {
  router.push('/profile')
}
</script>

<style scoped>
/* 기존 마이페이지와 동일한 스타일 */
.notices-page {
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

.notice-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.notice-item {
  background: #fafaff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  padding: 1.3rem;
  margin-bottom: 1rem;
  border-left: 4px solid #ffb74d;
  position: relative;
  transition: box-shadow 0.2s ease;
}

.notice-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.notice-item.latest {
  border-left-color: #7e57c2;
  background: #f8f4ff;
}

.latest-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: #7e57c2;
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: bold;
}

.notice-title {
  font-size: 1.1rem;
  color: #7e57c2;
  margin: 0 0 0.5rem 0;
  font-weight: bold;
  line-height: 1.3;
  padding-right: 3rem; /* 배지 공간 확보 */
}

.notice-content {
  color: #444;
  margin-bottom: 0.8rem;
  line-height: 1.5;
  word-break: break-word;
}

.notice-date {
  font-size: 0.9rem;
  color: #999;
  text-align: right;
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
</style>

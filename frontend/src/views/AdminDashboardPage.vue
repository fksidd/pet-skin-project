<template>
  <div class="admin-page">
    <h2>🛠️ 관리자 대시보드</h2>
    
    <!-- 통계 카드 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <h3>{{ stats.totalUsers }}</h3>
            <p>전체 회원</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💬</div>
          <div class="stat-info">
            <h3>{{ stats.pendingInquiries }}</h3>
            <p>대기중 문의</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📢</div>
          <div class="stat-info">
            <h3>{{ stats.totalNotices }}</h3>
            <p>전체 공지사항</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 관리 메뉴 -->
    <section class="menu-section">
      <h3>📋 관리 메뉴</h3>
      <div class="menu-buttons">
        <button class="menu-btn" @click="router.push('/admin/users')">
          <span class="btn-icon">👥</span>
          <span class="btn-text">회원 관리</span>
          <span class="btn-desc">회원 정보 조회 및 관리</span>
        </button>
        <button class="menu-btn" @click="router.push('/admin/inquiries')">
          <span class="btn-icon">💬</span>
          <span class="btn-text">문의 관리</span>
          <span class="btn-desc">고객 문의 답변 및 관리</span>
        </button>
        <button class="menu-btn" @click="router.push('/admin/notices')">
          <span class="btn-icon">📢</span>
          <span class="btn-text">공지사항 관리</span>
          <span class="btn-desc">공지사항 작성 및 관리</span>
        </button>
      </div>
    </section>

    <!-- 로그아웃 -->
    <section class="logout-section">
      <button class="logout-btn" @click="handleLogout">
        <span class="btn-icon">🚪</span>
        관리자 로그아웃
      </button>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { logout } from '../store/auth'

const router = useRouter()
const stats = ref({
  totalUsers: 0,
  pendingInquiries: 0,
  totalNotices: 0
})

onMounted(async () => {
  await loadStats()
})

async function loadStats() {
  try {
    const [usersRes, inquiriesRes, noticesRes] = await Promise.all([
      axios.get('/api/admin/users', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }),
      axios.get('/api/admin/inquiries', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }),
      axios.get('/api/admin/notices', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
    ])
    
    stats.value = {
      totalUsers: usersRes.data.data.length,
      pendingInquiries: inquiriesRes.data.data.filter(inq => inq.status === '대기').length,
      totalNotices: noticesRes.data.data.length
    }
  } catch (error) {
    console.error('통계 로딩 실패:', error)
  }
}

function handleLogout() {
  if (confirm('정말 로그아웃 하시겠습니까?')) {
    logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.admin-page {
  max-width: 600px;
  margin: 3rem auto;
  padding: 2.5rem 2rem;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}

h2 {
  text-align: center;
  color: #7e57c2;
  margin-bottom: 2rem;
  font-size: 1.6rem;
  font-weight: bold;
}

.stats-section {
  margin-bottom: 2.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: #fafaff;
  border-radius: 12px;
  padding: 1.2rem;
  text-align: center;
  border-left: 4px solid #7e57c2;
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-info h3 {
  font-size: 1.8rem;
  color: #7e57c2;
  margin: 0 0 0.2rem 0;
  font-weight: bold;
}

.stat-info p {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}

.menu-section h3 {
  color: #ffb74d;
  font-size: 1.1rem;
  margin-bottom: 1.2rem;
  font-weight: bold;
}

.menu-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.menu-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  padding: 1.2rem;
  border: none;
  border-radius: 12px;
  background: #fafaff;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  border-left: 4px solid #ffb74d;
}

.menu-btn:hover {
  background: #f3e5f5;
  transform: translateX(5px);
}

.btn-icon {
  font-size: 1.5rem;
  min-width: 40px;
}

.btn-text {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  min-width: 120px;
}

.btn-desc {
  font-size: 0.9rem;
  color: #666;
}

.logout-section {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  background: #ffebee;
  color: #e53935;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s ease;
}

.logout-btn:hover {
  background: #ffcdd2;
}
</style>

<template>
  <div class="admin-users-page">
    <div class="page-header">
      <h2>👥 회원 관리</h2>
      <button class="back-btn" @click="router.push('/admin')">← 대시보드로</button>
    </div>

    <div v-if="loading" class="loading">회원 정보를 불러오는 중...</div>
    
    <div v-else>
      <div class="users-stats">
        <span class="stat">전체 회원: {{ users.length }}명</span>
        <span class="stat">일반 회원: {{ users.filter(u => u.role === 'user').length }}명</span>
        <span class="stat">관리자: {{ users.filter(u => u.role === 'admin').length }}명</span>
      </div>

      <div v-if="users.length === 0" class="empty-state">
        <div class="empty-icon">👤</div>
        <p>등록된 회원이 없습니다.</p>
      </div>

      <div v-else class="users-list">
        <div v-for="user in users" :key="user.id" class="user-card">
          <div class="user-info">
            <div class="user-main">
              <h3>{{ user.name }}</h3>
              <span class="user-role" :class="user.role">{{ user.role === 'admin' ? '관리자' : '일반회원' }}</span>
            </div>
            <div class="user-details">
              <p>📧 {{ user.email }}</p>
              <p>📅 가입일: {{ formatDate(user.created_at) }}</p>
            </div>
          </div>
          <div class="user-actions">
            <button 
              v-if="user.role !== 'admin'" 
              class="delete-btn" 
              @click="confirmDeleteUser(user)"
            >
              🗑️ 삭제
            </button>
            <span v-else class="admin-label">관리자</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal">
        <h3>회원 삭제 확인</h3>
        <p>{{ selectedUser?.name }}님을 정말 삭제하시겠습니까?<br>
        모든 관련 데이터가 삭제되며 복구할 수 없습니다.</p>
        <div class="modal-actions">
          <button class="confirm-btn" @click="deleteUser">삭제</button>
          <button class="cancel-btn" @click="cancelDelete">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const users = ref([])
const loading = ref(true)
const showDeleteModal = ref(false)
const selectedUser = ref(null)

onMounted(async () => {
  await loadUsers()
})

async function loadUsers() {
  try {
    const response = await axios.get('/api/admin/users', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    users.value = response.data.data
  } catch (error) {
    alert('회원 정보를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

function confirmDeleteUser(user) {
  selectedUser.value = user
  showDeleteModal.value = true
}

async function deleteUser() {
  try {
    const response = await axios.delete(`/api/admin/users/${selectedUser.value.id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    if (response.data.success) {
      await loadUsers()
      showDeleteModal.value = false
      alert('회원이 삭제되었습니다.')
    } else {
      alert(response.data.message) // 서버에서 온 메시지 표시
    }
  } catch (error) {
    alert(error.response?.data?.message || '삭제에 실패했습니다.')
  }
}

function cancelDelete() {
  showDeleteModal.value = false
  selectedUser.value = null
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr + 'Z')
  return d.toLocaleDateString('ko-KR')
}
</script>

<style scoped>
.admin-users-page {
  max-width: 700px;
  margin: 3rem auto;
  padding: 2.5rem 2rem;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  color: #7e57c2;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.back-btn {
  background: #f3e5f5;
  color: #7e57c2;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  font-weight: bold;
}

.back-btn:hover {
  background: #ede7f6;
}

.loading {
  text-align: center;
  color: #666;
  margin: 3rem 0;
}

.users-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.stat {
  background: #fafaff;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #666;
  border: 1px solid #ede7f6;
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: #999;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.user-card {
  background: #fafaff;
  border-radius: 12px;
  padding: 1.3rem;
  border-left: 4px solid #7e57c2;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  flex: 1;
}

.user-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.8rem;
}

.user-main h3 {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
}

.user-role {
  padding: 0.2rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.user-role.admin {
  background: #ffecb3;
  color: #f57c00;
}

.user-role.user {
  background: #e3f2fd;
  color: #1976d2;
}

.user-details p {
  margin: 0.3rem 0;
  color: #666;
  font-size: 0.9rem;
}

.user-actions {
  display: flex;
  align-items: center;
}

.delete-btn {
  background: #ffebee;
  color: #e53935;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
}

.delete-btn:hover {
  background: #ffcdd2;
}

.admin-label {
  color: #ffb74d;
  font-weight: bold;
  font-size: 0.9rem;
}

/* 모달 스타일 (기존과 동일) */
.modal-overlay {
  position: fixed;
  z-index: 1000;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
}

.modal h3 {
  margin-top: 0;
  color: #7e57c2;
  text-align: center;
}

.modal p {
  text-align: center;
  line-height: 1.5;
  color: #666;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.confirm-btn {
  background: #e53935;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  cursor: pointer;
  font-weight: bold;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  cursor: pointer;
}
</style>

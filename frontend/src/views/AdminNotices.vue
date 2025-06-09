<template>
  <div class="admin-notices-page">
    <div class="page-header">
      <h2>📢 공지사항 관리</h2>
      <div class="header-actions">
        <button class="add-btn" @click="openAddModal">+ 새 공지 작성</button>
        <button class="back-btn" @click="router.push('/admin')">← 대시보드로</button>
      </div>
    </div>

    <div v-if="loading" class="loading">공지사항을 불러오는 중...</div>
    
    <div v-else>
      <div class="notices-stats">
        <span class="stat">전체 공지사항: {{ notices.length }}개</span>
      </div>

      <div v-if="notices.length === 0" class="empty-state">
        <div class="empty-icon">📢</div>
        <p>등록된 공지사항이 없습니다.</p>
        <button class="add-first-btn" @click="openAddModal">첫 공지사항 작성하기</button>
      </div>

      <div v-else class="notices-list">
        <div v-for="(notice, index) in notices" :key="notice.id" class="notice-card">
          <div class="notice-header">
            <h3>{{ notice.title }}</h3>
            <div class="notice-meta">
              <span v-if="index === 0" class="latest-badge">최신</span>
              <span class="notice-date">{{ formatDate(notice.created_at) }}</span>
            </div>
          </div>
          
          <div class="notice-content">
            <p>{{ notice.content }}</p>
          </div>

          <div class="notice-actions">
            <button class="edit-btn" @click="openEditModal(notice)">
              ✏️ 수정
            </button>
            <button class="delete-btn" @click="confirmDeleteNotice(notice)">
              🗑️ 삭제
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 공지사항 작성/수정 모달 -->
    <div v-if="showNoticeModal" class="modal-overlay" @click.self="closeNoticeModal">
      <div class="modal">
        <h3>{{ isEditing ? '공지사항 수정' : '새 공지사항 작성' }}</h3>
        <form @submit.prevent="submitNotice">
          <div class="form-group">
            <label>제목</label>
            <input v-model="noticeForm.title" type="text" required placeholder="공지사항 제목을 입력하세요" />
          </div>
          <div class="form-group">
            <label>내용</label>
            <textarea 
              v-model="noticeForm.content" 
              placeholder="공지사항 내용을 입력하세요" 
              rows="8" 
              required
            ></textarea>
          </div>
          <div class="modal-actions">
            <button type="submit" class="save-btn">{{ isEditing ? '수정' : '등록' }}</button>
            <button type="button" @click="closeNoticeModal" class="cancel-btn">취소</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal">
        <h3>공지사항 삭제 확인</h3>
        <p>"{{ selectedNotice?.title }}"을(를) 정말 삭제하시겠습니까?<br>삭제된 공지사항은 복구할 수 없습니다.</p>
        <div class="modal-actions">
          <button class="confirm-btn" @click="deleteNotice">삭제</button>
          <button class="cancel-btn" @click="cancelDelete">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const notices = ref([])
const loading = ref(true)
const showNoticeModal = ref(false)
const showDeleteModal = ref(false)
const selectedNotice = ref(null)
const isEditing = ref(false)

const noticeForm = reactive({
  title: '',
  content: ''
})

onMounted(async () => {
  await loadNotices()
})

async function loadNotices() {
  try {
    const response = await axios.get('/api/admin/notices', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    notices.value = response.data.data
  } catch (error) {
    alert('공지사항을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  resetForm()
  isEditing.value = false
  showNoticeModal.value = true
}

function openEditModal(notice) {
  noticeForm.title = notice.title
  noticeForm.content = notice.content
  selectedNotice.value = notice
  isEditing.value = true
  showNoticeModal.value = true
}

function closeNoticeModal() {
  showNoticeModal.value = false
  resetForm()
}

function resetForm() {
  noticeForm.title = ''
  noticeForm.content = ''
  selectedNotice.value = null
}

async function submitNotice() {
  try {
    if (isEditing.value) {
      await axios.put(`/api/support/notices/${selectedNotice.value.id}`, noticeForm, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      alert('공지사항이 수정되었습니다.')
    } else {
      await axios.post('/api/support/notices', noticeForm, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      alert('공지사항이 등록되었습니다.')
    }
    await loadNotices()
    closeNoticeModal()
  } catch (error) {
    alert('처리에 실패했습니다.')
  }
}

function confirmDeleteNotice(notice) {
  selectedNotice.value = notice
  showDeleteModal.value = true
}

async function deleteNotice() {
  try {
    await axios.delete(`/api/admin/notices/${selectedNotice.value.id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    await loadNotices()
    showDeleteModal.value = false
    alert('공지사항이 삭제되었습니다.')
  } catch (error) {
    alert('삭제에 실패했습니다.')
  }
}

function cancelDelete() {
  showDeleteModal.value = false
  selectedNotice.value = null
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR')
}
</script>

<style scoped>
.admin-notices-page {
  max-width: 800px;
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

.header-actions {
  display: flex;
  gap: 1rem;
}

.add-btn {
  background: #ffb74d;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  font-weight: bold;
}

.add-btn:hover {
  background: #ffa726;
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

.notices-stats {
  margin-bottom: 1.5rem;
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

.add-first-btn {
  background: #ffb74d;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 1rem 2rem;
  cursor: pointer;
  font-weight: bold;
  margin-top: 1rem;
}

.notices-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.notice-card {
  background: #fafaff;
  border-radius: 12px;
  padding: 1.3rem;
  border-left: 4px solid #ffb74d;
}

.notice-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.notice-header h3 {
  margin: 0;
  color: #7e57c2;
  font-size: 1.2rem;
  font-weight: bold;
  flex: 1;
  margin-right: 1rem;
}

.notice-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.latest-badge {
  background: #7e57c2;
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: bold;
}

.notice-date {
  color: #666;
  font-size: 0.9rem;
}

.notice-content {
  margin-bottom: 1rem;
}

.notice-content p {
  color: #444;
  line-height: 1.6;
  margin: 0;
}

.notice-actions {
  display: flex;
  gap: 0.8rem;
  justify-content: flex-end;
}

.edit-btn {
  background: #7e57c2;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
}

.edit-btn:hover {
  background: #5e35b1;
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

/* 모달 스타일 (기존과 동일) */
.modal-overlay {
  position: fixed;
  z-index: 1000;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.modal {
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  color: #7e57c2;
  text-align: center;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #7e57c2;
  font-weight: bold;
  font-size: 1.05rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  background: #fafaff;
}

.form-group textarea {
  resize: vertical;
  min-height: 200px;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #b39ddb;
  outline: none;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.save-btn, .confirm-btn {
  background: #7e57c2;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  cursor: pointer;
  font-weight: bold;
}

.save-btn:hover, .confirm-btn:hover {
  background: #5e35b1;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #e0e0e0;
}
</style>

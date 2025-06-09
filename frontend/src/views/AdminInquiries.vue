<template>
  <div class="admin-inquiries-page">
    <div class="page-header">
      <h2>💬 문의 관리</h2>
      <button class="back-btn" @click="router.push('/admin')">← 대시보드로</button>
    </div>

    <div v-if="loading" class="loading">문의 내역을 불러오는 중...</div>
    
    <div v-else>
      <div class="inquiries-stats">
        <span class="stat waiting">대기: {{ inquiries.filter(i => i.status === '대기').length }}건</span>
        <span class="stat processing">처리중: {{ inquiries.filter(i => i.status === '처리중').length }}건</span>
        <span class="stat completed">완료: {{ inquiries.filter(i => i.status === '완료').length }}건</span>
      </div>

      <div v-if="inquiries.length === 0" class="empty-state">
        <div class="empty-icon">💬</div>
        <p>등록된 문의가 없습니다.</p>
      </div>

      <div v-else class="inquiries-list">
        <div v-for="inquiry in inquiries" :key="inquiry.id" class="inquiry-card">
          <div class="inquiry-header">
            <span class="inquiry-status" :class="getStatusClass(inquiry.status)">
              {{ inquiry.status }}
            </span>
            <span class="inquiry-date">{{ formatDate(inquiry.created_at) }}</span>
          </div>
          
          <div class="inquiry-content">
            <p>{{ inquiry.content }}</p>
          </div>

          <div v-if="inquiry.answer" class="answer-section">
            <div class="answer-label">📋 답변</div>
            <div class="answer-content">{{ inquiry.answer }}</div>
          </div>

          <div class="inquiry-actions">
            <button 
              v-if="inquiry.status !== '완료'" 
              class="answer-btn" 
              @click="openAnswerModal(inquiry)"
            >
              💬 답변하기
            </button>
            <button class="delete-btn" @click="confirmDeleteInquiry(inquiry)">
              🗑️ 삭제
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 답변 모달 -->
    <div v-if="showAnswerModal" class="modal-overlay" @click.self="closeAnswerModal">
      <div class="modal">
        <h3>문의 답변하기</h3>
        <div class="original-inquiry">
          <strong>문의 내용:</strong>
          <p>{{ selectedInquiry?.content }}</p>
        </div>
        <form @submit.prevent="submitAnswer">
          <textarea 
            v-model="answerText" 
            placeholder="답변을 입력하세요" 
            rows="5" 
            required
          ></textarea>
          <div class="modal-actions">
            <button type="submit" class="save-btn">답변 등록</button>
            <button type="button" @click="closeAnswerModal" class="cancel-btn">취소</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal">
        <h3>문의 삭제 확인</h3>
        <p>이 문의를 정말 삭제하시겠습니까?<br>삭제된 문의는 복구할 수 없습니다.</p>
        <div class="modal-actions">
          <button class="confirm-btn" @click="deleteInquiry">삭제</button>
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
const inquiries = ref([])
const loading = ref(true)
const showAnswerModal = ref(false)
const showDeleteModal = ref(false)
const selectedInquiry = ref(null)
const answerText = ref('')

onMounted(async () => {
  await loadInquiries()
})

async function loadInquiries() {
  try {
    const response = await axios.get('/api/admin/inquiries', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    inquiries.value = response.data.data
  } catch (error) {
    alert('문의 내역을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

function openAnswerModal(inquiry) {
  selectedInquiry.value = inquiry
  answerText.value = inquiry.answer || ''
  showAnswerModal.value = true
}

function closeAnswerModal() {
  showAnswerModal.value = false
  selectedInquiry.value = null
  answerText.value = ''
}

async function submitAnswer() {
  try {
    await axios.put(`/api/support/inquiries/${selectedInquiry.value.id}/answer`, 
      { answer: answerText.value },
      { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
    )
    await loadInquiries()
    closeAnswerModal()
    alert('답변이 등록되었습니다.')
  } catch (error) {
    alert('답변 등록에 실패했습니다.')
  }
}

function confirmDeleteInquiry(inquiry) {
  selectedInquiry.value = inquiry
  showDeleteModal.value = true
}

async function deleteInquiry() {
  try {
    await axios.delete(`/api/admin/inquiries/${selectedInquiry.value.id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    await loadInquiries()
    showDeleteModal.value = false
    alert('문의가 삭제되었습니다.')
  } catch (error) {
    alert('삭제에 실패했습니다.')
  }
}

function cancelDelete() {
  showDeleteModal.value = false
  selectedInquiry.value = null
}

function getStatusClass(status) {
  const classes = {
    '대기': 'status-waiting',
    '처리중': 'status-processing',
    '완료': 'status-completed'
  }
  return classes[status] || 'status-waiting'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr + 'Z')
  return d.toLocaleDateString('ko-KR')
}
</script>

<style scoped>
/* 기본 레이아웃은 AdminUsers와 동일 */
.admin-inquiries-page {
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

.back-btn {
  background: #f3e5f5;
  color: #7e57c2;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  font-weight: bold;
}

.inquiries-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.stat {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
}

.stat.waiting {
  background: #fff3cd;
  color: #856404;
}

.stat.processing {
  background: #d1ecf1;
  color: #0c5460;
}

.stat.completed {
  background: #d4edda;
  color: #155724;
}

.inquiries-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.inquiry-card {
  background: #fafaff;
  border-radius: 12px;
  padding: 1.3rem;
  border-left: 4px solid #7e57c2;
}

.inquiry-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.inquiry-status {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: bold;
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
  color: #666;
  font-size: 0.9rem;
}

.inquiry-content {
  margin-bottom: 1rem;
}

.inquiry-content p {
  color: #333;
  line-height: 1.5;
  margin: 0;
}

.answer-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
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
}

.inquiry-actions {
  display: flex;
  gap: 0.8rem;
  justify-content: flex-end;
}

.answer-btn {
  background: #7e57c2;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
}

.answer-btn:hover {
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

/* 모달 스타일 */
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
  max-width: 500px;
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

.original-inquiry {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.original-inquiry strong {
  color: #7e57c2;
}

.original-inquiry p {
  margin: 0.5rem 0 0 0;
  color: #333;
  line-height: 1.5;
}

.modal textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  background: #fafaff;
  resize: vertical;
  margin-bottom: 1.5rem;
}

.modal textarea:focus {
  border-color: #b39ddb;
  outline: none;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
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

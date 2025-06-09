<template>
  <div class="profile-page">
    <h2>
      <span class="emoji">🐾</span>
      <span class="username">{{ userInfo?.name || '회원' }}</span>님의 마이페이지
    </h2>

    <!-- 내 정보 섹션 -->
    <section class="info-section">
      <h3><span class="icon">📋</span> 내 정보</h3>
      <div class="info-list">
        <div class="info-item">
          <span class="label">이름</span>
          <span class="value">{{ userInfo?.name }}</span>
        </div>
        <div class="info-item">
          <span class="label">이메일</span>
          <span class="value">{{ userInfo?.email }}</span>
        </div>
        <div class="info-item">
          <span class="label">연락처</span>
          <span class="value">{{ userInfo?.phone || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">비밀번호 변경</span>
          <button class="change-btn" @click="onChangePassword">변경</button>
        </div>
      </div>
    </section>

    <!-- 반려동물 섹션 -->
    <section class="pet-section">
      <h3><span class="icon">🐶</span> 함께하는 아이들</h3>
      <div v-if="pets.length > 0" class="pets-simple-list">
        <div v-for="pet in pets" :key="pet.id" class="pet-simple-card">
          <div class="pet-avatar">
            <img v-if="pet.photo" :src="getPhotoUrl(pet.photo)" :alt="pet.name" />
            <div v-else class="avatar-placeholder">🐾</div>
          </div>
          <div class="pet-basic-info">
            <h4>{{ pet.name }}</h4>
            <p>{{ pet.breed || '품종 미상' }} · {{ pet.age ? `${pet.age}살` : '나이 미상' }} · {{ pet.gender }}</p>
          </div>
          <div class="pet-quick-actions">
            <button class="quick-btn" @click="viewHistory(pet)" title="진단이력">🩺</button>
            <button class="quick-btn" @click="openEditModal(pet)" title="수정">✏️</button>
            <button class="quick-btn danger" @click="confirmDelete(pet)" title="삭제">🗑️</button>
          </div>
        </div>
      </div>
      <button class="add-pet-btn" @click="openAddModal">+ 반려동물 등록하기</button>
    </section>

    <!-- 알림 설정 섹션 -->
    <section class="alert-section">
      <h3><span class="icon">🔔</span> 알림 설정</h3>
      <div class="alert-items">
        <div class="alert-item">
          <input type="checkbox" id="diagnosisAlert" v-model="alerts.diagnosis_alert" @change="updateAlerts" />
          <label for="diagnosisAlert">진단 알림 받기</label>
        </div>
        <div class="alert-item">
          <input type="checkbox" id="newsAlert" v-model="alerts.news_alert" @change="updateAlerts" />
          <label for="newsAlert">서비스 소식 받기</label>
        </div>
      </div>
    </section>

    <!-- 고객지원 섹션 -->
    <section class="support-section">
      <h3 class="support-title">고객지원</h3>
      <div class="support-buttons">
        <button class="support-btn" @click="viewInquiries">문의 내역 확인하기</button>
        <button class="support-btn" @click="viewNotices">공지사항 보기</button>
        <button class="support-btn" @click="showInquiryModal = true">새 문의하기</button>
        <button class="support-btn danger" @click="onDeleteAccount">계정 삭제하기</button>
      </div>
    </section>

    <!-- 반려동물 등록/수정 모달 -->
    <div v-if="showPetModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ isEditing ? '반려동물 정보 수정' : '새 반려동물 등록' }}</h3>
        <form @submit.prevent="submitPetForm">
          <div class="form-group">
            <label>이름 *</label>
            <input v-model="petForm.name" type="text" required placeholder="이름을 입력하세요" />
          </div>
          <div class="form-group">
            <label>품종</label>
            <input v-model="petForm.breed" type="text" placeholder="품종 (선택사항)" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>성별</label>
              <select v-model="petForm.gender" required>
                <option value="남">남</option>
                <option value="여">여</option>
              </select>
            </div>
            <div class="form-group">
              <label>나이</label>
              <input v-model.number="petForm.age" type="number" min="0" max="30" placeholder="나이" />
            </div>
          </div>
          <div class="form-group">
            <label>사진</label>
            <input type="file" accept="image/*" @change="handleFileUpload" />
            <div v-if="photoPreview" class="photo-preview">
              <img :src="photoPreview" alt="미리보기" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="submit" :disabled="isSubmitting" class="save-btn">
              {{ isSubmitting ? '처리 중...' : '저장' }}
            </button>
            <button type="button" @click="closeModal" class="cancel-btn">취소</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal delete-modal">
        <h3>{{ selectedPet?.name }} 삭제 확인</h3>
        <p>정말로 이 반려동물을 삭제하시겠습니까?<br>모든 진단 이력도 함께 삭제됩니다.</p>
        <div class="modal-actions">
          <button class="confirm-btn" @click="deletePet">삭제</button>
          <button class="cancel-btn" @click="cancelDelete">취소</button>
        </div>
      </div>
    </div>

    <!-- 문의 모달 -->
    <div v-if="showInquiryModal" class="modal-overlay" @click.self="showInquiryModal = false">
      <div class="modal">
        <h3>문의하기</h3>
        <form @submit.prevent="submitInquiry">
          <textarea v-model="inquiryContent" placeholder="문의 내용을 입력하세요" rows="5" required></textarea>
          <div class="modal-actions">
            <button type="submit">문의 등록</button>
            <button type="button" @click="showInquiryModal = false">취소</button>
          </div>
        </form>
      </div>
    </div>

    
    <div v-if="showPwModal" class="modal-overlay" @click.self="closePwModal">
      <div class="modal">
        <h3>비밀번호 변경</h3>
        <form @submit.prevent="submitChangePassword">
          <div class="form-group">
            <label>현재 비밀번호</label>
            <input v-model="pwForm.currentPassword" type="password" required autocomplete="current-password" />
          </div>
          <div class="form-group">
            <label>새 비밀번호</label>
            <input v-model="pwForm.newPassword" type="password" required autocomplete="new-password" />
          </div>
          <div class="form-group">
            <label>새 비밀번호 확인</label>
            <input v-model="pwForm.newPasswordConfirm" type="password" required autocomplete="new-password" />
          </div>
          <div class="modal-actions">
            <button type="submit" class="save-btn">변경</button>
            <button type="button" @click="closePwModal" class="cancel-btn">취소</button>
          </div>
          <p v-if="pwError" class="error-msg">{{ pwError }}</p>
          <p v-if="pwSuccess" class="success-msg">{{ pwSuccess }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { isLoggedIn, userInfo, logout } from '../store/auth'

const router = useRouter()

// 기존 상태 변수
const pets = ref([])
const showPetModal = ref(false)
const isEditing = ref(false)
const isSubmitting = ref(false)
const showDeleteModal = ref(false)
const selectedPet = ref(null)
const photoPreview = ref(null)
const editingPetId = ref(null)
const showInquiryModal = ref(false)
const inquiryContent = ref('')
const alerts = ref({
  diagnosis_alert: false,
  news_alert: false
})

const petForm = reactive({
  name: '',
  breed: '',
  gender: '남',
  age: null,
  photo: null
})

// 비밀번호 변경 상태 및 함수 (추가)
const showPwModal = ref(false)
const pwForm = reactive({
  currentPassword: '',
  newPassword: '',
  newPasswordConfirm: ''
})
const pwError = ref('')
const pwSuccess = ref('')

function onChangePassword() {
  showPwModal.value = true
  pwForm.currentPassword = ''
  pwForm.newPassword = ''
  pwForm.newPasswordConfirm = ''
  pwError.value = ''
  pwSuccess.value = ''
}

function closePwModal() {
  showPwModal.value = false
}

async function submitChangePassword() {
  pwError.value = ''
  pwSuccess.value = ''
  if (!pwForm.currentPassword || !pwForm.newPassword || !pwForm.newPasswordConfirm) {
    pwError.value = '모든 항목을 입력해주세요.'
    return
  }
  if (pwForm.newPassword !== pwForm.newPasswordConfirm) {
    pwError.value = '새 비밀번호가 일치하지 않습니다.'
    return
  }
  try {
    await axios.post('/api/change-password', {
      current_password: pwForm.currentPassword,
      new_password: pwForm.newPassword
    }, {
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    pwSuccess.value = '비밀번호가 성공적으로 변경되었습니다.'
    setTimeout(() => {
      closePwModal()
    }, 1500)
  } catch (error) {
    pwError.value = error.response?.data?.detail || '비밀번호 변경에 실패했습니다.'
  }
}

// 기존 함수들
onMounted(async () => {
  if (!isLoggedIn.value) router.replace('/login')
  await fetchPets()
  await fetchAlerts()
})

async function fetchPets() {
  try {
    const response = await axios.get('/api/pets', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    pets.value = response.data.data
  } catch (error) {
    console.error('반려동물 목록 조회 실패:', error)
    alert('반려동물 정보를 불러오는데 실패했습니다.')
  }
}

async function fetchAlerts() {
  try {
    const response = await axios.get('/api/alerts', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    alerts.value = response.data.data
  } catch (error) {
    console.error('알림 설정 조회 실패:', error)
  }
}

function openAddModal() {
  resetForm()
  showPetModal.value = true
}

function openEditModal(pet) {
  editingPetId.value = pet.id
  Object.assign(petForm, {
    name: pet.name,
    breed: pet.breed || '',
    gender: pet.gender,
    age: pet.age
  })
  photoPreview.value = pet.photo ? getPhotoUrl(pet.photo) : null
  isEditing.value = true
  showPetModal.value = true
}

async function submitPetForm() {
  if (!validatePetForm()) return
  isSubmitting.value = true
  try {
    const formData = new FormData()
    formData.append('name', petForm.name)
    formData.append('breed', petForm.breed)
    formData.append('gender', petForm.gender)
    formData.append('age', petForm.age)
    if (petForm.photo) formData.append('photo', petForm.photo)

    if (isEditing.value) {
      await axios.put(`/api/pets/${editingPetId.value}`, formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data'
        }
      })
    } else {
      await axios.post('/api/pets', formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data'
        }
      })
    }
    await fetchPets()
    closeModal()
    alert('처리가 완료되었습니다.')
  } catch (error) {
    handleApiError(error, '저장')
  } finally {
    isSubmitting.value = false
  }
}

async function deletePet() {
  try {
    await axios.delete(`/api/pets/${selectedPet.value.id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    await fetchPets()
    showDeleteModal.value = false
    alert('삭제가 완료되었습니다.')
  } catch (error) {
    handleApiError(error, '삭제')
  }
}

function getPhotoUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  // 슬래시가 없으면 앞에 / 붙이기
  return path.startsWith('/') ? `http://localhost:8000${path}` : `http://localhost:8000/${path}`
}

function validatePetForm() {
  if (!petForm.name.trim()) {
    alert('반려동물 이름을 입력해주세요.')
    return false
  }
  if (petForm.age < 0 || petForm.age > 30) {
    alert('나이는 0에서 30 사이로 입력해주세요.')
    return false
  }
  return true
}

function handleFileUpload(event) {
  const file = event.target.files[0]
  if (file) {
    petForm.photo = file
    const reader = new FileReader()
    reader.onload = (e) => {
      photoPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

function handleApiError(error, action) {
  console.error(`${action} 실패:`, error)
  alert(error.response?.data?.detail || `${action} 중 오류가 발생했습니다.`)
}

function resetForm() {
  Object.assign(petForm, {
    name: '',
    breed: '',
    gender: '남',
    age: null,
    photo: null
  })
  photoPreview.value = null
  isEditing.value = false
  editingPetId.value = null
}

function closeModal() {
  showPetModal.value = false
  resetForm()
}

function confirmDelete(pet) {
  selectedPet.value = pet
  showDeleteModal.value = true
}

function cancelDelete() {
  showDeleteModal.value = false
  selectedPet.value = null
}

function viewHistory(pet) {
  router.push(`/diagnosis-history/${pet.id}`)
}

async function updateAlerts() {
  try {
    await axios.put('/api/alerts', alerts.value, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
  } catch (error) {
    handleApiError(error, '알림 설정 업데이트')
  }
}
function viewInquiries() {
  router.push('/inquiries')
}

function viewNotices() {
  router.push('/notices')
}
async function submitInquiry() {
  try {
    await axios.post('/api/support/inquiry',
      { content: inquiryContent.value },
      { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
    )
    showInquiryModal.value = false
    inquiryContent.value = ''
    alert('문의가 등록되었습니다.')
  } catch {
    alert('문의 등록에 실패했습니다.')
  }
}
async function onDeleteAccount() {
  if (!confirm('정말로 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) return;
  try {
    await axios.delete('/api/delete-account', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    alert('계정이 삭제되었습니다.')
    logout()
    router.push('/')
  } catch (error) {
    alert(error.response?.data?.detail || '계정 삭제 중 오류가 발생했습니다.')
  }
}
</script>

<style scoped>
.profile-page {
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
  margin-bottom: 2.2rem;
  font-size: 1.7rem;
  font-weight: bold;
}
.emoji { font-size: 1.3em; vertical-align: middle; }
.username { color: #ffb74d; }

section {
  margin-bottom: 2.2rem;
}
section h3 {
  color: #ffb74d;
  font-size: 1.13rem;
  margin-bottom: 1.1rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.3em;
}
.icon { font-size: 1.1em; }

/* ====== 내 정보 ====== */
.info-list { margin-bottom: 0.5rem; }
.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.7rem;
  font-size: 1.09rem;
}
.label {
  color: #ffb74d;
  font-weight: bold;
  margin-right: 0.7rem;
}
.value { color: #222; }
.change-btn {
  background: #ffb74d;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.4rem 1.2rem;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.change-btn:hover { background: #ffa726; }

/* ====== 반려동물 리스트 ====== */
.pets-simple-list {
  margin-bottom: 1.5rem;
}
.pet-simple-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  margin-bottom: 0.8rem;
  border: 1px solid #eee;
  border-radius: 8px;
  transition: background 0.2s;
}
.pet-simple-card:hover {
  background: #f9fbe7;
}
.pet-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}
.pet-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}
.pet-basic-info {
  flex: 1;
}
.pet-basic-info h4 {
  margin: 0 0 0.3rem 0;
  color: #333;
  font-size: 1.1rem;
}
.pet-basic-info p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}
.pet-quick-actions {
  display: flex;
  gap: 0.3rem;
}
.quick-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: #f0f0f0;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.quick-btn:hover { background: #e0e0e0; }
.quick-btn.danger { background: #ffebee; }
.quick-btn.danger:hover { background: #ffcdd2; }

.add-pet-btn {
  display: block;
  width: 100%;
  padding: 0.8rem;
  background: #ffb74d;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1.05rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.add-pet-btn:hover { background: #ffa726; }

/* ====== 알림 설정 ====== */
.alert-items { margin-bottom: 0.5rem; }
.alert-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.8rem;
  font-size: 1.05rem;
}

/* ====== 고객지원 ====== */
.support-section { margin-bottom: 0; }
.support-title {
  color: #ffb74d;
  font-size: 1.1rem;
  margin-bottom: 1.1rem;
  font-weight: bold;
}
.support-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}
.support-btn {
  display: block;
  width: 100%;
  padding: 0.9rem 0;
  border: none;
  border-radius: 8px;
  font-size: 1.07rem;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s, color 0.2s;
  background: #f8f9fa;
  color: #444;
}
.support-btn:hover {
  background: #f3e5f5;
}
.support-btn.danger {
  background: #ffebee;
  color: #e53935;
}
.support-btn.danger:hover {
  background: #ffcdd2;
}

/* ====== 모달(공통) - 튀어나옴 방지 & 반응형 ====== */
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
  box-shadow: 0 8px 32px rgba(60,40,120,0.12);
  padding: 2.2rem 2rem 2rem 2rem;
  width: 95%;
  max-width: 400px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  animation: modalFadeIn 0.25s;
  box-sizing: border-box;
}
@media (max-width: 500px) {
  .modal {
    padding: 1.2rem 0.5rem 1.5rem 0.5rem;
    max-width: 98vw;
  }
}
@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(30px);}
  to { opacity: 1; transform: translateY(0);}
}
.modal h3 {
  margin-top: 0;
  margin-bottom: 1.6rem;
  color: #7e57c2;
  font-size: 1.25rem;
  font-weight: bold;
  text-align: center;
  letter-spacing: -1px;
}

/* ====== 폼 요소 튀어나옴 방지 ====== */
.modal input,
.modal select,
.modal textarea,
.modal button {
  width: 100%;
  box-sizing: border-box;
}
.form-group {
  margin-bottom: 1.4rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #7e57c2;
  font-weight: 500;
  font-size: 1.05rem;
}
.form-group input[type="text"],
.form-group input[type="password"],
.form-group input[type="number"],
.form-group input[type="file"],
.form-group select,
.form-group textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 0.7rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 7px;
  font-size: 1rem;
  background: #fafaff;
  transition: border 0.2s;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #b39ddb;
  outline: none;
}
.form-row {
  display: flex;
  gap: 1rem;
}
.photo-preview {
  margin-top: 0.8rem;
  text-align: center;
}
.photo-preview img {
  max-width: 120px;
  max-height: 120px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(60,40,120,0.10);
  background: #fafaff;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.3rem;
}
.save-btn, .confirm-btn {
  background: #7e57c2;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
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
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.cancel-btn:hover {
  background: #e0e0e0;
}
.error-msg {
  color: #e53935;
  margin-top: 0.7rem;
  font-size: 0.97rem;
  text-align: center;
}
.success-msg {
  color: #43a047;
  margin-top: 0.7rem;
  font-size: 0.97rem;
  text-align: center;
}
</style>

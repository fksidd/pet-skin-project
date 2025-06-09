<template>
  <div class="diagnosis-page">
    <h2>반려동물 피부 진단</h2>
    <div class="ai-section">
      <p class="ai-desc">AI가 사진만으로 피부질환을 분석해줍니다.</p>
      <div
        class="dropzone"
        :class="{ 'dropzone--dragover': isDragOver }"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
        @click="onClickFileInput"
        tabindex="0"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          @change="onFileSelected"
          style="display:none"
        />
        <div class="img-preview-fixed">
          <template v-if="imagePreview">
            <img :src="imagePreview" alt="미리보기" />
          </template>
          <template v-else>
            <div class="img-placeholder">이미지를 드래그하거나 클릭해서 업로드하세요</div>
          </template>
        </div>
      </div>
      <button
        class="diagnosis-btn"
        @click="uploadImage"
        :disabled="!selectedFile || loading"
      >
        {{ loading ? '진단 중...' : 'AI 진단 시작' }}
      </button>
    </div>
    <div v-if="result" class="diagnosis-result">
      <h3>예상 질환: {{ result.diagnosis || result.label }}</h3>
      <p>
        상태는
        <b>{{ getStatusMessage(result.diagnosis || result.label) }}</b>
        으로 판단됩니다.
      </p>
      <p>
        신뢰도:
        {{ (result.confidence ?? result.probability)
          ? ((result.confidence ?? result.probability) * 100).toFixed(2) + '%'
          : '정보 없음' }}
      </p>
      <!-- 저장 버튼 추가 -->
      <button @click="openSaveModal" class="save-btn">
        💾 진단 결과 저장
      </button>
    </div>

    <!-- 진단 결과 저장 모달 -->
    <div v-if="showSaveModal" class="modal-overlay" @click.self="showSaveModal = false">
      <div class="modal">
        <h3>어떤 반려동물의 진단 이력으로 저장할까요?</h3>
        <div class="pet-list">
          <div v-for="pet in pets" :key="pet.id" 
               class="pet-item" @click="selectPet(pet)">
            <img v-if="pet.photo" :src="getPhotoUrl(pet.photo)" class="pet-thumbnail">
            <div v-else class="pet-thumbnail placeholder">🐾</div>
            <span class="pet-name">{{ pet.name }}</span>
          </div>
          <div v-if="pets.length === 0" class="no-pets">
            <p>등록된 반려동물이 없습니다.</p>
            <button @click="goToProfile">+ 새 반려동물 등록</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { saveDiagnosis } from '../api/diagnosis'

const router = useRouter()
const selectedFile = ref(null)
const imagePreview = ref(null)
const result = ref(null)
const error = ref('')
const loading = ref(false)
const isDragOver = ref(false)
const fileInput = ref(null)

// 진단 결과 저장 플로우 관련 상태
const showSaveModal = ref(false)
const pets = ref([])

const statusMap = {
  '구진_플라크': '피부에 구진(작은 돌기)이나 플라크(넓은 융기)가 관찰됩니다. 만성 염증성 피부질환이나 알레르기, 감염 등 다양한 원인이 있을 수 있으니, 증상이 지속되면 수의사 상담이 필요합니다.',
  '비듬_각질_상피성잔고리': '피부에 각질, 비듬, 상피성 잔고리가 보입니다. 피부 건조, 초기 염증, 알레르기 등이 원인일 수 있으며, 정기적인 목욕과 보습 관리가 필요합니다.',
  '태선화_과다색소침착': '피부가 두꺼워지거나 색소가 짙어지는 태선화, 과다색소침착이 관찰됩니다. 만성 자극이나 긁음, 만성 피부질환의 신호일 수 있으니, 장기화 시 전문 진료를 권장합니다.',
  '농포_여드름': '피부에 농포(고름집)나 여드름이 나타납니다. 세균 감염, 피지선 문제 등이 원인일 수 있으며, 상태가 악화되면 수의사 진료가 필요합니다.',
  '미란_궤양': '피부에 미란(표면 벗겨짐) 또는 궤양(깊은 상처)이 있습니다. 2차 감염 위험이 높으므로 즉시 동물병원 진료가 필요합니다.',
  '결절_종괴': '피부에 결절(단단한 덩이)이나 종괴(혹)가 만져집니다. 양성 혹일 수도 있지만, 악성 가능성도 있으므로 빠른 진료를 권장합니다.',
  '무증상': '피부에 특별한 이상이 없으며 건강한 상태로 판단됩니다.'
}

function getStatusMessage(diagnosis) {
  return statusMap[diagnosis] || '상세 설명 정보를 찾을 수 없습니다.'
}

function onClickFileInput() {
  fileInput.value && fileInput.value.click()
}
function onFileSelected(event) {
  const file = event.target.files[0]
  if (file) {
    setFile(file)
  }
}
function onDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file) {
    setFile(file)
  }
  isDragOver.value = false
}
function onDragOver() {
  isDragOver.value = true
}
function onDragLeave() {
  isDragOver.value = false
}
function setFile(file) {
  selectedFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  result.value = null
  error.value = ''
}
async function uploadImage() {
  if (!selectedFile.value) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    const response = await axios.post('http://localhost:8000/predict', formData)
    result.value = response.data.data
  } catch (err) {
    error.value = '진단 요청 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

// 진단 결과 저장 플로우
function openSaveModal() {
  showSaveModal.value = true
  fetchPets()
}
async function fetchPets() {
  try {
    const response = await axios.get('/api/pets', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    pets.value = response.data.data
  } catch (error) {
    console.error('반려동물 조회 실패:', error)
    alert('반려동물 정보를 불러오는데 실패했습니다.')
  }
}
async function selectPet(pet) {
  try {
    await saveDiagnosis(
      pet.id,
      result.value.diagnosis,
      parseFloat(result.value.confidence),
      result.value.details || ''  // details 필드 추가!
    )
    alert(`${pet.name}의 진단 이력이 저장되었습니다!`)
    showSaveModal.value = false
    router.push(`/diagnosis-history/${pet.id}`)
  } catch (error) {
    alert(error.message || '진단 결과 저장에 실패했습니다.')
  }
}
function getPhotoUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  // 슬래시가 없으면 앞에 / 붙이기
  return path.startsWith('/') ? `http://localhost:8000${path}` : `http://localhost:8000/${path}`
}
function goToProfile() {
  showSaveModal.value = false
  router.push('/profile')
}
</script>

<style scoped>
.diagnosis-page {
  max-width: 460px;
  margin: 3rem auto;
  padding: 2rem 1.5rem;
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  background: #fff;
  text-align: center;
}
.diagnosis-page h2 {
  margin-bottom: 1.2rem;
  color: #7e57c2;
}
.ai-section {
  margin-bottom: 2rem;
}
.ai-desc {
  color: #555;
  margin-bottom: 1rem;
}
.dropzone {
  width: 320px;
  margin: 0 auto 1.2rem auto;
  cursor: pointer;
  outline: none;
}
.dropzone--dragover {
  border: 2px solid #7e57c2;
  background: #f3e5f5;
}
.img-preview-fixed {
  width: 320px;
  height: 200px;
  border: 2px dashed #bbb;
  border-radius: 10px;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}
.img-preview-fixed img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 10px;
}
.img-placeholder {
  color: #aaa;
  font-size: 1.1rem;
  user-select: none;
}
.diagnosis-btn {
  display: block;
  margin: 1.2rem auto 0 auto;
  background: #7e57c2;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.diagnosis-btn:disabled {
  background: #bbb;
  cursor: not-allowed;
}
.diagnosis-btn:hover:enabled {
  background: #5e35b1;
}
.diagnosis-result {
  background: #f9fbe7;
  border-radius: 12px;
  padding: 1.2rem;
  margin-top: 2rem;
  color: #333;
}
.error-msg {
  color: #d32f2f;
  margin-top: 1.5rem;
  font-weight: bold;
}

/* 저장 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
}
.pet-list {
  margin-top: 1.5rem;
}
.pet-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.pet-item:hover {
  background: #f9fbe7;
  transform: translateY(-2px);
}
.pet-thumbnail {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 1rem;
}
.pet-thumbnail.placeholder {
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}
.no-pets {
  text-align: center;
  padding: 1rem;
}
.save-btn {
  background: #7e57c2;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
  cursor: pointer;
}
</style>
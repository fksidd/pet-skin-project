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
    </div>
    <div v-if="error" class="error-msg">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const selectedFile = ref(null)
const imagePreview = ref(null)
const result = ref(null)
const error = ref('')
const loading = ref(false)
const isDragOver = ref(false)
const fileInput = ref(null)

const statusMap = {
  '무증상': '피부에 특별한 이상이 없으며 건강한 상태로 판단됩니다.',
  '비듬_각질': '피부에 각질과 비듬이 관찰되며, 가벼운 피부 건조 또는 초기 염증이 의심됩니다. 정기적인 목욕과 보습 관리가 필요합니다.',
  '농포_여드름': '피부에 농포(고름집)나 여드름이 관찰되며, 세균 감염 또는 피지선 문제 가능성이 있습니다. 악화 시 수의사 상담이 필요합니다.',
  '결절_종괴': '피부에 결절이나 종괴(혹)가 만져집니다. 양성 종양일 수도 있으나, 악성 가능성도 있으므로 동물병원 진료를 권장합니다.',
  '감염성피부염': '세균, 곰팡이 등 감염에 의한 피부염이 의심됩니다. 가려움, 발적, 진물, 악취 등이 동반될 수 있으며, 치료가 필요합니다.',
  '비감염성피부염': '알레르기, 아토피, 면역 이상 등 비감염성 원인에 의한 피부염이 의심됩니다. 만성화될 수 있으니 관리와 전문 치료가 필요합니다.'
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
    result.value = response.data
  } catch (err) {
    error.value = '진단 요청 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
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
</style>
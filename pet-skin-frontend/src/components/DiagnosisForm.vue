<template>
  <div>
    <h2>피부질환 이미지 진단</h2>
    <input type="file" accept="image/*" @change="onFileChange" />
    <img v-if="preview" :src="preview" alt="미리보기" width="200" />
    <button @click="onSubmit" :disabled="!selectedFile || loading">
      {{ loading ? '진단 중...' : '진단하기' }}
    </button>
    <div v-if="result">
      <h3>진단 결과</h3>
      <p>라벨: {{ result.diagnosis }}</p>
      <p>확률: {{ (result.confidence * 100).toFixed(2) }}%</p>
    </div>
    <div v-if="error" style="color: red;">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { diagnoseSkinDisease } from '../api/diagnosis'

const selectedFile = ref(null)
const preview = ref(null)
const result = ref(null)
const error = ref('')
const loading = ref(false)

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    preview.value = URL.createObjectURL(file)
    result.value = null
    error.value = ''
  }
}

async function onSubmit() {
  if (!selectedFile.value) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = await diagnoseSkinDisease(selectedFile.value)
  } catch (err) {
    error.value = '진단 요청 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}
</script>
<template>
  <div class="main-page">
    <h1>반려동물 피부 질환, AI로 빠르게 진단하세요!</h1>
    <p>사진 한 장으로 가능한 스마트한 피부 분석</p>
    <button class="main-btn" @click="onDiagnoseClick">진단 시작하기</button>
    <section>
      <h2>🐶 사용 방법</h2>
      <ol>
        <li><b>사진 업로드</b><br>반려동물의 피부 사진을 업로드하세요</li>
        <li><b>AI 진단</b><br>이미지를 업로드하면 AI가 질환을 분석해줘요</li>
        <li><b>진단 결과 확인</b><br>기록을 저장하고 이전 이력을 확인할 수 있어요</li>
      </ol>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { isUserLoggedIn } from '../store/auth'
const router = useRouter()

function onDiagnoseClick() {
  if (!isUserLoggedIn()) {
    router.push('/login')
  } else {
    router.push('/diagnosis')
  }
}
</script>
  <style scoped>
  .main-page {
    max-width: 500px;
    margin: 3rem auto;
    text-align: center;
    background: #fff;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    padding: 2.5rem 2rem;
  }
  .main-page h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: #2d3a4b;
  }
  .main-page p {
    color: #666;
    margin-bottom: 2rem;
  }
  .main-btn {
    background: #ffb74d;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.9rem 2.2rem;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    margin-bottom: 2rem;
    transition: background 0.2s;
  }
  .main-btn:hover {
    background: #ffa726;
  }
  section {
    background: #f9fbe7;
    border-radius: 12px;
    padding: 1.2rem;
    margin-top: 2rem;
  }
  section h2 {
    color: #7e57c2;
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }
  section ol {
    text-align: left;
    margin: 0 auto;
    padding-left: 1.2rem;
  }
  section li {
    margin-bottom: 1.2rem;
    font-size: 1rem;
  }
  </style>
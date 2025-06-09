<template>
  <div class="hospital-map-wrapper">
    <div class="hospital-map-card">
      <!-- 지도 영역 -->
      <div id="kakao-map" class="hospital-map"></div>
      
      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>청주시 동물병원을 검색하는 중...</p>
      </div>

      <!-- 병원 목록 -->
      <div v-if="hospitals.length > 0" class="hospital-list">
        <h3>청주시 동물병원 {{ hospitals.length }}곳</h3>
        <div 
          v-for="hospital in hospitals" 
          :key="hospital.id"
          class="hospital-item"
          @click="focusHospital(hospital)"
        >
          <div class="hospital-info">
            <h4>{{ hospital.place_name }}</h4>
            <p class="address">📍 {{ hospital.address_name }}</p>
            <p v-if="hospital.phone" class="phone">📞 {{ hospital.phone }}</p>
            <span v-if="hospital.is_24hour" class="emergency">24시간</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isLoading = ref(true)
const hospitals = ref([])
const map = ref(null)
const markers = ref([])

// 인포윈도우 상태 관리용
const currentInfoWindow = ref(null)
const currentMarker = ref(null)

// 청주시청 고정 좌표
const CHEONGJU_COORDS = {
  lat: 36.642434,
  lng: 127.489031
}

// 카카오맵 SDK 로드
async function loadKakaoSDK() {
  return new Promise((resolve, reject) => {
    if (window.kakao?.maps) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${process.env.VUE_APP_KAKAO_JS_KEY}&autoload=false&libraries=services`
    script.onload = () => {
      if (!window.kakao?.maps) {
        reject(new Error('카카오맵 SDK 초기화 실패'))
        return
      }
      window.kakao.maps.load(resolve)
    }
    script.onerror = () => reject(new Error('스크립트 로드 실패'))
    document.head.appendChild(script)
  })
}

// 지도 초기화 및 동물병원 검색
async function initializeMapAndSearch() {
  try {
    const container = document.getElementById('kakao-map')
    const options = {
      center: new window.kakao.maps.LatLng(CHEONGJU_COORDS.lat, CHEONGJU_COORDS.lng),
      level: 8
    }
    map.value = new window.kakao.maps.Map(container, options)
    await searchAnimalHospitals()
  } catch (error) {
    console.error('지도 초기화 실패:', error)
    alert('지도 초기화에 실패했습니다')
  }
}

// 동물병원 검색
async function searchAnimalHospitals() {
  const ps = new window.kakao.maps.services.Places()
  const keywords = [
    '청주 동물병원',
    '청주 동물의료센터',
    '청주 펫클리닉',
    '청주 24시 동물병원',
    '서원구 동물병원',
    '흥덕구 동물병원',
    '상당구 동물병원',
    '청원구 동물병원'
  ]
  let allResults = []
  for (const keyword of keywords) {
    await new Promise((resolve) => {
      ps.keywordSearch(keyword, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          const cheongjuResults = result.filter(hospital => 
            hospital.address_name.includes('청주시') ||
            hospital.address_name.includes('청주')
          )
          allResults = [...allResults, ...cheongjuResults]
        }
        resolve()
      })
    })
  }
  const uniqueResults = Array.from(
    new Set(allResults.map(h => h.place_name + h.address_name))
  ).map(unique => allResults.find(h => h.place_name + h.address_name === unique))
  hospitals.value = uniqueResults.slice(0, 50)
  displayMarkersOnMap(hospitals.value)
  isLoading.value = false
}

// 지도에 마커 표시 (토글 동작 구현)
function displayMarkersOnMap(hospitalsArr) {
  // 기존 마커 및 인포윈도우 제거
  markers.value.forEach(marker => marker.setMap(null))
  markers.value = []
  currentInfoWindow.value = null
  currentMarker.value = null

  hospitalsArr.forEach(hospital => {
    const lat = hospital.y
    const lng = hospital.x
    if (lat && lng) {
      const position = new window.kakao.maps.LatLng(lat, lng)
      const marker = new window.kakao.maps.Marker({
        position: position,
        clickable: true // 필수!
      })
      marker.setMap(map.value)

      // 인포윈도우 생성 (마커마다 새로 생성)
      const infoWindow = new window.kakao.maps.InfoWindow({
        content: `
          <div style="padding:8px;width:200px;font-size:12px;">
            <strong>${hospital.place_name}</strong><br>
            📍 ${hospital.address_name}<br>
            ${hospital.phone ? `📞 ${hospital.phone}` : ''}
          </div>
        `,
        removable: true // x버튼으로 닫을 수 있음
      })

      // 마커 클릭 이벤트 등록
      window.kakao.maps.event.addListener(marker, 'click', () => {
        // 같은 마커를 클릭한 경우 토글
        if (currentMarker.value === marker && currentInfoWindow.value) {
          currentInfoWindow.value.close()
          currentInfoWindow.value = null
          currentMarker.value = null
          return
        }
        // 다른 마커 클릭 시 기존 인포윈도우 닫고 새로 열기
        if (currentInfoWindow.value) {
          currentInfoWindow.value.close()
        }
        infoWindow.open(map.value, marker)
        currentInfoWindow.value = infoWindow
        currentMarker.value = marker
      })

      markers.value.push(marker)
    }
  })
}

// 병원 포커스
function focusHospital(hospital) {
  if (map.value && hospital.y && hospital.x) {
    const position = new window.kakao.maps.LatLng(hospital.y, hospital.x)
    map.value.setCenter(position)
    map.value.setLevel(3)
  }
}

// 메인 초기화
onMounted(async () => {
  try {
    await loadKakaoSDK()
    await initializeMapAndSearch()
  } catch (error) {
    console.error('카카오맵 SDK 로드 실패:', error)
    isLoading.value = false
    alert('카카오맵을 로드할 수 없습니다')
  }
})
</script>

<style scoped>
.page-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
}
.hospital-map-wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem 0;
  min-height: 100vh;
}

.hospital-map-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  padding: 1.5rem;
  max-width: 800px;
  width: 100%;
}

.hospital-map {
  width: 100%;
  height: 500px;
  border-radius: 12px;
  margin-bottom: 1rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  border-radius: 12px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.current-info {
  background: #e3f2fd;
  padding: 0.8rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 500;
  color: #1976d2;
  text-align: center;
}

.location-icon {
  margin-right: 0.5rem;
}

.hospital-list {
  margin-top: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.hospital-list h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.hospital-item {
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.hospital-item:hover {
  background: #f8f9fa;
  border-color: #007bff;
  transform: translateX(3px);
}

.hospital-info h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.hospital-info .address,
.hospital-info .phone {
  margin: 0.3rem 0;
  color: #666;
  font-size: 0.95rem;
}

.meta {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  margin-top: 0.5rem;
}

.emergency {
  background: #dc3545;
  color: white;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 500;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

@media (max-width: 768px) {
  .hospital-map-card {
    margin: 1rem;
    padding: 1rem;
  }
  
  .hospital-map {
    height: 400px;
  }
}
</style>
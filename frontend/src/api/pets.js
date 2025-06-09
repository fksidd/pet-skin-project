// src/api/pets.js
import axios from 'axios'

const BASE_URL = 'http://localhost:8000'

// 인증 헤더 생성 함수
function getAuthHeaders() {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// 반려동물 목록 조회
export async function fetchPets() {
  try {
    const response = await axios.get(`${BASE_URL}/api/pets`, {
      headers: getAuthHeaders()
    })
    return response.data.data // APIResponse의 data 필드만 반환
  } catch (error) {
    console.error('반려동물 목록 조회 실패:', error)
    throw error
  }
}

// 반려동물 등록
export async function createPet(petData) {
  try {
    const formData = new FormData()
    formData.append('name', petData.name)
    formData.append('gender', petData.gender || '남')
    if (petData.breed) formData.append('breed', petData.breed)
    if (petData.age !== undefined && petData.age !== null) formData.append('age', petData.age)
    if (petData.photo) formData.append('photo', petData.photo)

    const response = await axios.post(`${BASE_URL}/api/pets`, formData, {
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data.data
  } catch (error) {
    console.error('반려동물 등록 실패:', error)
    throw error
  }
}

// 반려동물 정보 조회
export async function fetchPet(petId) {
  try {
    const response = await axios.get(`${BASE_URL}/api/pets/${petId}`, {
      headers: getAuthHeaders()
    })
    return response.data.data
  } catch (error) {
    console.error('반려동물 정보 조회 실패:', error)
    throw error
  }
}

// 반려동물 정보 수정
export async function updatePet(petId, petData) {
  try {
    const formData = new FormData()
    if (petData.name) formData.append('name', petData.name)
    if (petData.breed !== undefined) formData.append('breed', petData.breed)
    if (petData.gender) formData.append('gender', petData.gender)
    if (petData.age !== undefined && petData.age !== null) formData.append('age', petData.age)
    if (petData.photo) formData.append('photo', petData.photo)

    const response = await axios.put(`${BASE_URL}/api/pets/${petId}`, formData, {
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data.data
  } catch (error) {
    console.error('반려동물 정보 수정 실패:', error)
    throw error
  }
}

// 반려동물 삭제
export async function deletePet(petId) {
  try {
    const response = await axios.delete(`${BASE_URL}/api/pets/${petId}`, {
      headers: getAuthHeaders()
    })
    return response.data.data
  } catch (error) {
    console.error('반려동물 삭제 실패:', error)
    throw error
  }
}

// 반려동물 통계 조회
export async function fetchPetStats(petId) {
  try {
    const response = await axios.get(`${BASE_URL}/api/pets/${petId}/stats`, {
      headers: getAuthHeaders()
    })
    return response.data.data
  } catch (error) {
    console.error('반려동물 통계 조회 실패:', error)
    throw error
  }
}
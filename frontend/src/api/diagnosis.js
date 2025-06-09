// src/api/diagnosis.js
import axios from 'axios'
import { getAuthHeaders } from '../store/auth'

const BASE_URL = 'http://localhost:8000'

/**
 * 피부질환 진단 API 호출 함수
 * @param {File} file - 업로드할 이미지 파일
 * @returns {Promise<Object>} - { filename, diagnosis, confidence }
 */
export async function diagnoseSkinDisease(file) {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await axios.post(`${BASE_URL}/predict`, formData, {
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data.data
  } catch (error) {
    throw new Error('진단 요청 실패: ' + error.response?.data?.detail || error.message)
  }
}

/**
 * 진단 이력 저장
 * @param {number} petId - 반려동물 ID
 * @param {string} diagnosis - 진단 결과
 * @param {number} confidence - 신뢰도
 */
export async function saveDiagnosis(petId, diagnosis, confidence, details = "") {
  try {
    const response = await axios.post(
      `${BASE_URL}/api/diagnosis/save`,
      { pet_id: petId, diagnosis, confidence, details },  
      { headers: getAuthHeaders() }
    )
    return response.data.data
  } catch (error) {
    throw new Error('저장 실패: ' + (error.response?.data?.detail || error.message))
  }
}

/**
 * 진단 이력 조회
 * @param {number} petId - 반려동물 ID
 */
export async function getDiagnosisHistory(petId) {
  try {
    const response = await axios.get(`${BASE_URL}/api/diagnosis/history/${petId}`, {
      headers: getAuthHeaders()
    })
    return response.data.data
  } catch (error) {
    throw new Error('조회 실패: ' + error.response?.data?.detail || error.message)
  }
}

/**
 * 진단 통계 조회
 * @param {number} petId - 반려동물 ID
 */
export async function getDiagnosisStats(petId) {
  try {
    const response = await axios.get(`${BASE_URL}/api/diagnosis/stats/${petId}`, {
      headers: getAuthHeaders()
    })
    return response.data.data
  } catch (error) {
    throw new Error('통계 조회 실패: ' + error.response?.data?.detail || error.message)
  }
}

/**
 * 진단 상세 정보 조회
 * @param {number} diagnosisId - 진단 기록 ID
 */
export async function getDiagnosisDetail(diagnosisId) {
  try {
    const response = await axios.get(`${BASE_URL}/api/diagnosis/detail/${diagnosisId}`, {
      headers: getAuthHeaders()
    })
    return response.data.data
  } catch (error) {
    throw new Error('상세 조회 실패: ' + error.response?.data?.detail || error.message)
  }
}

/**
 * 진단 기록 삭제
 * @param {number} diagnosisId - 진단 기록 ID
 */
export async function deleteDiagnosis(diagnosisId) {
  try {
    const response = await axios.delete(`${BASE_URL}/api/diagnosis/${diagnosisId}`, {
      headers: getAuthHeaders()
    })
    return response.data.data
  } catch (error) {
    throw new Error('삭제 실패: ' + error.response?.data?.detail || error.message)
  }
}

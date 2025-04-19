import axios from 'axios'

// FastAPI 백엔드 서버 주소
const BASE_URL = 'http://localhost:8000'

/**
 * 피부질환 진단 API 호출 함수
 * @param {File} file - 업로드할 이미지 파일
 * @returns {Promise<Object>} - { filename, diagnosis, confidence }
 */
export async function diagnoseSkinDisease(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post(`${BASE_URL}/predict`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}
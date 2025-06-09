import axios from 'axios'

export async function fetchHospitals(lat, lng, radius = 3000) {
  try {
    const response = await axios.get('/api/hospitals/nearby', {
      params: { lat, lng, radius }
    })
    return response.data.data
  } catch (error) {
    console.error('병원 데이터 조회 실패:', error)
    throw error
  }
}

import axios from 'axios'

const BASE_URL = 'http://localhost:8000'

export async function loginUser(email, password) {
  const params = new URLSearchParams()
  params.append('username', email)
  params.append('password', password)
  const res = await axios.post(`${BASE_URL}/api/token`, params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
  return res.data
}

export async function registerUser({ name, email, phone, password }) {
  const res = await axios.post(`${BASE_URL}/api/register/`, { name, email, phone, password })
  return res.data
}

export async function fetchUserInfo(token) {
  const res = await axios.get(`${BASE_URL}/api/me`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  return res.data
}
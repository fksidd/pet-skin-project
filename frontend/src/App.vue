<script setup>
import { isLoggedIn, logout } from './store/auth'
import { useRouter } from 'vue-router'
const router = useRouter()
function handleLogout() {
  if (window.confirm('로그아웃 하시겠습니까?')) {
    logout()
    router.push('/')
  }
}
</script>

<template>
  <header>
    <nav>
      <router-link to="/">메인</router-link>
      <template v-if="!isLoggedIn">
        <router-link to="/login">로그인</router-link>
        <router-link to="/register">회원가입</router-link>
      </template>
      <template v-else>
        <router-link to="/hospitals">병원 찾기</router-link>
        <button @click="handleLogout">로그아웃</button>
        <router-link to="/profile">회원정보</router-link>
      </template>
    </nav>
  </header>
  <router-view />
</template>

<style>
header {
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 1rem 0;
}
nav {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  align-items: center;
}
nav a, nav button {
  font-size: 1.1rem;
  color: #7e57c2;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.3rem 1rem;
  border-radius: 6px;
  transition: background 0.2s;
}
nav a.router-link-exact-active {
  background: #f3e5f5;
}
nav button:hover, nav a:hover {
  background: #ede7f6;
}
</style>
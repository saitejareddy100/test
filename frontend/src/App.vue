<template>
  <div class="app">
    <header>
      <h1>🤖 Smart Contract Analyzer Pro</h1>
      <nav>
        <button @click="currentView = 'analyzer'" :class="{ active: currentView === 'analyzer' }">Analyzer</button>
        <button @click="currentView = 'history'" :class="{ active: currentView === 'history' }">History</button>
        <button @click="loginVisible = true" v-if="!token">Login</button>
        <button @click="logout" v-else>Logout</button>
      </nav>
    </header>

    <Analyzer v-if="currentView === 'analyzer'" @result="onAnalysisResult" />
    <History v-else @login="loginVisible = true" :token="token" />

    <LoginModal v-if="loginVisible" @close="loginVisible = false" @login="onLogin" />

    <div v-if="currentResult" class="result-overlay">
      <div class="result-card">
        <h3>Analysis Complete!</h3>
        <p>Risk Level: <span :class="['risk-badge', currentResult.risk_level.toLowerCase()]">{{ currentResult.risk_level }}</span></p>
<p>Score: {{ currentResult.risk_score }}/20</p>
        <pre>{{ currentResult.summary }}</pre>
        <button @click="currentResult = null">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Analyzer from './components/Analyzer.vue'
import History from './components/History.vue'
import LoginModal from './components/LoginModal.vue'

const currentView = ref('analyzer')
const loginVisible = ref(false)
const token = ref(localStorage.getItem('token'))
const currentResult = ref(null)

const onLogin = (newToken) => {
  token.value = newToken
  localStorage.setItem('token', newToken)
  loginVisible.value = false
}

const logout = () => {
  token.value = null
  localStorage.removeItem('token')
}

const onAnalysisResult = (result) => {
  currentResult.value = result
}
</script>

<style>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

nav button {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 10px 20px;
  margin: 0 5px;
  border-radius: 5px;
  cursor: pointer;
}

nav button.active, nav button:hover {
  background: #3730a3;
}

.result-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.result-card {
  background: white;
  padding: 30px;
  border-radius: 10px;
  max-width: 600px;
  max-height: 80vh;
  overflow: auto;
}

.risk-badge {
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: bold;
}

.risk-badge.low-risk {
  background: #10b981;
  color: white;
}

.risk-badge.medium-risk {
  background: #f59e0b;
  color: white;
}

.risk-badge.high-risk {
  background: #ef4444;
  color: white;
}
</style>

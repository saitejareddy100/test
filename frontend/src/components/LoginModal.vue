<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>🔑 Login with API Key</h3>
      <input v-model="apiKey" placeholder="Enter API key" type="password" />
      <button @click="login">Login</button>
      <button @click="$emit('close')">Cancel</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['close', 'login'])
const apiKey = ref('')

const login = async () => {
  try {
    const res = await axios.post('/api/login', {
      api_key: apiKey.value
    })
    emit('login', res.data.access_token)
  } catch (e) {
    if (e.response?.status === 401) {
      alert('Invalid API key. Register first.')
    } else {
      alert('Backend error')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal {
  background: white;
  padding: 30px;
  border-radius: 10px;
  min-width: 300px;
}
input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 5px;
}
button {
  padding: 10px 20px;
  margin: 5px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:first-of-type {
  background: #4f46e5;
  color: white;
}
</style>

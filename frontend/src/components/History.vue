<template>
  <div class="history">
    <h2>📋 Analysis History</h2>
    <p v-if="!token" class="no-token">Login to see history</p>
    <ul v-else class="history-list">
      <li v-for="analysis in history" :key="analysis.id">
        {{ analysis.filename }} - {{ analysis.risk_level }} ({{ analysis.created_at }})
      </li>
    </ul>
    <button @click="$emit('login')" v-if="!token">Login</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  token: String
})

const emit = defineEmits(['login'])
const history = ref([])

onMounted(async () => {
  if (props.token) {
    try {
      const res = await axios.get('/api/history/1', {
        headers: { Authorization: `Bearer ${props.token}` }
      })
      history.value = res.data
    } catch (e) {
      console.log('History fetch failed')
    }
  }
})
</script>

<style scoped>
.history {
  padding: 20px;
}
.history-list {
  list-style: none;
}
li {
  padding: 10px;
  border-bottom: 1px solid #eee;
}
.no-token {
  color: #666;
  font-style: italic;
}
</style>

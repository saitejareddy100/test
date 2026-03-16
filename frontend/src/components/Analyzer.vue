<template>
  <div class="analyzer">
    <div class="upload-area" @drop="onDrop" @dragover.prevent @dragenter.prevent @dragleave="onDragLeave">
      <input type="file" @change="onFileSelect" accept=".pdf,.docx,.txt" ref="fileInput" style="display: none">
      <button @click="$refs.fileInput.click()">📁 Upload Contract</button>
      <p>Drag & drop PDF/DOCX/TXT or click to browse</p>
      <div v-if="loading" class="loading">Analyzing...</div>
    </div>

    <div v-if="result" class="results-preview">
      <h3>Quick Preview</h3>
      <chart-component :data="result" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import ChartComponent from './ChartComponent.vue'

const emit = defineEmits(['result'])

const fileInput = ref()
const loading = ref(false)
const result = ref(null)

const onFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) uploadFile(file)
}

const onDrop = (e) => {
  e.preventDefault()
  const file = e.dataTransfer.files[0]
  if (file) uploadFile(file)
}

const onDragLeave = (e) => {
  e.currentTarget.classList.remove('drag-over')
}

const uploadFile = async (file) => {
  loading.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await axios.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = response.data
    emit('result', response.data)
  } catch (error) {
    console.error('Upload error:', error)
    alert('Analysis failed. Backend may need API key or check console.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.analyzer {
  text-align: center;
  padding: 40px;
}

.upload-area {
  border: 3px dashed #ccc;
  border-radius: 10px;
  padding: 60px;
  margin: 0 auto;
  max-width: 500px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover, .upload-area.drag-over {
  border-color: #4f46e5;
  background: #f8f9ff;
}

button {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 15px 30px;
  font-size: 18px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 20px;
}

.loading {
  color: #4f46e5;
  font-size: 18px;
  margin-top: 20px;
}

.results-preview {
  margin-top: 40px;
  background: white;
  padding: 30px;
  border-radius: 10px;
}
</style>

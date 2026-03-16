<template>
  <canvas ref="chartCanvas" class="chart"></canvas>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  data: Object
})

const chartCanvas = ref(null)
let chart = null

onMounted(() => initChart())

watch(() => props.data, () => updateChart())

const initChart = () => {
  const ctx = chartCanvas.value.getContext('2d')
  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Risk', 'Safe'],
      datasets: [{
        data: [50, 50],
        backgroundColor: ['#ef4444', '#10b981']
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  })
}

const updateChart = () => {
  if (!props.data || !chart) return
  const score = props.data.risk_score || 0
  chart.data.datasets[0].data = [score, 10 - score]
  chart.update()
}
</script>

<style scoped>
.chart {
  max-height: 300px;
}
</style>

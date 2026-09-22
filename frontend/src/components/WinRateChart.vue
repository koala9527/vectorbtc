<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const props = defineProps<{
  data: any[];
}>();

const chartRef = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

const initChart = () => {
  if (!chartRef.value) return;
  chart = echarts.init(chartRef.value, 'dark');
  updateChart();
};

const updateChart = () => {
  if (!chart || !props.data || !props.data.length) return;
  
  // Sort ascending by win_rate so highest is at the top in horizontal bar
  const sorted = [...props.data].sort((a, b) => (a.win_rate || 0) - (b.win_rate || 0));
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0];
        const raw = sorted[item.dataIndex];
        return `${item.name}<br/>胜率: <b>${item.value}%</b><br/>总预测: ${raw.total_predictions || 0}<br/>正确: ${raw.correct_predictions || 0} / 错误: ${raw.wrong_predictions || 0}`;
      }
    },
    grid: {
      left: '4%',
      right: '12%',
      top: '5%',
      bottom: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%', color: '#8f9ca2' },
      splitLine: { lineStyle: { color: '#2a2a3e' } }
    },
    yAxis: {
      type: 'category',
      data: sorted.map(d => d.name || d.model_name || `模型 #${d.model_id}`),
      axisLabel: { color: '#e0e0e0' }
    },
    series: [
      {
        name: '胜率',
        type: 'bar',
        barWidth: 18,
        data: sorted.map(d => ({
          value: Number((d.win_rate || 0).toFixed(1)),
          itemStyle: {
            color: (d.win_rate || 0) >= 50 ? '#00c853' : '#ff1744',
            borderRadius: [0, 4, 4, 0]
          }
        })),
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          color: '#e0e0e0',
          fontWeight: 'bold'
        }
      }
    ]
  };
  
  chart.setOption(option);
};

const handleResize = () => {
  chart?.resize();
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  chart?.dispose();
  chart = null;
});

watch(() => props.data, updateChart, { deep: true });
</script>

<template>
  <div class="win-rate-chart" ref="chartRef"></div>
</template>

<style scoped>
.win-rate-chart {
  width: 100%;
  height: 280px;
}
</style>

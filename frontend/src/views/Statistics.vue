<script setup lang="ts">
import { ref, onMounted } from 'vue';
import WinRateChart from '../components/WinRateChart.vue';
import { statsApi } from '../api';

const overview = ref<any>({});
const modelStats = ref<any[]>([]);
const historyData = ref<any[]>([]);

onMounted(async () => {
  try {
    const [oRes, mRes, hRes]: any = await Promise.all([
      statsApi.getOverview(),
      statsApi.getByModel(),
      statsApi.getHistory(7),
    ]);
    overview.value = oRes;
    modelStats.value = mRes;
    historyData.value = hRes;
  } catch (e) {
    console.error(e);
  }
});
</script>

<template>
  <div class="statistics-page">
    <div class="overview">
      <van-grid :column-num="2" :border="false" class="custom-grid">
        <van-grid-item>
          <div class="stat-value">{{ overview.total_predictions || 0 }}</div>
          <div class="stat-label">总预测数</div>
        </van-grid-item>
        <van-grid-item>
          <div class="stat-value win-rate">{{ overview.win_rate || 0 }}%</div>
          <div class="stat-label">总胜率</div>
        </van-grid-item>
        <van-grid-item>
          <div class="stat-value correct">{{ overview.correct_predictions || 0 }}</div>
          <div class="stat-label">正确</div>
        </van-grid-item>
        <van-grid-item>
          <div class="stat-value wrong">{{ overview.wrong_predictions || 0 }}</div>
          <div class="stat-label">错误</div>
        </van-grid-item>
      </van-grid>
      <div class="skip-info">
        <van-icon name="info-o" size="12" />
        <span>跳过: {{ overview.skip_predictions || 0 }} 次（不计入胜率）</span>
      </div>
    </div>

    <div class="chart-section" v-if="modelStats.length">
      <h3 class="section-title">模型胜率对比</h3>
      <WinRateChart :data="modelStats" />
    </div>
    
    <div class="history-section" v-if="historyData.length">
      <h3 class="section-title">每日胜率趋势</h3>
      <div class="history-list">
        <van-cell v-for="h in historyData" :key="h.date" class="history-cell">
          <template #title>
            <span class="date">{{ h.date }}</span>
          </template>
          <template #label>
            <span>{{ h.correct }}/{{ h.total }} 预测正确</span>
          </template>
          <template #value>
            <span :class="h.win_rate >= 50 ? 'rate-good' : 'rate-bad'">{{ h.win_rate }}%</span>
          </template>
        </van-cell>
      </div>
    </div>
    
    <van-empty v-if="!modelStats.length && !historyData.length" description="暂无统计数据" image="search" />
  </div>
</template>

<style scoped>
.statistics-page {
  padding: 10px;
  min-height: 100vh;
  background: #0f0f1a;
}
.custom-grid {
  background: #1e2a3a;
  border-radius: 12px;
  overflow: hidden;
  padding: 8px 0;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #e0e0e0;
}
.stat-value.win-rate { color: #00c853; }
.stat-value.correct { color: #00c853; }
.stat-value.wrong { color: #ff1744; }
.stat-label {
  font-size: 12px;
  color: #8f9ca2;
  margin-top: 4px;
}
.skip-info {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: center;
  padding: 8px;
  font-size: 12px;
  color: #8f9ca2;
}
.section-title {
  font-size: 16px;
  margin: 20px 0 10px;
  padding-left: 10px;
  border-left: 4px solid #00c853;
  color: #e0e0e0;
}
.chart-section {
  margin-top: 12px;
}
.history-cell {
  background: #1a1a2e !important;
  border-bottom: 1px solid #2a2a3e;
}
.date { color: #c0c0c0; font-weight: 500; }
.rate-good { color: #00c853; font-weight: bold; font-size: 16px; }
.rate-bad { color: #ff1744; font-weight: bold; font-size: 16px; }
:deep(.van-grid-item__content) {
  background: transparent;
}
:deep(.van-cell__label) {
  color: #8f9ca2;
}
:deep(.van-empty__description) {
  color: #8f9ca2;
}
</style>

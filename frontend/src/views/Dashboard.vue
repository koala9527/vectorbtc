<script setup lang="ts">
import { onMounted, ref, computed, onUnmounted } from 'vue';
import { showToast } from 'vant';
import MarketTicker from '../components/MarketTicker.vue';
import KlineChart from '../components/KlineChart.vue';
import IndicatorPanel from '../components/IndicatorPanel.vue';
import PredictionCard from '../components/PredictionCard.vue';
import { useMarketStore } from '../stores/market';
import { usePredictionStore } from '../stores/prediction';
import { predictionsApi } from '../api';

const marketStore = useMarketStore();
const predictionStore = usePredictionStore();

const activeCollapse = ref<string[]>(['1']);
const isTriggering = ref(false);

// Countdown to next 5-minute candle
const timeToNext = ref(0);
let countdownInterval: number | null = null;

const calcCountdown = () => {
  const now = Date.now();
  const fiveMin = 5 * 60 * 1000;
  const remainder = fiveMin - (now % fiveMin);
  timeToNext.value = remainder;
};

const refreshAll = () => {
  marketStore.fetchTicker();
  marketStore.fetchKlines();
  marketStore.fetchIndicators();
  predictionStore.fetchLatest();
};

const handleManualTrigger = async () => {
  isTriggering.value = true;
  try {
    await predictionsApi.trigger();
    showToast({ type: 'success', message: '已触发预测与结算！' });
    // Refresh data after a short delay for background task to execute
    setTimeout(() => {
      refreshAll();
      isTriggering.value = false;
    }, 4000);
  } catch (e) {
    showToast({ type: 'fail', message: '触发失败' });
    isTriggering.value = false;
  }
};

onMounted(() => {
  refreshAll();
  calcCountdown();
  countdownInterval = window.setInterval(calcCountdown, 1000);
});

onUnmounted(() => {
  if (countdownInterval) clearInterval(countdownInterval);
});

const countdownText = computed(() => {
  const totalSec = Math.floor(timeToNext.value / 1000);
  const min = Math.floor(totalSec / 60);
  const sec = totalSec % 60;
  return `${String(min).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
});
</script>

<template>
  <div class="dashboard">
    <MarketTicker />
    
    <van-collapse v-model="activeCollapse">
      <van-collapse-item title="K线图表 (5M)" name="1">
        <KlineChart />
      </van-collapse-item>
      <van-collapse-item title="技术指标 (MACD/RSI/布林带/均线)" name="2">
        <IndicatorPanel />
      </van-collapse-item>
    </van-collapse>

    <div class="control-bar">
      <div class="countdown-section">
        <van-icon name="clock-o" size="16" color="#8f9ca2" />
        <span class="countdown-label">下次结算/预测:</span>
        <span class="countdown-time">{{ countdownText }}</span>
      </div>
      <van-button
        type="primary"
        size="small"
        :loading="isTriggering"
        loading-text="计算中..."
        icon="replay"
        round
        @click="handleManualTrigger"
      >
        立即预测
      </van-button>
    </div>

    <div class="predictions-list" v-if="predictionStore.latestPredictions.length">
      <div class="section-header">
        <h3 class="section-title">最新预测 (本周期)</h3>
        <span class="refresh-btn" @click="refreshAll">刷新</span>
      </div>
      <PredictionCard
        v-for="pred in predictionStore.latestPredictions"
        :key="pred.id"
        :prediction="pred"
      />
    </div>
    <div v-else class="empty-box">
      <van-empty description="暂无预测数据，请在「设置」中添加AI模型后点击「立即预测」" image="search" />
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 10px;
  min-height: 100vh;
  background: #0f0f1a;
  padding-bottom: 70px;
}
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  margin: 8px 10px;
  background: #1e2a3a;
  border-radius: 8px;
  border: 1px solid #2a2a3e;
}
.countdown-section {
  display: flex;
  align-items: center;
  gap: 6px;
}
.countdown-label {
  font-size: 13px;
  color: #8f9ca2;
}
.countdown-time {
  color: #00c853;
  font-weight: bold;
  font-size: 16px;
  font-family: monospace;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 10px 8px;
}
.section-title {
  font-size: 15px;
  padding-left: 10px;
  border-left: 4px solid #00c853;
  color: #e0e0e0;
  margin: 0;
}
.refresh-btn {
  font-size: 12px;
  color: #00c853;
  cursor: pointer;
}
:deep(.van-collapse-item) {
  margin: 4px 10px;
  border-radius: 8px;
  overflow: hidden;
}
:deep(.van-collapse-item__title) {
  background: #1e2a3a;
  color: #e0e0e0;
}
:deep(.van-collapse-item__content) {
  background: #1a1a2e;
  padding: 0;
}
:deep(.van-collapse-item__wrapper) {
  background: #1a1a2e;
}
.empty-box {
  margin: 20px 10px;
  background: #1a1a2e;
  border-radius: 10px;
  padding: 20px 0;
}
:deep(.van-empty__description) {
  color: #8f9ca2;
  font-size: 13px;
  padding: 0 20px;
  text-align: center;
}
</style>

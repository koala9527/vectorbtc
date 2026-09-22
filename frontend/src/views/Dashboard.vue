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
import dayjs from 'dayjs';

const marketStore = useMarketStore();
const predictionStore = usePredictionStore();

const activeCollapse = ref<string[]>(['1']);
const isTriggering = ref(false);

// Countdown to next 5-minute candle
const timeToNext = ref(0);
const currentRoundStart = ref('');
const currentRoundEnd = ref('');
let countdownInterval: number | null = null;

const calcCountdown = () => {
  const now = Date.now();
  const fiveMin = 5 * 60 * 1000;
  const candleStartTime = Math.floor(now / fiveMin) * fiveMin;
  const candleEndTime = candleStartTime + fiveMin;
  
  timeToNext.value = candleEndTime - now;
  currentRoundStart.value = dayjs(candleStartTime).format('HH:mm');
  currentRoundEnd.value = dayjs(candleEndTime).format('HH:mm');
};

const refreshAll = () => {
  marketStore.fetchTicker();
  marketStore.fetchKlines();
  marketStore.fetchIndicators();
  predictionStore.fetchLatest();
};

const handleManualTrigger = async () => {
  isTriggering.value = true;
  showToast({ type: 'loading', message: '正在采集中并由各AI进行M5量化推演...', duration: 0, forbidClick: true });
  try {
    await predictionsApi.trigger();
    showToast({ type: 'success', message: '已触发 5M 预测与结算！' });
    setTimeout(() => {
      refreshAll();
      isTriggering.value = false;
    }, 4500);
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

const countdownProgress = computed(() => {
  const total = 5 * 60;
  const remaining = Math.floor(timeToNext.value / 1000);
  return Math.min(100, Math.max(0, Math.round(((total - remaining) / total) * 100)));
});
</script>

<template>
  <div class="dashboard">
    <MarketTicker />
    
    <!-- 5-Minute Cycle Status Card -->
    <div class="m5-cycle-card">
      <div class="cycle-main">
        <div class="cycle-left">
          <div class="cycle-badge">
            <span class="pulse-dot"></span>
            <span>5M 正在推演周期</span>
          </div>
          <div class="cycle-interval">{{ currentRoundStart }} ~ {{ currentRoundEnd }}</div>
        </div>

        <div class="cycle-right">
          <div class="countdown-wrap">
            <span class="cd-label">收盘结算倒计时</span>
            <span class="cd-time">{{ countdownText }}</span>
          </div>
          <van-button
            type="primary"
            size="small"
            :loading="isTriggering"
            loading-text="推演中..."
            icon="replay"
            round
            class="trigger-btn"
            @click="handleManualTrigger"
          >
            立即推演
          </van-button>
        </div>
      </div>
      <div class="cycle-progress-track">
        <div class="cycle-progress-bar" :style="{ width: countdownProgress + '%' }"></div>
      </div>
    </div>

    <!-- Collapsible Charts & Indicators -->
    <van-collapse v-model="activeCollapse" class="dashboard-collapse">
      <van-collapse-item name="1">
        <template #title>
          <div class="collapse-header">
            <span class="c-title">5M 实时 K 线图表</span>
            <span class="c-sub">蜡烛形态 · 成交量</span>
          </div>
        </template>
        <KlineChart />
      </van-collapse-item>

      <van-collapse-item name="2">
        <template #title>
          <div class="collapse-header">
            <span class="c-title">M5 技术指标量化矩阵</span>
            <span class="c-sub">MACD / RSI / 布林带 / 均线</span>
          </div>
        </template>
        <IndicatorPanel />
      </van-collapse-item>
    </van-collapse>

    <!-- Real-time Predictions -->
    <div class="predictions-section">
      <div class="section-header">
        <div class="title-wrap">
          <h3 class="section-title">各 AI 模型 5M 预测结论</h3>
          <span class="badge-count" v-if="predictionStore.latestPredictions.length">
            {{ predictionStore.latestPredictions.length }} 个模型就绪
          </span>
        </div>
        <span class="refresh-btn" @click="refreshAll">
          <van-icon name="replay" size="12" />
          <span>刷新</span>
        </span>
      </div>

      <div v-if="predictionStore.latestPredictions.length" class="predictions-list">
        <PredictionCard
          v-for="pred in predictionStore.latestPredictions"
          :key="pred.id"
          :prediction="pred"
        />
      </div>

      <div v-else class="empty-box">
        <van-empty description="当前周期暂无预测数据，请在「设置」中添加AI模型后点击「立即推演」" image="search" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 8px;
  min-height: 100vh;
  background: #0a0b14;
  padding-bottom: 75px;
}
.m5-cycle-card {
  display: flex;
  flex-direction: column;
  padding: 14px 16px 12px;
  margin: 6px 4px 12px;
  background: linear-gradient(135deg, #13172b 0%, #0e1122 100%);
  border-radius: 12px;
  border: 1px solid rgba(0, 240, 144, 0.2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.cycle-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.cycle-progress-track {
  width: 100%;
  height: 3px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  margin-top: 10px;
  overflow: hidden;
}
.cycle-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #00b0ff 0%, #00f090 100%);
  border-radius: 3px;
  transition: width 1s linear;
}
.cycle-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.cycle-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #00f090;
  font-weight: 600;
}
.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #00f090;
  box-shadow: 0 0 6px #00f090;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { transform: scale(0.9); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0.8; }
}
.cycle-interval {
  font-size: 17px;
  font-weight: 800;
  color: #f0f2f5;
  font-family: 'Courier New', Courier, monospace;
}
.cycle-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.countdown-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}
.cd-label {
  font-size: 10px;
  color: #7d889b;
}
.cd-time {
  color: #00f090;
  font-weight: 800;
  font-size: 17px;
  font-family: monospace;
}
.trigger-btn {
  background: linear-gradient(90deg, #00c853 0%, #00e676 100%);
  border: none;
  font-weight: 700;
  font-size: 12px;
  padding: 0 12px;
  box-shadow: 0 2px 10px rgba(0, 200, 83, 0.3);
}
.collapse-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}
.c-title {
  font-size: 14px;
  font-weight: 700;
  color: #f0f2f5;
}
.c-sub {
  font-size: 11px;
  color: #7d889b;
}
.dashboard-collapse {
  margin: 0 4px 12px;
}
:deep(.van-collapse-item) {
  margin-bottom: 8px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
:deep(.van-collapse-item__title) {
  background: #121424;
  color: #f0f2f5;
  padding: 12px 14px;
}
:deep(.van-collapse-item__content) {
  background: #0d0f1e;
  padding: 8px 10px;
}
:deep(.van-collapse-item__wrapper) {
  background: #0d0f1e;
}
.predictions-section {
  margin: 14px 4px 0;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 0 4px;
}
.title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-title {
  font-size: 15px;
  font-weight: 700;
  padding-left: 8px;
  border-left: 4px solid #00f090;
  color: #f0f2f5;
  margin: 0;
}
.badge-count {
  font-size: 11px;
  color: #00f090;
  background: rgba(0, 240, 144, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}
.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #00f090;
  cursor: pointer;
}
.empty-box {
  margin: 16px 0;
  background: #121424;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 24px 0;
}
</style>

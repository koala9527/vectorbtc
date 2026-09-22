<script setup lang="ts">
import { computed } from 'vue';
import { useMarketStore } from '../stores/market';

const marketStore = useMarketStore();
const ind = computed(() => marketStore.indicators || {});

const formatNum = (val: any, decimals = 2) => {
  if (val === undefined || val === null || isNaN(val)) return '-';
  return Number(val).toFixed(decimals);
};

const rsiVal = computed(() => {
  const r = Number(ind.value.rsi_14);
  return isNaN(r) ? 50 : Math.max(0, Math.min(100, r));
});

const rsiStatus = computed(() => {
  const rsi = rsiVal.value;
  if (rsi >= 70) return { text: '超买区', color: '#ff3355' };
  if (rsi <= 30) return { text: '超卖反弹', color: '#00f090' };
  if (rsi > 50) return { text: '多头占优', color: '#00f090' };
  return { text: '空头承压', color: '#ff3355' };
});

const macdStatus = computed(() => {
  const hist = Number(ind.value.macd_hist || 0);
  if (hist > 0) return { text: '红柱多头放量', color: '#00f090' };
  if (hist < 0) return { text: '绿柱空头放量', color: '#ff3355' };
  return { text: '多空平衡', color: '#8f9ca2' };
});

const emaStatus = computed(() => {
  const ema7 = Number(ind.value.ema_7 || 0);
  const ema25 = Number(ind.value.ema_25 || 0);
  if (ema7 > ema25) return { text: 'EMA金叉排列', color: '#00f090' };
  return { text: 'EMA死叉排列', color: '#ff3355' };
});
</script>

<template>
  <div class="indicators-container">
    <div class="indicator-grid">
      <!-- MACD Card -->
      <div class="ind-card">
        <div class="ind-head">
          <span class="ind-name">MACD (12, 26, 9)</span>
          <span class="status-badge" :style="{ color: macdStatus.color }">{{ macdStatus.text }}</span>
        </div>
        <div class="ind-body">
          <div class="stat-line">
            <span class="k">DIF (快线):</span>
            <span class="v font-mono">{{ formatNum(ind.macd) }}</span>
          </div>
          <div class="stat-line">
            <span class="k">DEA (慢线):</span>
            <span class="v font-mono">{{ formatNum(ind.macd_signal) }}</span>
          </div>
          <div class="stat-line">
            <span class="k">HIST (能量柱):</span>
            <span class="v font-mono bold" :style="{ color: (ind.macd_hist || 0) >= 0 ? '#00f090' : '#ff3355' }">
              {{ (ind.macd_hist || 0) >= 0 ? '+' : '' }}{{ formatNum(ind.macd_hist) }}
            </span>
          </div>
        </div>
      </div>

      <!-- RSI Card with Visual Progress -->
      <div class="ind-card">
        <div class="ind-head">
          <span class="ind-name">RSI (14) 强弱度</span>
          <span class="status-badge" :style="{ color: rsiStatus.color }">{{ rsiStatus.text }}</span>
        </div>
        <div class="rsi-body">
          <div class="rsi-num font-mono" :style="{ color: rsiVal >= 50 ? '#00f090' : '#ff3355' }">
            {{ formatNum(rsiVal, 1) }}
          </div>
          <div class="rsi-bar-wrap">
            <div class="rsi-track">
              <div
                class="rsi-fill"
                :style="{ width: rsiVal + '%', background: rsiVal >= 50 ? '#00f090' : '#ff3355' }"
              ></div>
              <div class="rsi-midline"></div>
            </div>
            <div class="rsi-scale">
              <span>0</span>
              <span class="mid">50</span>
              <span>100</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Bollinger Bands Card -->
      <div class="ind-card">
        <div class="ind-head">
          <span class="ind-name">布林通道 (20, 2)</span>
          <span class="status-badge">M5 通道</span>
        </div>
        <div class="ind-body">
          <div class="stat-line">
            <span class="k">上轨 (阻力):</span>
            <span class="v font-mono red">${{ formatNum(ind.bb_upper, 1) }}</span>
          </div>
          <div class="stat-line">
            <span class="k">中轨 (均线):</span>
            <span class="v font-mono yellow">${{ formatNum(ind.bb_middle, 1) }}</span>
          </div>
          <div class="stat-line">
            <span class="k">下轨 (支撑):</span>
            <span class="v font-mono green">${{ formatNum(ind.bb_lower, 1) }}</span>
          </div>
        </div>
      </div>

      <!-- EMA & SMA System -->
      <div class="ind-card">
        <div class="ind-head">
          <span class="ind-name">均线共振系统</span>
          <span class="status-badge" :style="{ color: emaStatus.color }">{{ emaStatus.text }}</span>
        </div>
        <div class="ind-body">
          <div class="stat-line">
            <span class="k">EMA(7) 极速:</span>
            <span class="v font-mono">${{ formatNum(ind.ema_7, 1) }}</span>
          </div>
          <div class="stat-line">
            <span class="k">EMA(25) 短线:</span>
            <span class="v font-mono">${{ formatNum(ind.ema_25, 1) }}</span>
          </div>
          <div class="stat-line">
            <span class="k">SMA(99) 牛熊:</span>
            <span class="v font-mono">${{ formatNum(ind.sma_99, 1) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.indicators-container {
  padding: 4px 0;
}
.indicator-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.ind-card {
  background: linear-gradient(145deg, #13172b 0%, #0d0f1e 100%);
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.ind-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.ind-name {
  font-size: 11px;
  font-weight: 700;
  color: #d8e0ec;
}
.status-badge {
  font-size: 10px;
  font-weight: 700;
  color: #7d889b;
}
.ind-body {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.stat-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}
.stat-line .k {
  color: #7d889b;
}
.stat-line .v {
  color: #f0f2f5;
  font-weight: 600;
}
.stat-line .v.bold {
  font-weight: 800;
}
.stat-line .v.green {
  color: #00f090;
}
.stat-line .v.red {
  color: #ff3355;
}
.stat-line .v.yellow {
  color: #f0b90b;
}
.font-mono {
  font-family: 'Courier New', Courier, monospace;
}
.rsi-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}
.rsi-num {
  font-size: 26px;
  font-weight: 900;
  line-height: 1;
}
.rsi-bar-wrap {
  width: 100%;
}
.rsi-track {
  position: relative;
  width: 100%;
  height: 6px;
  background: #080a14;
  border-radius: 3px;
  overflow: hidden;
}
.rsi-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}
.rsi-midline {
  position: absolute;
  top: 0;
  left: 50%;
  width: 2px;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
}
.rsi-scale {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: #555d6e;
  margin-top: 2px;
  font-family: monospace;
}
.rsi-scale .mid {
  color: #7d889b;
}
</style>

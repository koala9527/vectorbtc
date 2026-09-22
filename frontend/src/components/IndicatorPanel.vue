<script setup lang="ts">
import { computed } from 'vue';
import { useMarketStore } from '../stores/market';

const marketStore = useMarketStore();
const ind = computed(() => marketStore.indicators || {});

const formatNum = (val: any) => {
  if (val === undefined || val === null || isNaN(val)) return '-';
  return Number(val).toFixed(2);
};

const rsiStatus = computed(() => {
  const rsi = ind.value.rsi_14;
  if (!rsi) return { text: '正常', color: '#8f9ca2' };
  if (rsi >= 70) return { text: '超买', color: '#ff1744' };
  if (rsi <= 30) return { text: '超卖', color: '#00c853' };
  return { text: '中性', color: '#8f9ca2' };
});

const macdStatus = computed(() => {
  const hist = ind.value.macd_hist;
  if (!hist) return { text: '平稳', color: '#8f9ca2' };
  if (hist > 0) return { text: '多头', color: '#00c853' };
  return { text: '空头', color: '#ff1744' };
});
</script>

<template>
  <div class="indicators">
    <div class="indicator-grid">
      <div class="ind-card">
        <div class="ind-title">
          <span>MACD (12, 26, 9)</span>
          <span class="badge" :style="{ color: macdStatus.color }">{{ macdStatus.text }}</span>
        </div>
        <div class="ind-values">
          <div>DIF: <span class="val">{{ formatNum(ind.macd) }}</span></div>
          <div>DEA: <span class="val">{{ formatNum(ind.macd_signal) }}</span></div>
          <div>HIST: <span class="val" :style="{ color: (ind.macd_hist || 0) >= 0 ? '#00c853' : '#ff1744' }">{{ formatNum(ind.macd_hist) }}</span></div>
        </div>
      </div>

      <div class="ind-card">
        <div class="ind-title">
          <span>RSI (14)</span>
          <span class="badge" :style="{ color: rsiStatus.color }">{{ rsiStatus.text }}</span>
        </div>
        <div class="ind-main-val" :style="{ color: (ind.rsi_14 || 50) > 50 ? '#00c853' : '#ff1744' }">
          {{ formatNum(ind.rsi_14) }}
        </div>
      </div>

      <div class="ind-card">
        <div class="ind-title">布林带 (20, 2)</div>
        <div class="ind-values">
          <div>上轨: <span class="val">{{ formatNum(ind.bb_upper) }}</span></div>
          <div>中轨: <span class="val">{{ formatNum(ind.bb_middle) }}</span></div>
          <div>下轨: <span class="val">{{ formatNum(ind.bb_lower) }}</span></div>
        </div>
      </div>

      <div class="ind-card">
        <div class="ind-title">均线系统</div>
        <div class="ind-values">
          <div>EMA(7): <span class="val">{{ formatNum(ind.ema_7) }}</span></div>
          <div>EMA(25): <span class="val">{{ formatNum(ind.ema_25) }}</span></div>
          <div>SMA(99): <span class="val">{{ formatNum(ind.sma_99) }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.indicators {
  padding: 8px 4px;
}
.indicator-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.ind-card {
  background: #1e2a3a;
  padding: 10px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.ind-title {
  font-size: 12px;
  font-weight: 600;
  color: #8f9ca2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.badge {
  font-size: 11px;
  font-weight: bold;
}
.ind-values {
  font-size: 11px;
  color: #8f9ca2;
  line-height: 1.6;
}
.ind-values .val {
  color: #e0e0e0;
  font-family: monospace;
}
.ind-main-val {
  font-size: 24px;
  font-weight: bold;
  font-family: monospace;
  margin: auto 0;
  text-align: center;
}
</style>

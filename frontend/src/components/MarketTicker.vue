<script setup lang="ts">
import { computed } from 'vue';
import { useMarketStore } from '../stores/market';

const marketStore = useMarketStore();

const pctChange = computed(() => parseFloat(marketStore.priceChangePct24h) || 0);

const priceColor = computed(() => {
  return pctChange.value >= 0 ? '#00f090' : '#ff3355';
});

const changeText = computed(() => {
  const val = pctChange.value;
  return (val >= 0 ? '+' : '') + val.toFixed(2) + '%';
});

const formatVolume = computed(() => {
  const vol = parseFloat(marketStore.volume24h) || 0;
  if (vol >= 1e9) return (vol / 1e9).toFixed(2) + 'B';
  if (vol >= 1e6) return (vol / 1e6).toFixed(2) + 'M';
  if (vol >= 1e3) return (vol / 1e3).toFixed(2) + 'K';
  return vol.toFixed(2);
});
</script>

<template>
  <div class="market-ticker">
    <div class="ticker-header">
      <div class="pair-wrap">
        <span class="pair">BTC / USDT</span>
        <span class="m5-beacon">
          <span class="pulse-dot"></span>
          5M 周期
        </span>
      </div>
      <div class="badge-wrap">
        <span class="change-badge" :class="pctChange >= 0 ? 'up' : 'down'">
          {{ changeText }}
        </span>
      </div>
    </div>

    <div class="price-row">
      <span class="currency-symbol">$</span>
      <span class="price" :style="{ color: priceColor }">
        {{ marketStore.currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
      </span>
      <span class="live-tag">实盘实时</span>
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <span class="stat-label">24H 最高</span>
        <span class="stat-value">${{ parseFloat(marketStore.high24h).toLocaleString('en-US', { minimumFractionDigits: 1 }) }}</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-label">24H 最低</span>
        <span class="stat-value">${{ parseFloat(marketStore.low24h).toLocaleString('en-US', { minimumFractionDigits: 1 }) }}</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-label">24H 额 (USDT)</span>
        <span class="stat-value">{{ formatVolume }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.market-ticker {
  background: linear-gradient(145deg, #121528 0%, #0d0f1e 100%);
  padding: 16px 18px;
  border-radius: 14px;
  margin: 6px 4px 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}
.ticker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.pair-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.pair {
  font-size: 16px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 0.5px;
}
.m5-beacon {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  color: #00f090;
  background: rgba(0, 240, 144, 0.12);
  border: 1px solid rgba(0, 240, 144, 0.3);
  padding: 2px 7px;
  border-radius: 20px;
}
.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #00f090;
  box-shadow: 0 0 8px #00f090;
  animation: pulse 1.8s infinite;
}
@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}
.change-badge {
  font-size: 13px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
}
.change-badge.up {
  color: #00f090;
  background: rgba(0, 240, 144, 0.12);
}
.change-badge.down {
  color: #ff3355;
  background: rgba(255, 51, 85, 0.12);
}
.price-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin: 6px 0 14px;
}
.currency-symbol {
  font-size: 22px;
  color: #8c98ad;
  font-weight: 600;
}
.price {
  font-size: 38px;
  font-weight: 900;
  letter-spacing: -0.5px;
  font-family: 'SF Pro Display', -apple-system, sans-serif;
  line-height: 1;
}
.live-tag {
  font-size: 11px;
  color: #7d889b;
  margin-left: 4px;
}
.stats-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.03);
}
.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-divider {
  width: 1px;
  height: 20px;
  background: rgba(255, 255, 255, 0.08);
}
.stat-label {
  font-size: 10px;
  color: #7d889b;
}
.stat-value {
  font-size: 12px;
  color: #d8e0ec;
  font-weight: 600;
  font-family: monospace;
}
</style>

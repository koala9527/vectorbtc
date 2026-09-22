<script setup lang="ts">
import { computed } from 'vue';
import { useMarketStore } from '../stores/market';

const marketStore = useMarketStore();

const pctChange = computed(() => parseFloat(marketStore.priceChangePct24h) || 0);

const priceColor = computed(() => {
  return pctChange.value >= 0 ? '#00c853' : '#ff1744';
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
      <span class="pair">BTC/USDT</span>
      <van-tag :type="pctChange >= 0 ? 'success' : 'danger'" size="medium">
        {{ changeText }}
      </van-tag>
    </div>
    <div class="price" :style="{ color: priceColor }">
      ${{ marketStore.currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
    </div>
    <div class="stats-row">
      <div class="stat-item">
        <span class="stat-label">24H高</span>
        <span class="stat-value">{{ parseFloat(marketStore.high24h).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">24H低</span>
        <span class="stat-value">{{ parseFloat(marketStore.low24h).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">24H量</span>
        <span class="stat-value">{{ formatVolume }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.market-ticker {
  background: linear-gradient(135deg, #1e2a3a 0%, #1a1a2e 100%);
  padding: 16px;
  border-radius: 12px;
  margin: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
.ticker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.pair {
  font-size: 16px;
  font-weight: 600;
  color: #e0e0e0;
}
.price {
  font-size: 36px;
  font-weight: bold;
  margin: 4px 0 12px;
  letter-spacing: -1px;
}
.stats-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.stat-label {
  font-size: 11px;
  color: #8f9ca2;
  margin-bottom: 2px;
}
.stat-value {
  font-size: 13px;
  color: #c0c0c0;
  font-weight: 500;
}
</style>

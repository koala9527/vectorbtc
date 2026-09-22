<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  prediction: any;
}>();

const predDirection = computed(() => {
  return (props.prediction.prediction || props.prediction.direction || 'SKIP').toUpperCase();
});

const directionLabel = computed(() => {
  if (predDirection.value === 'UP') return '看涨 (UP)';
  if (predDirection.value === 'DOWN') return '看跌 (DOWN)';
  return '观望 (SKIP)';
});

const directionColor = computed(() => {
  if (predDirection.value === 'UP') return '#00f090';
  if (predDirection.value === 'DOWN') return '#ff3355';
  return '#f0b90b';
});

const resultStatus = computed(() => {
  if (!props.prediction.settled) {
    return { text: '5M 推演中 · 待结算', type: 'primary' as const, bg: 'rgba(25, 137, 250, 0.15)', color: '#389e0d' };
  }
  if (predDirection.value === 'SKIP') {
    return { text: '已跳过 (SKIP)', type: 'warning' as const, bg: 'rgba(240, 185, 11, 0.15)', color: '#f0b90b' };
  }
  if (props.prediction.is_correct === true) {
    return { text: '✓ 预测准确', type: 'success' as const, bg: 'rgba(0, 240, 144, 0.15)', color: '#00f090' };
  }
  if (props.prediction.is_correct === false) {
    return { text: '✗ 预测偏差', type: 'danger' as const, bg: 'rgba(255, 51, 85, 0.15)', color: '#ff3355' };
  }
  return { text: '待定', type: 'default' as const, bg: '#1e2a3a', color: '#8f9ca2' };
});

const confidencePct = computed(() => {
  const conf = props.prediction.confidence ?? 0;
  return Math.min(100, Math.max(0, Math.round(conf * 100)));
});
</script>

<template>
  <div class="prediction-card" :class="predDirection.toLowerCase()">
    <!-- Card Header -->
    <div class="card-header">
      <div class="model-info">
        <span class="m5-tag">5M</span>
        <span class="model-name">{{ prediction.model_name || prediction.ai_model?.name || 'AI Model' }}</span>
      </div>
      <span class="status-tag" :style="{ background: resultStatus.bg, color: resultStatus.color }">
        {{ resultStatus.text }}
      </span>
    </div>

    <!-- Direction & Price Row -->
    <div class="card-body">
      <div class="direction-row">
        <div class="dir-badge" :style="{ color: directionColor, borderColor: directionColor }">
          <span class="dir-arrow">{{ predDirection === 'UP' ? '▲' : predDirection === 'DOWN' ? '▼' : '—' }}</span>
          <span class="dir-text">{{ directionLabel }}</span>
        </div>
        <div class="price-box" v-if="prediction.entry_price">
          <div class="p-item">
            <span class="p-label">开盘入场</span>
            <span class="p-val font-mono">${{ prediction.entry_price?.toFixed(2) }}</span>
          </div>
          <div class="p-item" v-if="prediction.exit_price">
            <span class="p-label">收盘结算</span>
            <span class="p-val font-mono highlight">${{ prediction.exit_price?.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Confidence Bar -->
      <div class="confidence-bar">
        <div class="conf-text">
          <span class="conf-title">量化模型置信度</span>
          <span class="conf-num" :style="{ color: directionColor }">{{ confidencePct }}%</span>
        </div>
        <div class="progress-track">
          <div
            class="progress-fill"
            :style="{ width: confidencePct + '%', backgroundColor: directionColor, boxShadow: '0 0 8px ' + directionColor }"
          ></div>
        </div>
      </div>

      <!-- Direct Visible Reasoning (Convincing & Engaging!) -->
      <div class="reasoning-box" v-if="prediction.reasoning">
        <div class="reasoning-header">
          <van-icon name="chart-trending-o" size="12" color="#00f090" />
          <span>5M 量化决策推演逻辑:</span>
        </div>
        <div class="reasoning-body">{{ prediction.reasoning }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.prediction-card {
  background: linear-gradient(145deg, #13172b 0%, #0d0f1e 100%);
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
  transition: all 0.2s ease;
}
.prediction-card.up {
  border-left: 3px solid #00f090;
}
.prediction-card.down {
  border-left: 3px solid #ff3355;
}
.prediction-card.skip {
  border-left: 3px solid #f0b90b;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.model-info {
  display: flex;
  align-items: center;
  gap: 6px;
}
.m5-tag {
  font-size: 10px;
  font-weight: 800;
  color: #00f090;
  background: rgba(0, 240, 144, 0.15);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: monospace;
}
.model-name {
  font-size: 14px;
  font-weight: 700;
  color: #f0f2f5;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.status-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}
.card-body {
  padding: 14px;
}
.direction-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.dir-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 17px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid;
}
.dir-arrow {
  font-size: 14px;
}
.price-box {
  display: flex;
  gap: 12px;
  background: rgba(0, 0, 0, 0.2);
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.03);
}
.p-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 1px;
}
.p-label {
  font-size: 9px;
  color: #7d889b;
}
.p-val {
  font-size: 12px;
  color: #d8e0ec;
  font-weight: 600;
}
.p-val.highlight {
  color: #00f090;
}
.font-mono {
  font-family: 'Courier New', Courier, monospace;
}
.confidence-bar {
  margin-bottom: 12px;
}
.conf-text {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 5px;
}
.conf-title {
  color: #7d889b;
}
.conf-num {
  font-weight: 700;
  font-family: monospace;
}
.progress-track {
  width: 100%;
  height: 6px;
  background: #080a14;
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}
.reasoning-box {
  background: rgba(18, 20, 36, 0.7);
  border-radius: 8px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.reasoning-header {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #00f090;
  font-weight: 600;
  margin-bottom: 4px;
}
.reasoning-body {
  font-size: 12px;
  line-height: 1.6;
  color: #cbd5e1;
  word-break: break-word;
}
</style>

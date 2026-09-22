<script setup lang="ts">
import { computed, ref } from 'vue';

const props = defineProps<{
  prediction: any;
}>();

const activeNames = ref<string[]>([]);

const predDirection = computed(() => {
  return (props.prediction.prediction || props.prediction.direction || 'SKIP').toUpperCase();
});

const directionLabel = computed(() => {
  if (predDirection.value === 'UP') return '看涨 (UP)';
  if (predDirection.value === 'DOWN') return '看跌 (DOWN)';
  return '观望 (SKIP)';
});

const directionIcon = computed(() => {
  if (predDirection.value === 'UP') return 'arrow-up';
  if (predDirection.value === 'DOWN') return 'arrow-down';
  return 'minus';
});

const directionColor = computed(() => {
  if (predDirection.value === 'UP') return '#00c853';
  if (predDirection.value === 'DOWN') return '#ff1744';
  return '#8f9ca2';
});

const resultStatus = computed(() => {
  if (!props.prediction.settled) {
    return { text: '待结算', type: 'primary' as const, color: '#1989fa' };
  }
  if (predDirection.value === 'SKIP') {
    return { text: '跳过', type: 'warning' as const, color: '#ff976a' };
  }
  if (props.prediction.is_correct === true) {
    return { text: '✓ 准确', type: 'success' as const, color: '#00c853' };
  }
  if (props.prediction.is_correct === false) {
    return { text: '✗ 错误', type: 'danger' as const, color: '#ff1744' };
  }
  return { text: '待定', type: 'default' as const, color: '#8f9ca2' };
});

const confidencePct = computed(() => {
  const conf = props.prediction.confidence ?? 0;
  return Math.min(100, Math.max(0, Math.round(conf * 100)));
});
</script>

<template>
  <div class="prediction-card">
    <div class="card-header">
      <div class="model-name">
        <van-icon name="gem-o" size="14" color="#00c853" />
        <span>{{ prediction.model_name || prediction.ai_model?.name || 'AI Model' }}</span>
      </div>
      <van-tag :type="resultStatus.type" size="medium" plain>
        {{ resultStatus.text }}
      </van-tag>
    </div>

    <div class="card-body">
      <div class="direction-row">
        <div class="direction" :style="{ color: directionColor }">
          <van-icon :name="directionIcon" />
          <span>{{ directionLabel }}</span>
        </div>
        <div class="prices" v-if="prediction.entry_price">
          入场: ${{ prediction.entry_price?.toFixed(2) }}
          <span v-if="prediction.exit_price"> → 出场: ${{ prediction.exit_price?.toFixed(2) }}</span>
        </div>
      </div>

      <div class="confidence-bar">
        <div class="conf-text">
          <span>置信度</span>
          <span class="conf-val">{{ confidencePct }}%</span>
        </div>
        <van-progress
          :percentage="confidencePct"
          stroke-width="5"
          :color="directionColor"
          track-color="#0f0f1a"
          :show-pivot="false"
        />
      </div>
    </div>

    <div class="card-footer" v-if="prediction.reasoning">
      <van-collapse v-model="activeNames" :border="false">
        <van-collapse-item title="AI 决策理由" name="1">
          <div class="reasoning-text">{{ prediction.reasoning }}</div>
        </van-collapse-item>
      </van-collapse>
    </div>
  </div>
</template>

<style scoped>
.prediction-card {
  background: #1a1a2e;
  border-radius: 10px;
  margin: 10px;
  overflow: hidden;
  border: 1px solid #2a2a3e;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: #1e2a3a;
  border-bottom: 1px solid #2a2a3e;
}
.model-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #e0e0e0;
}
.card-body {
  padding: 12px 14px;
}
.direction-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.direction {
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
}
.prices {
  font-size: 12px;
  color: #8f9ca2;
  font-family: monospace;
}
.confidence-bar {
  margin-top: 6px;
}
.conf-text {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #8f9ca2;
  margin-bottom: 4px;
}
.conf-val {
  font-weight: 600;
  color: #e0e0e0;
}
.card-footer {
  border-top: 1px solid #2a2a3e;
}
.reasoning-text {
  font-size: 12px;
  color: #c0c0c0;
  line-height: 1.5;
  white-space: pre-wrap;
}
:deep(.van-collapse-item__title) {
  background: transparent;
  padding: 8px 14px;
  font-size: 12px;
  color: #8f9ca2;
}
:deep(.van-collapse-item__content) {
  background: #151524;
  padding: 10px 14px;
}
</style>

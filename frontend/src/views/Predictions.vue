<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { usePredictionStore } from '../stores/prediction';
import { useSettingsStore } from '../stores/settings';
import dayjs from 'dayjs';

const predictionStore = usePredictionStore();
const settingsStore = useSettingsStore();

const refreshing = ref(false);
const selectedModel = ref(0);
const modelOptions = ref([{ text: '全部模型', value: 0 }]);

const loadData = async (isRefresh = false) => {
  await predictionStore.fetchHistory(selectedModel.value || undefined, isRefresh);
};

const onRefresh = async () => {
  refreshing.value = true;
  await loadData(true);
  refreshing.value = false;
};

const onLoad = () => loadData(false);

const onModelChange = () => {
  loadData(true);
};

onMounted(async () => {
  await settingsStore.fetchModels();
  const opts = settingsStore.aiModels.map((m: any) => ({ text: m.name, value: m.id }));
  modelOptions.value = [{ text: '全部模型', value: 0 }, ...opts];
});

const formatTime = (time: string) => dayjs(time).format('MM-DD HH:mm');

const directionIcon = (dir: string) => {
  if (dir === 'UP') return '▲';
  if (dir === 'DOWN') return '▼';
  return '—';
};

const directionColor = (dir: string) => {
  if (dir === 'UP') return '#00c853';
  if (dir === 'DOWN') return '#ff1744';
  return '#8f9ca2';
};

const getResultTag = (item: any) => {
  if (!item.settled) return { type: 'primary' as const, text: '待结算' };
  if (item.prediction === 'SKIP') return { type: 'warning' as const, text: '跳过' };
  if (item.is_correct === true) return { type: 'success' as const, text: '✓ 正确' };
  if (item.is_correct === false) return { type: 'danger' as const, text: '✗ 错误' };
  return { type: 'primary' as const, text: '待定' };
};
</script>

<template>
  <div class="predictions-page">
    <van-dropdown-menu>
      <van-dropdown-item v-model="selectedModel" :options="modelOptions" @change="onModelChange" />
    </van-dropdown-menu>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="predictionStore.loading"
        :finished="predictionStore.finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <van-cell v-for="item in predictionStore.history" :key="item.id" class="pred-cell">
          <template #title>
            <div class="pred-row">
              <span class="time">{{ formatTime(item.predicted_at) }}</span>
              <span class="prediction" :style="{ color: directionColor(item.prediction) }">
                {{ directionIcon(item.prediction) }} {{ item.prediction }}
              </span>
              <span v-if="item.actual_direction" class="actual" :style="{ color: directionColor(item.actual_direction) }">
                → {{ directionIcon(item.actual_direction) }}
              </span>
            </div>
          </template>
          <template #label>
            <div class="pred-detail">
              <span>信心: {{ (item.confidence * 100).toFixed(0) }}%</span>
              <span v-if="item.entry_price">入场: {{ item.entry_price?.toFixed(2) }}</span>
              <span v-if="item.exit_price">出场: {{ item.exit_price?.toFixed(2) }}</span>
            </div>
          </template>
          <template #value>
            <van-tag :type="getResultTag(item).type" plain>{{ getResultTag(item).text }}</van-tag>
          </template>
        </van-cell>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.predictions-page {
  min-height: 100vh;
  background: #0f0f1a;
}
.pred-cell {
  background: #1a1a2e !important;
  border-bottom: 1px solid #2a2a3e;
}
.pred-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.time {
  font-size: 12px;
  color: #8f9ca2;
}
.prediction {
  font-weight: bold;
  font-size: 14px;
}
.actual {
  font-size: 13px;
}
.pred-detail {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #8f9ca2;
  margin-top: 4px;
}
:deep(.van-dropdown-menu__bar) {
  background: #1a1a2e;
}
:deep(.van-dropdown-menu__title) {
  color: #e0e0e0;
}
:deep(.van-cell__label) {
  color: #8f9ca2;
}
:deep(.van-list__finished-text) {
  color: #8f9ca2;
}
</style>

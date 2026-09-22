<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  model: any;
}>();

defineEmits(['edit', 'test', 'delete', 'toggle']);

const winRate = computed(() => {
  const total = props.model.total_predictions || 0;
  const correct = props.model.correct_predictions || 0;
  if (total === 0) return '0.0%';
  return ((correct / total) * 100).toFixed(1) + '%';
});
</script>

<template>
  <div class="ai-model-card" :class="{ 'is-disabled': !model.is_active }">
    <div class="card-top">
      <div class="model-info">
        <div class="model-name">
          <span>{{ model.name }}</span>
          <van-tag :type="model.is_active ? 'success' : 'default'">
            {{ model.is_active ? '启用中' : '已停用' }}
          </van-tag>
        </div>
        <div class="model-sub">{{ model.model_name }} · {{ model.provider || 'Custom API' }}</div>
      </div>
      <div class="top-right-wrap">
        <div class="switch-box" @click.stop>
          <span class="switch-label">{{ model.is_active ? '已启用' : '已停用' }}</span>
          <van-switch
            :model-value="model.is_active"
            size="18px"
            active-color="#00c853"
            inactive-color="#3a3a4e"
            @change="$emit('toggle', model)"
          />
        </div>
        <div class="rate-badge">
          <div class="rate-val">{{ winRate }}</div>
          <div class="rate-label">胜率</div>
        </div>
      </div>
    </div>

    <div v-if="!model.is_active" class="disabled-tip-banner">
      <van-icon name="info-o" size="13" />
      <span>已停用：该模型数据已在行情、预测和统计大盘中隐藏</span>
    </div>

    <div class="card-details">
      <div class="detail-item">
        <span class="label">API地址:</span>
        <span class="val truncate">{{ model.base_url }}</span>
      </div>
      <div class="detail-item">
        <span class="label">密钥:</span>
        <span class="val">{{ model.api_key_masked || '••••••••' }}</span>
      </div>
      <div class="detail-item stats-row">
        <span>总预测: {{ model.total_predictions || 0 }}</span>
        <span>正确: {{ model.correct_predictions || 0 }}</span>
        <span>跳过: {{ model.skip_predictions || 0 }}</span>
      </div>
    </div>

    <div class="card-actions">
      <van-button
        size="small"
        :type="model.is_active ? 'warning' : 'success'"
        plain
        :icon="model.is_active ? 'pause-circle-o' : 'play-circle-o'"
        @click="$emit('toggle', model)"
      >
        {{ model.is_active ? '停用' : '启用' }}
      </van-button>
      <van-button size="small" type="primary" plain icon="play-circle-o" @click="$emit('test', model.id)">测试连接</van-button>
      <van-button size="small" type="default" plain icon="edit" @click="$emit('edit', model)">编辑</van-button>
      <van-button size="small" type="danger" plain icon="delete-o" @click="$emit('delete', model.id)">删除</van-button>
    </div>
  </div>
</template>

<style scoped>
.ai-model-card {
  background: #1a1a2e;
  border-radius: 12px;
  border: 1px solid #2a2a3e;
  margin-bottom: 12px;
  padding: 14px;
  transition: all 0.3s ease;
}
.ai-model-card.is-disabled {
  opacity: 0.65;
  border-color: rgba(255, 255, 255, 0.08);
  background: #141424;
}
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}
.top-right-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.switch-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  background: rgba(255, 255, 255, 0.03);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.switch-label {
  font-size: 10px;
  color: #7d889b;
}
.disabled-tip-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 179, 0, 0.1);
  border: 1px solid rgba(255, 179, 0, 0.25);
  color: #ffb300;
  font-size: 11px;
  padding: 6px 10px;
  border-radius: 6px;
  margin-bottom: 10px;
}
.model-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.model-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #e0e0e0;
}
.model-sub {
  font-size: 12px;
  color: #8f9ca2;
}
.rate-badge {
  text-align: right;
  background: #1e2a3a;
  padding: 6px 12px;
  border-radius: 8px;
}
.rate-val {
  font-size: 18px;
  font-weight: bold;
  color: #00c853;
  font-family: monospace;
}
.rate-label {
  font-size: 11px;
  color: #8f9ca2;
}
.card-details {
  background: #151524;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}
.detail-item {
  display: flex;
  gap: 6px;
  color: #8f9ca2;
}
.detail-item .val {
  color: #c0c0c0;
  font-family: monospace;
}
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}
.stats-row {
  display: flex;
  justify-content: space-between;
  border-top: 1px dashed #2a2a3e;
  padding-top: 4px;
  margin-top: 2px;
  color: #8f9ca2;
  font-size: 11px;
}
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { showToast, showConfirmDialog } from 'vant';
import AIModelCard from '../components/AIModelCard.vue';
import { useSettingsStore } from '../stores/settings';
import { aiModelsApi } from '../api';

const settingsStore = useSettingsStore();
const showForm = ref(false);
const formTitle = ref('添加模型');
const isEdit = ref(false);
const form = ref({
  id: 0,
  name: '',
  provider: 'DeepSeek',
  base_url: '',
  api_key: '',
  model_name: '',
  temperature: 0.3,
  system_prompt: '',
  is_active: true,
});

// Test Result Modal State
const showTestModal = ref(false);
const testLoading = ref(false);
const testResult = ref<any>({
  model_name: '',
  prediction: '',
  confidence: 0,
  reasoning: '',
  latency: 0,
  success: true,
  error: '',
});

onMounted(() => {
  settingsStore.fetchModels();
});

const openAdd = () => {
  isEdit.value = false;
  formTitle.value = '添加 5M 预测 AI 模型';
  form.value = {
    id: 0,
    name: '',
    provider: 'DeepSeek',
    base_url: 'https://api.deepseek.com/v1',
    api_key: '',
    model_name: 'deepseek-chat',
    temperature: 0.3,
    system_prompt: '',
    is_active: true,
  };
  showForm.value = true;
};

const openEdit = (model: any) => {
  isEdit.value = true;
  formTitle.value = '编辑 AI 模型配置';
  form.value = {
    ...model,
    is_active: model.is_active !== undefined ? model.is_active : true,
    api_key: '', // Leave blank if not modifying
  };
  showForm.value = true;
};

const onToggleActive = async (model: any) => {
  try {
    const updated: any = await aiModelsApi.toggle(model.id);
    model.is_active = updated.is_active;
    showToast({
      type: 'success',
      message: updated.is_active
        ? `模型「${model.name}」已启用`
        : `模型「${model.name}」已停用，其数据已在行情、预测和统计中隐藏`,
    });
    settingsStore.fetchModels();
  } catch (e) {
    // Handled by interceptor
  }
};

const onSubmit = async () => {
  try {
    const payload = { ...form.value };
    if (isEdit.value) {
      if (!payload.api_key) {
        delete (payload as any).api_key;
      }
      await aiModelsApi.update(payload.id, payload);
      showToast({ type: 'success', message: '更新成功' });
    } else {
      await aiModelsApi.create(payload);
      showToast({ type: 'success', message: '添加成功' });
    }
    showForm.value = false;
    settingsStore.fetchModels();
  } catch (e: any) {
    // Handled by axios interceptor
  }
};

const onDelete = (id: number) => {
  showConfirmDialog({
    title: '确认删除模型',
    message: '确定要删除该模型吗？删除后该模型及其所有历史预测与胜率统计将在系统中被屏蔽隐藏。',
  }).then(async () => {
    try {
      await aiModelsApi.remove(id);
      showToast({ type: 'success', message: '删除成功，已屏蔽相关数据' });
      settingsStore.fetchModels();
    } catch (e) {
      // Handled by interceptor
    }
  }).catch(() => {});
};

const onTest = async (id: number) => {
  testLoading.value = true;
  showToast({ type: 'loading', message: '正在连通测试并执行M5量化推演...', duration: 0, forbidClick: true });
  const start = Date.now();
  try {
    const res: any = await aiModelsApi.test(id);
    const latency = Date.now() - start;
    testResult.value = {
      model_name: res.model_name || 'AI Model',
      prediction: res.prediction || 'SKIP',
      confidence: res.confidence || 0,
      reasoning: res.reasoning || '无分析说明',
      latency: latency,
      success: true,
      error: '',
    };
    showTestModal.value = true;
  } catch (e: any) {
    const latency = Date.now() - start;
    const errMsg = e.response?.data?.detail || e.message || '连接失败';
    testResult.value = {
      model_name: `模型 #${id}`,
      prediction: 'FAIL',
      confidence: 0,
      reasoning: '',
      latency: latency,
      success: false,
      error: errMsg,
    };
    showTestModal.value = true;
  } finally {
    testLoading.value = false;
  }
};
</script>

<template>
  <div class="settings-page">
    <div class="header">
      <div class="header-left">
        <h3 class="section-title">AI 多模型对决配置</h3>
        <span class="sub-title">支持配置多个量化模型同时推演 5M 涨跌</span>
      </div>
      <van-button type="primary" size="small" icon="plus" round @click="openAdd">添加模型</van-button>
    </div>

    <div class="model-list" v-if="settingsStore.aiModels.length">
      <AIModelCard
        v-for="model in settingsStore.aiModels"
        :key="model.id"
        :model="model"
        @edit="openEdit"
        @delete="onDelete"
        @test="onTest"
        @toggle="onToggleActive"
      />
    </div>
    <div v-else class="empty-wrap">
      <van-empty description="暂无配置中的 AI 模型，请点击右上角「添加模型」接入你的 API" image="search" />
    </div>

    <!-- Edit/Add Model Popup -->
    <van-popup v-model:show="showForm" position="bottom" class="model-form-popup" round>
      <div class="popup-top">
        <span class="popup-title">{{ formTitle }}</span>
        <van-icon name="cross" size="18" color="#8f9ca2" class="close-icon" @click="showForm = false" />
      </div>

      <van-form @submit="onSubmit" class="custom-form">
        <van-cell-group inset class="form-group">
          <van-field
            v-model="form.name"
            name="name"
            label="显示别名"
            placeholder="如: DeepSeek-V4-Flash"
            :rules="[{ required: true, message: '请输入模型别名' }]"
          />
          <van-field
            v-model="form.provider"
            name="provider"
            label="供应商"
            placeholder="如: DeepSeek / OpenAI / 自建代理"
          />
          <van-field
            v-model="form.base_url"
            name="base_url"
            label="API 地址"
            placeholder="如: https://api.deepseek.com/v1"
            :rules="[{ required: true, message: '请输入API Base URL' }]"
          />
          <van-field
            v-model="form.api_key"
            type="password"
            name="api_key"
            label="API Key"
            :placeholder="isEdit ? '留空表示保持原密钥不变' : '请输入 sk-xxx...'"
            :rules="isEdit ? [] : [{ required: true, message: '请输入 API 密钥' }]"
          />
          <van-field
            v-model="form.model_name"
            name="model_name"
            label="模型 ID"
            placeholder="如: deepseek-chat / gpt-4o"
            :rules="[{ required: true, message: '请输入模型标识' }]"
          />
          
          <van-field name="temperature" label="随机度 (Temp)">
            <template #input>
              <van-slider v-model="form.temperature" :min="0" :max="1" :step="0.05" />
              <div class="temp-val">{{ form.temperature }}</div>
            </template>
          </van-field>

          <van-field
            v-model="form.system_prompt"
            rows="3"
            autosize
            label="自定义 Prompt"
            type="textarea"
            placeholder="留空则使用默认高阶 M5 币安量化多空推演提示词"
          />

          <van-field name="is_active" label="启用状态">
            <template #input>
              <van-switch v-model="form.is_active" size="20px" active-color="#00c853" inactive-color="#3a3a4e" />
              <span style="margin-left: 10px; font-size: 13px; color: #8f9ca2;">
                {{ form.is_active ? '启用推演与展示' : '停用（隐藏数据与停止推演）' }}
              </span>
            </template>
          </van-field>
        </van-cell-group>
        
        <div class="submit-btn-wrap">
          <van-button round block type="primary" native-type="submit" class="save-btn">
            保存配置
          </van-button>
        </div>
      </van-form>
    </van-popup>

    <!-- Professional Test Result Modal (Fixes white-text bug!) -->
    <van-popup v-model:show="showTestModal" class="test-result-popup" round>
      <div class="test-box">
        <div class="test-header">
          <div class="test-title-wrap">
            <span class="test-title">5M 实时连通与推演测试</span>
            <span class="test-model">{{ testResult.model_name }}</span>
          </div>
          <van-tag :type="testResult.success ? 'success' : 'danger'" size="medium">
            {{ testResult.success ? '连通成功' : '请求失败' }}
          </van-tag>
        </div>

        <div v-if="testResult.success" class="test-body">
          <div class="res-row">
            <span class="label">试测周期:</span>
            <span class="val highlight">BTC/USDT 5分钟 (M5)</span>
          </div>
          <div class="res-row">
            <span class="label">响应耗时:</span>
            <span class="val font-mono">{{ testResult.latency }} ms</span>
          </div>
          <div class="res-row">
            <span class="label">5M 预测方向:</span>
            <span class="val pred-badge" :class="testResult.prediction.toLowerCase()">
              {{ testResult.prediction === 'UP' ? '▲ 看涨 (UP)' : testResult.prediction === 'DOWN' ? '▼ 看跌 (DOWN)' : '— 观望 (SKIP)' }}
            </span>
          </div>
          <div class="res-row">
            <span class="label">量化置信度:</span>
            <span class="val font-mono bold">{{ ((testResult.confidence || 0) * 100).toFixed(0) }}%</span>
          </div>

          <div class="reasoning-box">
            <div class="reasoning-label">AI 量化决策依据:</div>
            <div class="reasoning-content">{{ testResult.reasoning }}</div>
          </div>
        </div>

        <div v-else class="test-error-body">
          <van-icon name="warning-o" size="36" color="#ff3355" />
          <div class="err-title">调用 AI 模型失败</div>
          <div class="err-detail">{{ testResult.error }}</div>
          <div class="err-tip">请检查 API 密钥、Base URL 接口地址或模型名称是否正确。</div>
        </div>

        <div class="test-footer">
          <van-button round block type="primary" @click="showTestModal = false">
            好的，知道了
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 12px;
  min-height: 100vh;
  background: #0a0b14;
  padding-bottom: 75px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 6px 4px 16px;
}
.header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  padding-left: 10px;
  border-left: 4px solid #00f090;
  margin: 0;
  color: #f0f2f5;
  letter-spacing: 0.5px;
}
.sub-title {
  font-size: 11px;
  color: #7d889b;
  padding-left: 14px;
}
.empty-wrap {
  margin: 30px 6px;
  background: #121424;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 24px 0;
}

/* Edit/Add Form Popup */
.model-form-popup {
  background: #121424 !important;
  color: #f0f2f5;
  max-height: 85%;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.popup-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.popup-title {
  font-size: 16px;
  font-weight: bold;
  color: #f0f2f5;
}
.close-icon {
  cursor: pointer;
}
.custom-form {
  padding: 12px 0 24px;
}
.form-group {
  background: #181b30 !important;
}
:deep(.form-group .van-cell) {
  background: transparent !important;
  color: #f0f2f5 !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
:deep(.form-group .van-field__label) {
  color: #9aa5b8 !important;
  width: 90px;
}
:deep(.form-group .van-field__control) {
  color: #ffffff !important;
}
:deep(.form-group .van-field__control::placeholder) {
  color: #555d6e !important;
}
.temp-val {
  margin-left: 12px;
  font-family: monospace;
  color: #00f090;
  font-weight: bold;
}
.submit-btn-wrap {
  margin: 20px 20px 0;
}
.save-btn {
  background: linear-gradient(90deg, #00c853 0%, #00e676 100%);
  border: none;
  font-weight: bold;
  font-size: 15px;
}

/* Test Result Modal (Dark high-contrast, crisp text) */
.test-result-popup {
  background: #121424 !important;
  width: 90%;
  max-width: 420px;
  border: 1px solid rgba(0, 240, 144, 0.3);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
}
.test-box {
  padding: 20px;
  color: #f0f2f5;
}
.test-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.test-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.test-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
}
.test-model {
  font-size: 12px;
  color: #00f090;
  font-family: monospace;
}
.test-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 18px;
}
.res-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}
.res-row .label {
  color: #8c98ad;
}
.res-row .val {
  color: #f0f2f5;
  font-weight: 500;
}
.res-row .highlight {
  color: #00f090;
  font-weight: 600;
}
.font-mono {
  font-family: 'Courier New', Courier, monospace;
}
.bold {
  font-weight: bold;
}
.pred-badge {
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}
.pred-badge.up {
  color: #00c853;
  background: rgba(0, 200, 83, 0.15);
}
.pred-badge.down {
  color: #ff3355;
  background: rgba(255, 51, 85, 0.15);
}
.pred-badge.skip {
  color: #f0b90b;
  background: rgba(240, 185, 11, 0.15);
}
.reasoning-box {
  background: #181b30;
  border-radius: 8px;
  padding: 12px;
  margin-top: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.reasoning-label {
  font-size: 12px;
  color: #8c98ad;
  margin-bottom: 6px;
  font-weight: 600;
}
.reasoning-content {
  font-size: 13px;
  line-height: 1.6;
  color: #e2e8f0;
  white-space: pre-wrap;
}
.test-error-body {
  text-align: center;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.err-title {
  font-size: 16px;
  font-weight: bold;
  color: #ff3355;
}
.err-detail {
  font-size: 12px;
  color: #e2e8f0;
  background: rgba(255, 51, 85, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 51, 85, 0.3);
  word-break: break-all;
}
.err-tip {
  font-size: 11px;
  color: #8c98ad;
}
.test-footer {
  margin-top: 14px;
}
</style>

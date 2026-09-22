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
});

onMounted(() => {
  settingsStore.fetchModels();
});

const openAdd = () => {
  isEdit.value = false;
  formTitle.value = '添加 AI 模型';
  form.value = {
    id: 0,
    name: '',
    provider: 'DeepSeek',
    base_url: 'https://api.deepseek.com/v1',
    api_key: '',
    model_name: 'deepseek-chat',
    temperature: 0.3,
    system_prompt: '',
  };
  showForm.value = true;
};

const openEdit = (model: any) => {
  isEdit.value = true;
  formTitle.value = '编辑 AI 模型';
  form.value = {
    ...model,
    api_key: '', // Leave blank if not modifying
  };
  showForm.value = true;
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
    title: '确认删除',
    message: '确定要删除这个模型配置吗？历史预测记录仍会保留。',
  }).then(async () => {
    try {
      await aiModelsApi.remove(id);
      showToast({ type: 'success', message: '删除成功' });
      settingsStore.fetchModels();
    } catch (e) {
      // Handled by interceptor
    }
  }).catch(() => {});
};

const onTest = async (id: number) => {
  showToast({ type: 'loading', message: '正在测试AI模型连接...', duration: 0, forbidClick: true });
  try {
    const res: any = await aiModelsApi.test(id);
    showToast({
      type: 'success',
      message: `连接成功！预测: ${res.prediction || 'SKIP'} (${((res.confidence || 0) * 100).toFixed(0)}%)`
    });
  } catch (e: any) {
    // Error details shown by axios interceptor
  }
};
</script>

<template>
  <div class="settings-page">
    <div class="header">
      <h3 class="section-title">AI 模型配置 (支持多模型对比)</h3>
      <van-button type="primary" size="small" icon="plus" @click="openAdd">添加模型</van-button>
    </div>

    <div class="model-list" v-if="settingsStore.aiModels.length">
      <AIModelCard
        v-for="model in settingsStore.aiModels"
        :key="model.id"
        :model="model"
        @edit="openEdit"
        @delete="onDelete"
        @test="onTest"
      />
    </div>
    <van-empty v-else description="暂无已配置的AI模型，请点击右上角「添加模型」" image="search" />

    <van-popup v-model:show="showForm" position="bottom" :style="{ height: '85%' }" round>
      <div class="popup-header">{{ formTitle }}</div>
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            name="name"
            label="显示名称"
            placeholder="如: DeepSeek-V3"
            :rules="[{ required: true, message: '请输入模型名称' }]"
          />
          <van-field
            v-model="form.provider"
            name="provider"
            label="供应商"
            placeholder="如: DeepSeek / OpenAI / Claude"
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
            :placeholder="isEdit ? '留空表示保持原密钥不变' : '请输入 API 密钥'"
            :rules="isEdit ? [] : [{ required: true, message: '请输入 API 密钥' }]"
          />
          <van-field
            v-model="form.model_name"
            name="model_name"
            label="模型标识"
            placeholder="如: deepseek-chat / gpt-4o"
            :rules="[{ required: true, message: '请输入模型ID' }]"
          />
          
          <van-field name="temperature" label="随机度 (Temp)">
            <template #input>
              <van-slider v-model="form.temperature" :min="0" :max="1" :step="0.05" />
              <div style="margin-left: 10px; font-family: monospace">{{ form.temperature }}</div>
            </template>
          </van-field>

          <van-field
            v-model="form.system_prompt"
            rows="3"
            autosize
            label="自定义 Prompt"
            type="textarea"
            placeholder="留空则使用默认专业量化分析提示词"
          />
        </van-cell-group>
        
        <div style="margin: 20px 16px;">
          <van-button round block type="primary" native-type="submit">
            保存配置
          </van-button>
        </div>
      </van-form>
    </van-popup>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 10px;
  min-height: 100vh;
  background: #0f0f1a;
  padding-bottom: 70px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 6px 16px;
}
.section-title {
  font-size: 15px;
  padding-left: 10px;
  border-left: 4px solid #00c853;
  margin: 0;
  color: #e0e0e0;
}
.popup-header {
  text-align: center;
  font-size: 16px;
  font-weight: bold;
  padding: 18px;
  color: #323233;
}
:deep(.van-popup) {
  background: #fff;
}
:deep(.van-cell) {
  padding: 12px 16px;
}
</style>

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { aiModelsApi, settingsApi } from '../api';

export const useSettingsStore = defineStore('settings', () => {
  const aiModels = ref<any[]>([]);
  const systemSettings = ref<any>({});

  const fetchModels = async () => {
    try {
      const res: any = await aiModelsApi.getAll();
      aiModels.value = res;
    } catch (e) {
      console.error(e);
    }
  };

  const fetchSettings = async () => {
    try {
      const res: any = await settingsApi.get();
      systemSettings.value = res;
    } catch (e) {
      console.error(e);
    }
  };

  return {
    aiModels,
    systemSettings,
    fetchModels,
    fetchSettings,
  };
});

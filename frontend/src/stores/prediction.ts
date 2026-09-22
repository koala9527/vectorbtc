import { defineStore } from 'pinia';
import { ref } from 'vue';
import { predictionsApi } from '../api';

export const usePredictionStore = defineStore('prediction', () => {
  const latestPredictions = ref<any[]>([]);
  const history = ref<any[]>([]);
  const loading = ref(false);
  const finished = ref(false);
  const offset = ref(0);
  const pageSize = 20;

  const fetchLatest = async () => {
    try {
      const res: any = await predictionsApi.getLatest();
      latestPredictions.value = Array.isArray(res) ? res : [];
    } catch (e) {
      console.error('fetchLatest error:', e);
    }
  };

  const fetchHistory = async (modelId?: number, isRefresh = false): Promise<boolean> => {
    if (isRefresh) {
      offset.value = 0;
      finished.value = false;
    }
    
    loading.value = true;
    try {
      const params: any = { limit: pageSize, offset: offset.value };
      if (modelId) params.ai_model_id = modelId;
      
      const res: any = await predictionsApi.getList(params);
      const items = Array.isArray(res) ? res : [];
      
      if (isRefresh) {
        history.value = items;
      } else {
        history.value.push(...items);
      }
      
      if (items.length < pageSize) {
        finished.value = true;
      }
      offset.value += items.length;
      return finished.value;
    } catch (e) {
      console.error('fetchHistory error:', e);
      finished.value = true;
      return true;
    } finally {
      loading.value = false;
    }
  };

  const addLatest = (data: any) => {
    if (Array.isArray(data)) {
      latestPredictions.value = data;
    } else if (data && data.predictions && Array.isArray(data.predictions)) {
      latestPredictions.value = data.predictions;
    } else if (data && data.id) {
      latestPredictions.value = [data, ...latestPredictions.value.filter(p => p.id !== data.id)];
    }
  };

  const updateSettlement = (data: any) => {
    const idx = latestPredictions.value.findIndex(p => p.id === data.id);
    if (idx !== -1) {
      latestPredictions.value[idx] = { ...latestPredictions.value[idx], ...data };
    }
  };

  return {
    latestPredictions,
    history,
    loading,
    finished,
    fetchLatest,
    fetchHistory,
    addLatest,
    updateSettlement,
  };
});

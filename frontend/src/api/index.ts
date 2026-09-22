import axios from 'axios';
import { showToast } from 'vant';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    showToast(error.response?.data?.detail || '网络请求错误');
    return Promise.reject(error);
  }
);

export const marketApi = {
  getTicker: () => api.get('/market/ticker'),
  getKlines: (limit = 100) => api.get('/market/klines', { params: { limit } }),
  getIndicators: () => api.get('/market/indicators'),
};

export const predictionsApi = {
  getList: (params: any) => api.get('/predictions', { params }),
  getLatest: () => api.get('/predictions/latest'),
  trigger: () => api.post('/predictions/trigger'),
};

export const aiModelsApi = {
  getAll: () => api.get('/ai-models'),
  create: (data: any) => api.post('/ai-models', data),
  update: (id: number, data: any) => api.put(`/ai-models/${id}`, data),
  remove: (id: number) => api.delete(`/ai-models/${id}`),
  test: (id: number) => api.post(`/ai-models/${id}/test`),
};

export const statsApi = {
  getOverview: () => api.get('/stats/overview'),
  getByModel: () => api.get('/stats/by-model'),
  getHistory: (days = 7) => api.get('/stats/history', { params: { days } }),
};

export const settingsApi = {
  get: () => api.get('/settings'),
  update: (data: any) => api.put('/settings', data),
};

import { onMounted, onUnmounted, ref } from 'vue';
import { useMarketStore } from '../stores/market';
import { usePredictionStore } from '../stores/prediction';

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null);
  const isConnected = ref(false);
  const reconnectTimer = ref<number | null>(null);
  
  const marketStore = useMarketStore();
  const predictionStore = usePredictionStore();

  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    ws.value = new WebSocket(`${protocol}//${host}/ws`);

    ws.value.onopen = () => {
      isConnected.value = true;
      if (reconnectTimer.value) clearInterval(reconnectTimer.value);
    };

    ws.value.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'ticker') {
          marketStore.updateTicker(payload.data);
        } else if (payload.type === 'prediction') {
          predictionStore.addLatest(payload.data);
        } else if (payload.type === 'settlement') {
          predictionStore.updateSettlement(payload.data);
        }
      } catch (e) {
        console.error('WS parse error', e);
      }
    };

    ws.value.onclose = () => {
      isConnected.value = false;
      scheduleReconnect();
    };

    ws.value.onerror = () => {
      ws.value?.close();
    };
  };

  const scheduleReconnect = () => {
    if (!reconnectTimer.value) {
      reconnectTimer.value = window.setInterval(() => {
        if (!isConnected.value) connect();
      }, 5000);
    }
  };

  onMounted(() => {
    connect();
  });

  onUnmounted(() => {
    if (ws.value) {
      ws.value.close();
    }
    if (reconnectTimer.value) {
      clearInterval(reconnectTimer.value);
    }
  });

  return { isConnected };
}

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { marketApi } from '../api';

export const useMarketStore = defineStore('market', () => {
  const currentPrice = ref(0);
  const priceChange24h = ref('0');
  const priceChangePct24h = ref('0');
  const volume24h = ref('0');
  const high24h = ref('0');
  const low24h = ref('0');
  const klines = ref<any[]>([]);
  const indicators = ref<any>({});

  const fetchTicker = async () => {
    try {
      const res: any = await marketApi.getTicker();
      // Binance ticker/24hr returns these field names
      currentPrice.value = parseFloat(res.lastPrice || res.price || 0);
      priceChange24h.value = res.priceChange || '0';
      priceChangePct24h.value = res.priceChangePercent || '0';
      volume24h.value = res.quoteVolume || '0';
      high24h.value = res.highPrice || '0';
      low24h.value = res.lowPrice || '0';
    } catch (e) {
      console.error(e);
    }
  };

  const fetchKlines = async (limit = 100) => {
    try {
      const res: any = await marketApi.getKlines(limit);
      klines.value = res;
    } catch (e) {
      console.error(e);
    }
  };

  const fetchIndicators = async () => {
    try {
      const res: any = await marketApi.getIndicators();
      indicators.value = res;
    } catch (e) {
      console.error(e);
    }
  };

  const updateTicker = (data: any) => {
    if (data.price) currentPrice.value = parseFloat(data.price);
    if (data.change24h) priceChangePct24h.value = data.change24h;
    if (data.volume24h) volume24h.value = data.volume24h;
  };

  return {
    currentPrice,
    priceChange24h,
    priceChangePct24h,
    volume24h,
    high24h,
    low24h,
    klines,
    indicators,
    fetchTicker,
    fetchKlines,
    fetchIndicators,
    updateTicker,
  };
});

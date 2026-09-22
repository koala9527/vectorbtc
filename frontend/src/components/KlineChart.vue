<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue';
import { createChart, IChartApi, ISeriesApi, UTCTimestamp } from 'lightweight-charts';
import { useMarketStore } from '../stores/market';

const marketStore = useMarketStore();
const chartContainer = ref<HTMLElement | null>(null);
let chart: IChartApi | null = null;
let candlestickSeries: ISeriesApi<"Candlestick"> | null = null;
let volumeSeries: ISeriesApi<"Histogram"> | null = null;

const initChart = () => {
  if (!chartContainer.value) return;
  
  chart = createChart(chartContainer.value, {
    height: 280,
    layout: {
      background: { color: 'transparent' },
      textColor: '#8f9ca2',
    },
    grid: {
      vertLines: { color: 'rgba(42, 42, 62, 0.5)' },
      horzLines: { color: 'rgba(42, 42, 62, 0.5)' },
    },
    crosshair: {
      mode: 0,
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
      borderColor: '#2a2a3e',
    },
    rightPriceScale: {
      borderColor: '#2a2a3e',
    },
  });

  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#00c853',
    downColor: '#ff1744',
    borderVisible: false,
    wickUpColor: '#00c853',
    wickDownColor: '#ff1744',
  });

  volumeSeries = chart.addHistogramSeries({
    color: '#26a69a',
    priceFormat: {
      type: 'volume',
    },
    priceScaleId: '',
  });

  volumeSeries.priceScale().applyOptions({
    scaleMargins: {
      top: 0.8,
      bottom: 0,
    },
  });

  updateData();
  handleResize();
};

const updateData = () => {
  if (!candlestickSeries || !volumeSeries || !marketStore.klines.length) return;
  
  const timeSet = new Set<number>();
  const cData: any[] = [];
  const vData: any[] = [];

  for (const k of marketStore.klines) {
    let t: number;
    if (typeof k.timestamp === 'number') {
      t = Math.floor(k.timestamp / 1000);
    } else if (k.open_time) {
      t = Math.floor(new Date(k.open_time).getTime() / 1000);
    } else {
      continue;
    }

    if (timeSet.has(t)) continue;
    timeSet.add(t);

    const open = Number(k.open ?? k.open_price);
    const high = Number(k.high ?? k.high_price);
    const low = Number(k.low ?? k.low_price);
    const close = Number(k.close ?? k.close_price);
    const volume = Number(k.volume ?? 0);

    if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close)) continue;

    cData.push({
      time: t as UTCTimestamp,
      open,
      high,
      low,
      close,
    });

    vData.push({
      time: t as UTCTimestamp,
      value: volume,
      color: close >= open ? 'rgba(0, 200, 83, 0.4)' : 'rgba(255, 23, 68, 0.4)',
    });
  }

  // Sort ascending by time (strict lightweight-charts requirement)
  cData.sort((a, b) => a.time - b.time);
  vData.sort((a, b) => a.time - b.time);

  candlestickSeries.setData(cData);
  volumeSeries.setData(vData);
};

watch(() => marketStore.klines, updateData, { deep: true });

const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.applyOptions({ width: chartContainer.value.clientWidth });
  }
};

onMounted(() => {
  nextTick(() => {
    initChart();
    window.addEventListener('resize', handleResize);
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (chart) {
    chart.remove();
    chart = null;
  }
});
</script>

<template>
  <div class="kline-container" ref="chartContainer"></div>
</template>

<style scoped>
.kline-container {
  width: 100%;
  min-height: 280px;
  margin: 4px 0;
}
</style>

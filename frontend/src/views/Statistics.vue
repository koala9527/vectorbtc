<script setup lang="ts">
import { ref, onMounted } from 'vue';
import WinRateChart from '../components/WinRateChart.vue';
import { statsApi } from '../api';

const overview = ref<any>({});
const modelStats = ref<any[]>([]);
const historyData = ref<any[]>([]);
const loading = ref(false);

const fetchData = async () => {
  loading.value = true;
  try {
    const [oRes, mRes, hRes]: any = await Promise.all([
      statsApi.getOverview(),
      statsApi.getByModel(),
      statsApi.getHistory(7),
    ]);
    overview.value = oRes || {};
    modelStats.value = Array.isArray(mRes) ? mRes : [];
    historyData.value = Array.isArray(hRes) ? hRes : [];
  } catch (e) {
    console.error('Stats fetch error', e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<template>
  <div class="statistics-page">
    <!-- Top Branding Header -->
    <div class="stats-header">
      <div class="header-text">
        <h3 class="page-title">5M 周期量化胜率矩阵</h3>
        <span class="page-sub">统计各 AI 模型在 5 分钟级别 BTC 多空推演中的实战战绩</span>
      </div>
      <van-button size="mini" type="primary" plain round icon="replay" @click="fetchData">刷新</van-button>
    </div>

    <!-- Overview Metrics Grid -->
    <div class="overview-box">
      <div class="metric-card main-rate">
        <span class="m-label">全模型综合胜率 (5M)</span>
        <div class="m-val-wrap">
          <span class="m-val" :class="(overview.win_rate || 0) >= 50 ? 'good' : 'bad'">
            {{ overview.win_rate || 0 }}%
          </span>
        </div>
        <span class="m-sub">基准盈亏平衡线: 50.0%</span>
      </div>

      <div class="sub-metrics">
        <div class="metric-card">
          <span class="m-label">5M 总结算轮次</span>
          <span class="m-val font-mono">{{ overview.total_predictions || 0 }}</span>
        </div>
        <div class="metric-card">
          <span class="m-label">预测命中 (UP/DOWN)</span>
          <span class="m-val font-mono good">{{ overview.correct_predictions || 0 }}</span>
        </div>
        <div class="metric-card">
          <span class="m-label">预测偏差</span>
          <span class="m-val font-mono bad">{{ overview.wrong_predictions || 0 }}</span>
        </div>
        <div class="metric-card">
          <span class="m-label">观望避险 (SKIP)</span>
          <span class="m-val font-mono skip">{{ overview.skip_predictions || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- Model Comparison Chart -->
    <div class="chart-section" v-if="modelStats.length">
      <div class="sec-title-wrap">
        <h4 class="section-title">5M 各模型实盘胜率排行榜</h4>
        <span class="sec-tag">横向对比</span>
      </div>
      <div class="chart-box">
        <WinRateChart :data="modelStats" />
      </div>
    </div>

    <!-- Daily Trend -->
    <div class="history-section" v-if="historyData.length">
      <div class="sec-title-wrap">
        <h4 class="section-title">每日胜率表现追踪 (近7日)</h4>
        <span class="sec-tag">周期趋势</span>
      </div>
      <div class="history-list">
        <div v-for="h in historyData" :key="h.date" class="history-card">
          <div class="h-left">
            <span class="h-date font-mono">{{ h.date }}</span>
            <span class="h-stat">命中 {{ h.correct }} / 共 {{ h.total }} 轮 5M 预测</span>
          </div>
          <div class="h-right">
            <span class="h-rate font-mono" :class="h.win_rate >= 50 ? 'good' : 'bad'">
              {{ h.win_rate }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!modelStats.length && !historyData.length && !loading" class="empty-wrap">
      <van-empty description="暂无 5M 结算统计，请先在「行情」或设置中触发预测以积累胜率数据" image="search" />
    </div>
  </div>
</template>

<style scoped>
.statistics-page {
  padding: 12px;
  min-height: 100vh;
  background: #0a0b14;
  padding-bottom: 75px;
}
.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 6px 4px 14px;
}
.page-title {
  font-size: 16px;
  font-weight: 700;
  padding-left: 10px;
  border-left: 4px solid #00f090;
  color: #f0f2f5;
  margin: 0;
}
.page-sub {
  font-size: 11px;
  color: #7d889b;
  padding-left: 14px;
}
.overview-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
.metric-card {
  background: linear-gradient(145deg, #13172b 0%, #0d0f1e 100%);
  border-radius: 10px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.metric-card.main-rate {
  text-align: center;
  padding: 18px 14px;
  background: linear-gradient(135deg, #161c38 0%, #0d0f1e 100%);
  border: 1px solid rgba(0, 240, 144, 0.25);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}
.sub-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.m-label {
  font-size: 11px;
  color: #7d889b;
}
.m-val-wrap {
  margin: 4px 0;
}
.m-val {
  font-size: 22px;
  font-weight: 800;
  color: #f0f2f5;
}
.main-rate .m-val {
  font-size: 40px;
  letter-spacing: -1px;
}
.m-sub {
  font-size: 10px;
  color: #7d889b;
}
.good {
  color: #00f090 !important;
}
.bad {
  color: #ff3355 !important;
}
.skip {
  color: #f0b90b !important;
}
.font-mono {
  font-family: 'Courier New', Courier, monospace;
}
.sec-title-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 4px 8px;
}
.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #f0f2f5;
  margin: 0;
}
.sec-tag {
  font-size: 10px;
  color: #00f090;
  background: rgba(0, 240, 144, 0.1);
  padding: 1px 6px;
  border-radius: 4px;
}
.chart-box {
  background: #121424;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 10px;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.history-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #121424;
  border-radius: 8px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}
.h-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.h-date {
  font-size: 13px;
  font-weight: 600;
  color: #f0f2f5;
}
.h-stat {
  font-size: 11px;
  color: #7d889b;
}
.h-rate {
  font-size: 18px;
  font-weight: 800;
}
.empty-wrap {
  margin: 30px 4px;
  background: #121424;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 24px 0;
}
</style>

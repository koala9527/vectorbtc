<script setup lang="ts">
import { useWebSocket } from './composables/useWebSocket';

useWebSocket();
</script>

<template>
  <div class="app-container">
    <div class="main-content">
      <router-view />
    </div>
    <van-tabbar route safe-area-inset-bottom fixed>
      <van-tabbar-item replace to="/" icon="chart-trending-o">行情</van-tabbar-item>
      <van-tabbar-item replace to="/predictions" icon="bulb-o">预测</van-tabbar-item>
      <van-tabbar-item replace to="/statistics" icon="bar-chart-o">统计</van-tabbar-item>
      <van-tabbar-item replace to="/settings" icon="setting-o">设置</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0f0f1a;
}
.main-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 50px;
  -webkit-overflow-scrolling: touch;
}
:deep(.van-tabbar) {
  background-color: #1a1a2e;
  border-top: 1px solid #2a2a3e;
}
:deep(.van-tabbar-item) {
  color: #8f9ca2;
}
:deep(.van-tabbar-item--active) {
  background-color: transparent;
  color: #00c853;
}
</style>

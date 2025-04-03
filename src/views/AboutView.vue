<template>
  <div class="main-container">
    <HeaderContainer class="header" />
    <div class="content-container">
      <SidebarContainer class="sidebar" />
      <CanvasPlayer class="content" />
    </div>
  </div>
</template>
<script>
import HeaderContainer from '@/components/container/HeaderContainer.vue';
import SidebarContainer from '@/components/container/SidebarContainer.vue';
import CanvasPlayer from '@/components/container/CanvasPlayer.vue';

export default {
  name: 'AboutView',
  components: {
    HeaderContainer,
    SidebarContainer,
    CanvasPlayer
  }
}
</script>
<style>
/* 主体布局 */
.main-container {
  display: flex;
  flex-direction: column;
  width: 100vw;
  /* 容器宽度100%视口 */
  height: 100vh;
  /* 容器高度100%视口 */
}

/* 头部 */
.header {
  height: 70px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 1000;
}

/* 内容区域 */
.content-container {
  display: flex;
  flex: 1;
  height: calc(100vh - 70px);
  /* 减去 header 的高度 */
}

/* 左侧导航栏样式 */
.sidebar {
  width: 200px;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  /* 确保宽度不被压缩 */
  height: 100%;
  /* 高度填满父容器 */
}

.sidebar-item {
  flex: 1;
  /* 让每个 item 等高平分父容器 */
  display: flex;
  /* 确保内容居中 */
  align-items: center;
  justify-content: center;
  padding: 0;
  /* 移除 padding */
  color: #333;
  text-decoration: none;
  font-size: 16px;
  border-bottom: 1px solid #e0e0e0;
  /* 分隔线 */
  transition: background-color 0.3s ease, color 0.3s ease;
}

.sidebar-item:last-child {
  border-bottom: none;
  /* 去掉最后一项的分隔线 */
}

.sidebar-item:hover {
  background-color: #e6e8eb;
}

/* 选中状态 */
.sidebar-item.router-link-exact-active {
  background-color: rgb(39, 131, 229);
  /* 暗色强调 */
  color: #fff;
  /* 文字颜色变为白色 */
}

/* 主内容区域 */
.content {
  flex: 1;
  padding: 20px;
  min-width: 0;
  /* 防止内容撑开布局 */
}
</style>

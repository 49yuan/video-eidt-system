<template>
    <aside class="sidebar">
        <router-link to="/template-library" class="sidebar-item">生产模板</router-link>
        <router-link to="/video-generation" class="sidebar-item">视频生成</router-link>
        <router-link to="/library-management" class="sidebar-item">系统管理</router-link>
    </aside>
</template>
<script>
export default {
    name: 'SidebarContainer',
}
</script>
<style>
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
</style>
<template>
  <header class="header">
    <!-- 左侧系统图标和名称 -->
    <div class="header-left">
      <img id="project-icon" src="logoImage" alt="Logo" @click="goHome" />
      <h1 @click="goHome">短视频社交平台账号自动化运营系统</h1>
    </div>
    <!-- 右侧用户头像和名称 -->
    <div class="header-right" @click="toggleUserMenu">
      <el-icon>
        <User />
      </el-icon>
      <span class="user-name">用户名</span>
      <!-- 用户菜单 -->
      <div v-show="isUserMenuVisible" class="user-menu">
        <ul>
          <li @click="goToProfile">个人资料</li>
          <li @click="logout">退出登录</li>
        </ul>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'HeaderContainer',
  data() {
    return {
      logoImage: require('@/assets/logo.png'),
      isUserMenuVisible: false, // 控制用户菜单显示
      isLoading: false,
    };
  },
  methods: {
    goHome() {
      this.$router.push('/');
    },
    toggleUserMenu() {
      this.isUserMenuVisible = !this.isUserMenuVisible;
    },
    closeUserMenu() {
      this.isUserMenuVisible = false;
    },
    goToProfile() {
      // 跳转到个人资料页面
      this.$router.push('/profile');
    },
    logout() {
      // 执行退出登录操作
      console.log('用户已退出登录');
      // 可在此处清除用户相关数据并跳转到登录页面
      this.$router.push('/login');
    },
    handleClickOutside(event) {
      const headerRight = this.$el.querySelector('.header-right');
      if (!headerRight.contains(event.target)) {
        // 如果点击不在用户菜单内，则关闭菜单
        this.closeUserMenu();
      }
    },
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleClickOutside);
  },
};
</script>

<style>
html,
body {
  overflow: hidden;
  /* 禁止整个页面滚动 */
  height: 100%;
  /* 确保内容高度占满视窗 */
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  /* 改为 100%，避免溢出 */
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 顶部样式 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #ffffff;
  padding: 10px 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100vw;
  z-index: 1001;
  box-sizing: border-box;
  /* 包含 padding */
}

.header-left {
  display: flex;
  align-items: center;
}

#project-icon {
  height: 50px;
  margin-right: 10px;
}

.header h1 {
  font-size: 20px;
  color: rgb(39, 131, 229);
  margin: 0;
  cursor: pointer;
  white-space: nowrap;
  /* 防止标题换行 */
  overflow: hidden;
  /* 防止溢出 */
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  /* 为下拉菜单定位 */
  cursor: pointer;
}

.user-avatar {
  height: 40px;
  width: 40px;
  border-radius: 50%;
}

.user-name {
  font-size: 16px;
  color: #333;
  white-space: nowrap;
}

.user-menu {
  position: absolute;
  top: 60px;
  /* 调整为头像底部 */
  right: 0;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  overflow: hidden;
  z-index: 1000;
}

.user-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.user-menu li {
  padding: 10px 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.user-menu li:hover {
  background-color: #f0f0f0;
}
</style>

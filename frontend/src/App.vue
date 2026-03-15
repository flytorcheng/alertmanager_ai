<template>
  <div class="app-container">
    <el-container class="main-layout">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
        <div class="logo">
          <el-icon class="logo-icon"><Bell /></el-icon>
          <span v-show="!isCollapse" class="logo-text">AlertManager</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          background-color="transparent"
          text-color="#a0aec0"
          active-text-color="#00d4ff"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataBoard /></el-icon>
            <template #title>控制台</template>
          </el-menu-item>
          <el-menu-item index="/receivers">
            <el-icon><User /></el-icon>
            <template #title>接收人管理</template>
          </el-menu-item>
          <el-menu-item index="/alert-groups">
            <el-icon><Grid /></el-icon>
            <template #title>告警分组</template>
          </el-menu-item>
          <el-menu-item index="/alert-history">
            <el-icon><Clock /></el-icon>
            <template #title>告警历史</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-icon class="collapse-btn" @click="toggleSidebar">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </div>
          <div class="header-right">
            <el-badge :value="alertCount" :hidden="alertCount === 0" class="alert-badge">
              <el-button circle>
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isCollapse = ref(false)
const alertCount = ref(3)

const activeMenu = computed(() => route.path)

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style lang="scss" scoped>
.app-container {
  height: 100vh;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f4e 50%, #0d1033 100%);
}

.main-layout {
  height: 100%;
}

.sidebar {
  background: rgba(15, 20, 50, 0.8);
  border-right: 1px solid rgba(0, 212, 255, 0.2);
  transition: width 0.3s;
  backdrop-filter: blur(10px);

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid rgba(0, 212, 255, 0.1);

    .logo-icon {
      font-size: 28px;
      color: #00d4ff;
      animation: pulse 2s infinite;
    }

    .logo-text {
      margin-left: 10px;
      font-size: 18px;
      font-weight: 600;
      background: linear-gradient(90deg, #00d4ff, #00ff88);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: 2px;
    }
  }

  .sidebar-menu {
    border-right: none;

    .el-menu-item {
      margin: 8px 10px;
      border-radius: 8px;
      transition: all 0.3s;

      &:hover {
        background: rgba(0, 212, 255, 0.1) !important;
      }

      &.is-active {
        background: linear-gradient(90deg, rgba(0, 212, 255, 0.2), rgba(0, 255, 136, 0.1)) !important;
        border-left: 3px solid #00d4ff;
      }
    }
  }
}

.header {
  background: rgba(15, 20, 50, 0.6);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  backdrop-filter: blur(10px);

  .header-left {
    .collapse-btn {
      font-size: 20px;
      color: #a0aec0;
      cursor: pointer;
      transition: color 0.3s;

      &:hover {
        color: #00d4ff;
      }
    }
  }

  .header-right {
    .alert-badge {
      :deep(.el-badge__content) {
        background: #ff4757;
      }
    }

    .el-button {
      background: transparent;
      border-color: rgba(0, 212, 255, 0.3);
      color: #a0aec0;

      &:hover {
        border-color: #00d4ff;
        color: #00d4ff;
      }
    }
  }
}

.main-content {
  padding: 20px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(0, 212, 255, 0.3);
    border-radius: 3px;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
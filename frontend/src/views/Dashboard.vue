<template>
  <div class="dashboard-page fade-in">
    <div class="page-header">
      <h1 class="page-title">控制台</h1>
      <p class="page-subtitle">AlertManager Webhook 配置管理系统概览</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="tech-card stat-card">
          <el-icon class="stat-icon user-icon"><User /></el-icon>
          <div class="stat-value">{{ stats.receivers }}</div>
          <div class="stat-label">接收人总数</div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="tech-card stat-card">
          <el-icon class="stat-icon group-icon"><Grid /></el-icon>
          <div class="stat-value">{{ stats.alertGroups }}</div>
          <div class="stat-label">告警分组</div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="tech-card stat-card">
          <el-icon class="stat-icon firing-icon"><Warning /></el-icon>
          <div class="stat-value">{{ stats.firing }}</div>
          <div class="stat-label">告警中</div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="tech-card stat-card">
          <el-icon class="stat-icon resolved-icon"><CircleCheck /></el-icon>
          <div class="stat-value">{{ stats.resolved }}</div>
          <div class="stat-label">已恢复</div>
        </div>
      </el-col>
    </el-row>

    <!-- 最近告警 -->
    <div class="tech-card recent-alerts">
      <div class="card-header">
        <h3><el-icon><Clock /></el-icon> 最近告警</h3>
        <el-button type="primary" text @click="$router.push('/alert-history')">
          查看全部 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <el-table :data="recentAlerts" class="tech-table" stripe>
        <el-table-column prop="alert_name" label="告警名称" min-width="180">
          <template #default="{ row }">
            <span class="alert-name">{{ row.alert_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small" effect="dark">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'firing' ? 'danger' : 'success'" size="small">
              {{ row.status === 'firing' ? '告警中' : '已恢复' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fired_at" label="触发时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.fired_at) }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 快速操作 -->
    <div class="tech-card quick-actions">
      <div class="card-header">
        <h3><el-icon><Operation /></el-icon> 快速操作</h3>
      </div>
      <el-row :gutter="16">
        <el-col :xs="12" :sm="8" :md="6">
          <div class="action-item" @click="$router.push('/receivers')">
            <el-icon class="action-icon"><UserFilled /></el-icon>
            <span>添加接收人</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <div class="action-item" @click="$router.push('/alert-groups')">
            <el-icon class="action-icon"><Grid /></el-icon>
            <span>创建告警分组</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <div class="action-item" @click="$router.push('/alert-history')">
            <el-icon class="action-icon"><Document /></el-icon>
            <span>查看告警历史</span>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { alertHistoryApi, receiverApi, alertGroupApi } from '@/api/modules'

const stats = ref({
  receivers: 0,
  alertGroups: 0,
  firing: 0,
  resolved: 0
})

const recentAlerts = ref([])

const getSeverityType = (severity) => {
  const types = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return types[severity] || 'info'
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const fetchStats = async () => {
  try {
    const [receivers, alertGroups, history] = await Promise.all([
      receiverApi.getList(),
      alertGroupApi.getList(),
      alertHistoryApi.getList()
    ])

    stats.value.receivers = receivers.count || receivers.length || 0
    stats.value.alertGroups = alertGroups.count || alertGroups.length || 0

    const alerts = history.results || history || []
    stats.value.firing = alerts.filter(a => a.status === 'firing').length
    stats.value.resolved = alerts.filter(a => a.status === 'resolved').length
    recentAlerts.value = alerts.slice(0, 5)
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style lang="scss" scoped>
.dashboard-page {
  .stat-row {
    margin-bottom: 24px;
  }

  .stat-card {
    padding: 24px;
    position: relative;
    overflow: hidden;

    .stat-icon {
      position: absolute;
      right: 20px;
      top: 20px;
      font-size: 60px;
      opacity: 0.1;

      &.user-icon {
        color: #00d4ff;
      }
      &.group-icon {
        color: #00ff88;
      }
      &.firing-icon {
        color: #ff4757;
      }
      &.resolved-icon {
        color: #00ff88;
      }
    }

    .stat-value {
      font-size: 42px;
      font-weight: 700;
      background: linear-gradient(90deg, #00d4ff, #00ff88);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .stat-label {
      color: #a0aec0;
      font-size: 14px;
      margin-top: 8px;
    }
  }

  .recent-alerts {
    margin-bottom: 24px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid rgba(0, 212, 255, 0.1);

      h3 {
        color: #00d4ff;
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .alert-name {
      color: #e2e8f0;
      font-weight: 500;
    }
  }

  .quick-actions {
    .card-header {
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid rgba(0, 212, 255, 0.1);

      h3 {
        color: #00d4ff;
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .action-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px 16px;
      background: rgba(0, 212, 255, 0.05);
      border: 1px solid rgba(0, 212, 255, 0.15);
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: rgba(0, 212, 255, 0.1);
        border-color: rgba(0, 212, 255, 0.3);
        transform: translateY(-2px);
      }

      .action-icon {
        font-size: 32px;
        color: #00d4ff;
        margin-bottom: 12px;
      }

      span {
        color: #a0aec0;
        font-size: 14px;
      }
    }
  }
}
</style>
<template>
  <div class="alert-history-page fade-in">
    <div class="page-header">
      <h1 class="page-title">告警历史</h1>
      <p class="page-subtitle">查看历史告警记录和状态</p>
    </div>

    <!-- 筛选栏 -->
    <div class="action-bar">
      <div class="search-box">
        <el-input
          v-model="searchParams.alert_name"
          placeholder="搜索告警名称"
          clearable
          @clear="fetchAlertHistory"
          @keyup.enter="fetchAlertHistory"
          style="width: 200px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="searchParams.severity" placeholder="严重级别" clearable @change="fetchAlertHistory" style="width: 120px">
          <el-option label="Critical" value="critical" />
          <el-option label="Warning" value="warning" />
          <el-option label="Info" value="info" />
        </el-select>
        <el-select v-model="searchParams.status" placeholder="状态" clearable @change="fetchAlertHistory" style="width: 120px">
          <el-option label="告警中" value="firing" />
          <el-option label="已恢复" value="resolved" />
        </el-select>
      </div>
      <div class="action-buttons">
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>

    <!-- 告警列表 -->
    <div class="tech-card">
      <el-table :data="alertHistory" v-loading="loading" class="tech-table" stripe>
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <div class="detail-item">
                <label>告警信息:</label>
                <p>{{ row.message || '暂无详细信息' }}</p>
              </div>
              <div class="detail-item" v-if="row.labels && Object.keys(row.labels).length > 0">
                <label>标签:</label>
                <div class="labels-list">
                  <el-tag
                    v-for="(value, key) in row.labels"
                    :key="key"
                    size="small"
                    class="label-tag"
                  >
                    {{ key }}: {{ value }}
                  </el-tag>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="alert_name" label="告警名称" min-width="200">
          <template #default="{ row }">
            <div class="alert-name-cell">
              <el-icon class="alert-icon" :class="row.status">
                <Warning v-if="row.status === 'firing'" />
                <CircleCheck v-else />
              </el-icon>
              <span class="name">{{ row.alert_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重级别" width="120">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small" effect="dark" class="severity-tag">
              {{ row.severity?.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'firing' ? 'danger' : 'success'"
              size="small"
              effect="dark"
              class="status-tag"
            >
              {{ row.status === 'firing' ? '告警中' : '已恢复' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_group_name" label="告警分组" width="150">
          <template #default="{ row }">
            <span class="group-name">{{ row.alert_group_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="fired_at" label="触发时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.fired_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="resolved_at" label="恢复时间" width="180">
          <template #default="{ row }">
            <span :class="{ 'not-resolved': !row.resolved_at }">
              {{ row.resolved_at ? formatTime(row.resolved_at) : '未恢复' }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchAlertHistory"
          @current-change="fetchAlertHistory"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { alertHistoryApi } from '@/api/modules'

const loading = ref(false)
const alertHistory = ref([])

const searchParams = reactive({
  alert_name: '',
  severity: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

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

const fetchAlertHistory = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchParams
    }
    const res = await alertHistoryApi.getList(params)
    alertHistory.value = res.results || res
    pagination.total = res.count || alertHistory.value.length
  } catch (error) {
    console.error('Failed to fetch alert history:', error)
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  Object.assign(searchParams, {
    alert_name: '',
    severity: '',
    status: ''
  })
  pagination.page = 1
  fetchAlertHistory()
}

onMounted(() => {
  fetchAlertHistory()
})
</script>

<style lang="scss" scoped>
.alert-history-page {
  .alert-name-cell {
    display: flex;
    align-items: center;
    gap: 10px;

    .alert-icon {
      font-size: 18px;

      &.firing {
        color: #ff4757;
        animation: blink 1s infinite;
      }

      &.resolved {
        color: #00ff88;
      }
    }

    .name {
      color: #e2e8f0;
      font-weight: 500;
    }
  }

  .severity-tag {
    font-weight: 600;
    letter-spacing: 1px;
  }

  .status-tag {
    min-width: 60px;
    text-align: center;
  }

  .group-name {
    color: #a0aec0;
  }

  .not-resolved {
    color: #ff4757;
    font-style: italic;
  }

  .expand-content {
    padding: 16px 20px;
    background: rgba(0, 212, 255, 0.03);

    .detail-item {
      margin-bottom: 12px;

      label {
        color: #00d4ff;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
        display: block;
      }

      p {
        color: #a0aec0;
        line-height: 1.6;
        margin: 0;
      }

      .labels-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .label-tag {
          background: rgba(0, 212, 255, 0.15);
          border-color: rgba(0, 212, 255, 0.3);
          color: #00d4ff;
        }
      }
    }
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;

    :deep(.el-pagination) {
      .el-pagination__total,
      .el-pagination__sizes,
      .el-pagination__jump {
        color: #a0aec0;
      }

      .el-pager li {
        background: transparent;
        color: #a0aec0;

        &.is-active {
          background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 255, 136, 0.1));
          color: #00d4ff;
        }
      }

      button {
        background: transparent;
        color: #a0aec0;
      }
    }
  }
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
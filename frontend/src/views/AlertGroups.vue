<template>
  <div class="alert-groups-page fade-in">
    <div class="page-header">
      <h1 class="page-title">告警分组</h1>
      <p class="page-subtitle">配置告警分组规则，关联接收人实现精准告警通知</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="search-box">
        <el-input
          v-model="searchParams.name"
          placeholder="搜索分组名称"
          clearable
          @clear="fetchAlertGroups"
          @keyup.enter="fetchAlertGroups"
          style="width: 200px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          创建分组
        </el-button>
      </div>
    </div>

    <!-- 分组列表 -->
    <el-row :gutter="20" class="groups-grid">
      <el-col :xs="24" :sm="12" :lg="8" v-for="group in alertGroups" :key="group.id">
        <div class="tech-card group-card">
          <div class="card-header">
            <div class="header-left">
              <el-icon class="group-icon"><Grid /></el-icon>
              <h3 class="group-name">{{ group.name }}</h3>
            </div>
            <el-switch
              v-model="group.is_active"
              @change="toggleActive(group)"
              active-color="#00ff88"
              inactive-color="#4a5568"
            />
          </div>
          <p class="group-desc">{{ group.description || '暂无描述' }}</p>

          <!-- 匹配规则 -->
          <div class="rules-section">
            <h4><el-icon><Setting /></el-icon> 匹配规则</h4>
            <div class="rules-content">
              <template v-if="group.match_rules && Object.keys(group.match_rules).length > 0">
                <el-tag
                  v-for="(value, key) in group.match_rules"
                  :key="key"
                  size="small"
                  class="rule-tag"
                >
                  {{ key }}: {{ value }}
                </el-tag>
              </template>
              <span v-else class="no-rules">暂无匹配规则</span>
            </div>
          </div>

          <!-- 接收人 -->
          <div class="receivers-section">
            <h4><el-icon><User /></el-icon> 接收人 ({{ group.receiver_count || 0 }})</h4>
            <div class="receivers-avatars">
              <template v-if="group.receiver_names && group.receiver_names.length > 0">
                <el-avatar
                  v-for="(name, index) in group.receiver_names.slice(0, 5)"
                  :key="index"
                  :size="28"
                  class="avatar"
                >
                  {{ name?.charAt(0) }}
                </el-avatar>
                <span v-if="group.receiver_names.length > 5" class="more-count">
                  +{{ group.receiver_names.length - 5 }}
                </span>
              </template>
              <span v-else class="no-receivers">暂无接收人</span>
            </div>
          </div>

          <div class="card-footer">
            <span class="time">{{ formatTime(group.updated_at) }}</span>
            <div class="actions">
              <el-button type="primary" text size="small" @click="openDialog(group)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" text size="small" @click="deleteGroup(group)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && alertGroups.length === 0" description="暂无告警分组">
      <el-button type="primary" @click="openDialog()">创建第一个分组</el-button>
    </el-empty>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingGroup ? '编辑告警分组' : '创建告警分组'"
      width="600px"
      class="tech-dialog"
      destroy-on-close
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px" class="tech-form">
        <el-form-item label="分组名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入分组名称" />
        </el-form-item>
        <el-form-item label="分组描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="请输入分组描述（选填）" />
        </el-form-item>

        <!-- 匹配规则 -->
        <el-form-item label="匹配规则">
          <div class="rules-editor">
            <div v-for="(rule, index) in matchRules" :key="index" class="rule-item">
              <el-input v-model="rule.key" placeholder="标签名" style="width: 150px" />
              <span class="separator">=</span>
              <el-input v-model="rule.value" placeholder="标签值" style="width: 150px" />
              <el-button type="danger" text @click="removeRule(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" text @click="addRule">
              <el-icon><Plus /></el-icon>
              添加规则
            </el-button>
          </div>
        </el-form-item>

        <!-- 接收人选择 -->
        <el-form-item label="接收人" prop="receiver_ids">
          <el-select
            v-model="formData.receiver_ids"
            multiple
            filterable
            placeholder="请选择接收人"
            style="width: 100%"
          >
            <el-option
              v-for="receiver in allReceivers"
              :key="receiver.id"
              :label="receiver.name"
              :value="receiver.id"
            >
              <span>{{ receiver.name }}</span>
              <el-tag size="small" :type="getTypeTag(receiver.receive_type)" style="margin-left: 8px">
                {{ receiver.receive_type_display }}
              </el-tag>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="formData.is_active" active-color="#00ff88" inactive-color="#4a5568" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { alertGroupApi, receiverApi } from '@/api/modules'

const loading = ref(false)
const alertGroups = ref([])
const allReceivers = ref([])
const dialogVisible = ref(false)
const editingGroup = ref(null)
const formRef = ref(null)

const searchParams = reactive({
  name: ''
})

const matchRules = ref([])

const formData = reactive({
  name: '',
  description: '',
  match_rules: {},
  receiver_ids: [],
  is_active: true
})

const formRules = {
  name: [{ required: true, message: '请输入分组名称', trigger: 'blur' }]
}

const getTypeTag = (type) => {
  const types = {
    email: 'primary',
    webhook: 'success',
    dingtalk: 'warning',
    wechat: 'success',
    slack: 'info'
  }
  return types[type] || 'info'
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const fetchAlertGroups = async () => {
  loading.value = true
  try {
    const res = await alertGroupApi.getList(searchParams)
    alertGroups.value = res.results || res
  } catch (error) {
    console.error('Failed to fetch alert groups:', error)
  } finally {
    loading.value = false
  }
}

const fetchReceivers = async () => {
  try {
    const res = await receiverApi.getList({ page_size: 1000 })
    allReceivers.value = res.results || res
  } catch (error) {
    console.error('Failed to fetch receivers:', error)
  }
}

const openDialog = (group = null) => {
  editingGroup.value = group
  if (group) {
    formData.name = group.name
    formData.description = group.description || ''
    formData.match_rules = group.match_rules || {}
    formData.receiver_ids = group.receivers?.map(r => r.id) || []
    formData.is_active = group.is_active

    // 转换匹配规则为数组
    matchRules.value = Object.entries(group.match_rules || {}).map(([key, value]) => ({ key, value }))
  } else {
    Object.assign(formData, {
      name: '',
      description: '',
      match_rules: {},
      receiver_ids: [],
      is_active: true
    })
    matchRules.value = []
  }
  dialogVisible.value = true
}

const addRule = () => {
  matchRules.value.push({ key: '', value: '' })
}

const removeRule = (index) => {
  matchRules.value.splice(index, 1)
}

const submitForm = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // 转换匹配规则为对象
  formData.match_rules = {}
  matchRules.value.forEach(rule => {
    if (rule.key && rule.value) {
      formData.match_rules[rule.key] = rule.value
    }
  })

  try {
    if (editingGroup.value) {
      await alertGroupApi.update(editingGroup.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await alertGroupApi.create(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchAlertGroups()
  } catch (error) {
    console.error('Failed to save alert group:', error)
  }
}

const toggleActive = async (group) => {
  try {
    await alertGroupApi.toggleActive(group.id)
    ElMessage.success(group.is_active ? '已启用' : '已禁用')
  } catch (error) {
    group.is_active = !group.is_active
  }
}

const deleteGroup = async (group) => {
  try {
    await ElMessageBox.confirm('确定要删除该告警分组吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await alertGroupApi.delete(group.id)
    ElMessage.success('删除成功')
    fetchAlertGroups()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete alert group:', error)
    }
  }
}

onMounted(() => {
  fetchAlertGroups()
  fetchReceivers()
})
</script>

<style lang="scss" scoped>
.alert-groups-page {
  .groups-grid {
    margin-bottom: 20px;
  }

  .group-card {
    padding: 20px;
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      .header-left {
        display: flex;
        align-items: center;
        gap: 10px;

        .group-icon {
          font-size: 20px;
          color: #00d4ff;
        }

        .group-name {
          font-size: 16px;
          font-weight: 600;
          color: #e2e8f0;
          margin: 0;
        }
      }
    }

    .group-desc {
      color: #a0aec0;
      font-size: 13px;
      margin-bottom: 16px;
      line-height: 1.5;
    }

    .rules-section,
    .receivers-section {
      margin-bottom: 16px;

      h4 {
        font-size: 12px;
        color: #00d4ff;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
        text-transform: uppercase;
        letter-spacing: 1px;
      }
    }

    .rules-content {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .rule-tag {
        background: rgba(0, 212, 255, 0.15);
        border-color: rgba(0, 212, 255, 0.3);
        color: #00d4ff;
      }

      .no-rules {
        color: #6b7280;
        font-size: 12px;
      }
    }

    .receivers-avatars {
      display: flex;
      align-items: center;
      gap: 6px;

      .avatar {
        background: linear-gradient(135deg, #00d4ff, #00ff88);
        color: #0a0e27;
        font-size: 11px;
        font-weight: 600;
      }

      .more-count {
        font-size: 12px;
        color: #a0aec0;
        margin-left: 4px;
      }

      .no-receivers {
        color: #6b7280;
        font-size: 12px;
      }
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 16px;
      border-top: 1px solid rgba(0, 212, 255, 0.1);

      .time {
        font-size: 12px;
        color: #6b7280;
      }

      .actions {
        display: flex;
        gap: 4px;
      }
    }
  }

  .rules-editor {
    .rule-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;

      .separator {
        color: #00d4ff;
        font-weight: 600;
      }
    }
  }
}
</style>
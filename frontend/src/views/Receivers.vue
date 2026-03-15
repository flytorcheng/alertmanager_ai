<template>
  <div class="receivers-page fade-in">
    <div class="page-header">
      <h1 class="page-title">接收人管理</h1>
      <p class="page-subtitle">管理告警接收人的联系方式和通知方式</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="search-box">
        <el-input
          v-model="searchParams.name"
          placeholder="搜索接收人"
          clearable
          @clear="fetchReceivers"
          @keyup.enter="fetchReceivers"
          style="width: 200px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="searchParams.receive_type" placeholder="接收方式" clearable @change="fetchReceivers" style="width: 140px">
          <el-option label="邮件" value="email" />
          <el-option label="Webhook" value="webhook" />
          <el-option label="钉钉" value="dingtalk" />
          <el-option label="企业微信" value="wechat" />
          <el-option label="Slack" value="slack" />
        </el-select>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          添加接收人
        </el-button>
      </div>
    </div>

    <!-- 接收人列表 -->
    <div class="tech-card">
      <el-table :data="receivers" v-loading="loading" class="tech-table" stripe>
        <el-table-column prop="name" label="姓名" min-width="120">
          <template #default="{ row }">
            <div class="name-cell">
              <el-avatar :size="32" class="avatar">{{ row.name?.charAt(0) }}</el-avatar>
              <span class="name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="receive_type_display" label="接收方式" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.receive_type)" size="small">
              {{ row.receive_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180">
          <template #default="{ row }">
            <span class="contact-info">{{ row.email || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="140">
          <template #default="{ row }">
            <span class="contact-info">{{ row.phone || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="toggleActive(row)"
              active-color="#00ff88"
              inactive-color="#4a5568"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="openDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" text size="small" @click="deleteReceiver(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
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
          @size-change="fetchReceivers"
          @current-change="fetchReceivers"
        />
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingReceiver ? '编辑接收人' : '添加接收人'"
      width="500px"
      class="tech-dialog"
      destroy-on-close
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px" class="tech-form">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="接收方式" prop="receive_type">
          <el-select v-model="formData.receive_type" placeholder="请选择接收方式" style="width: 100%">
            <el-option label="邮件" value="email" />
            <el-option label="Webhook" value="webhook" />
            <el-option label="钉钉" value="dingtalk" />
            <el-option label="企业微信" value="wechat" />
            <el-option label="Slack" value="slack" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.receive_type === 'email'" label="邮箱地址" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item v-if="['webhook', 'dingtalk', 'wechat', 'slack'].includes(formData.receive_type)" label="Webhook地址" prop="webhook_url">
          <el-input v-model="formData.webhook_url" placeholder="请输入Webhook地址" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入手机号（选填）" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注信息（选填）" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { receiverApi } from '@/api/modules'

const loading = ref(false)
const receivers = ref([])
const dialogVisible = ref(false)
const editingReceiver = ref(null)
const formRef = ref(null)

const searchParams = reactive({
  name: '',
  receive_type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  name: '',
  receive_type: 'email',
  email: '',
  webhook_url: '',
  phone: '',
  remark: '',
  is_active: true
})

const formRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  receive_type: [{ required: true, message: '请选择接收方式', trigger: 'change' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }]
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

const fetchReceivers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchParams
    }
    const res = await receiverApi.getList(params)
    receivers.value = res.results || res
    pagination.total = res.count || receivers.value.length
  } catch (error) {
    console.error('Failed to fetch receivers:', error)
  } finally {
    loading.value = false
  }
}

const openDialog = (receiver = null) => {
  editingReceiver.value = receiver
  if (receiver) {
    Object.assign(formData, receiver)
  } else {
    Object.assign(formData, {
      name: '',
      receive_type: 'email',
      email: '',
      webhook_url: '',
      phone: '',
      remark: '',
      is_active: true
    })
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (editingReceiver.value) {
      await receiverApi.update(editingReceiver.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await receiverApi.create(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchReceivers()
  } catch (error) {
    console.error('Failed to save receiver:', error)
  }
}

const toggleActive = async (receiver) => {
  try {
    await receiverApi.toggleActive(receiver.id)
    ElMessage.success(receiver.is_active ? '已启用' : '已禁用')
  } catch (error) {
    receiver.is_active = !receiver.is_active
  }
}

const deleteReceiver = async (receiver) => {
  try {
    await ElMessageBox.confirm('确定要删除该接收人吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await receiverApi.delete(receiver.id)
    ElMessage.success('删除成功')
    fetchReceivers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete receiver:', error)
    }
  }
}

onMounted(() => {
  fetchReceivers()
})
</script>

<style lang="scss" scoped>
.receivers-page {
  .name-cell {
    display: flex;
    align-items: center;
    gap: 12px;

    .avatar {
      background: linear-gradient(135deg, #00d4ff, #00ff88);
      color: #0a0e27;
      font-weight: 600;
    }

    .name {
      color: #e2e8f0;
      font-weight: 500;
    }
  }

  .contact-info {
    color: #a0aec0;
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
</style>
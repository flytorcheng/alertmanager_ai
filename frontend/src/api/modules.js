import api from './index'

// 接收人相关API
export const receiverApi = {
  // 获取接收人列表
  getList(params = {}) {
    return api.get('/receivers/', { params })
  },

  // 获取单个接收人
  get(id) {
    return api.get(`/receivers/${id}/`)
  },

  // 创建接收人
  create(data) {
    return api.post('/receivers/', data)
  },

  // 更新接收人
  update(id, data) {
    return api.put(`/receivers/${id}/`, data)
  },

  // 删除接收人
  delete(id) {
    return api.delete(`/receivers/${id}/`)
  },

  // 切换激活状态
  toggleActive(id) {
    return api.post(`/receivers/${id}/toggle_active/`)
  }
}

// 告警分组相关API
export const alertGroupApi = {
  // 获取分组列表
  getList(params = {}) {
    return api.get('/alert-groups/', { params })
  },

  // 获取单个分组
  get(id) {
    return api.get(`/alert-groups/${id}/`)
  },

  // 创建分组
  create(data) {
    return api.post('/alert-groups/', data)
  },

  // 更新分组
  update(id, data) {
    return api.put(`/alert-groups/${id}/`, data)
  },

  // 删除分组
  delete(id) {
    return api.delete(`/alert-groups/${id}/`)
  },

  // 切换激活状态
  toggleActive(id) {
    return api.post(`/alert-groups/${id}/toggle_active/`)
  },

  // 获取分组的接收人
  getReceivers(id) {
    return api.get(`/alert-groups/${id}/receivers/`)
  },

  // 更新分组的接收人
  updateReceivers(id, receiverIds) {
    return api.post(`/alert-groups/${id}/receivers/`, { receiver_ids: receiverIds })
  }
}

// 告警历史相关API
export const alertHistoryApi = {
  // 获取告警历史列表
  getList(params = {}) {
    return api.get('/alert-history/', { params })
  },

  // 获取单个告警详情
  get(id) {
    return api.get(`/alert-history/${id}/`)
  }
}
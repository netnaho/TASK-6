<template>
  <div class="page-shell">
    <PageHeader eyebrow="USER MANAGEMENT" title="Accounts and access control" description="Create reviewer or administrator accounts, disable users, and perform offline password resets with forced change at next sign-in." />
    <div class="responsive-two">
      <n-card class="section-card" title="Create account">
        <n-form :model="form" label-placement="top">
          <div class="responsive-two">
            <n-form-item label="Full name"><n-input v-model:value="form.full_name" /></n-form-item>
            <n-form-item label="Username"><n-input v-model:value="form.username" /></n-form-item>
          </div>
          <div class="responsive-two">
            <n-form-item label="Role"><n-select v-model:value="form.role" :options="roleOptions" /></n-form-item>
            <n-form-item label="Temporary password"><n-input v-model:value="form.password" type="password" /></n-form-item>
          </div>
          <n-button type="primary" @click="createUser">Create user</n-button>
        </n-form>
      </n-card>
      <n-card class="section-card" title="Current users">
        <n-data-table :columns="columns" :data="users" :bordered="false" />
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, reactive, ref } from 'vue'
import { NButton, NCard, NDataTable, NForm, NFormItem, NInput, NPopconfirm, NSelect, useMessage } from 'naive-ui'

import { adminApi } from '@/api/admin'
import { extractApiError } from '@/api/client'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const message = useMessage()
const users = ref<any[]>([])
const form = reactive({ full_name: '', username: '', role: 'reviewer', password: 'NewPassword#2026' })
const roleOptions = [
  { label: 'Reviewer', value: 'reviewer' },
  { label: 'Administrator', value: 'administrator' },
]

async function load() {
  users.value = await adminApi.users()
}

async function createUser() {
  try {
    await adminApi.createUser(form)
    message.success('User created.')
    await load()
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function toggleDisable(user: any) {
  try {
    await adminApi.updateUser(user.id, { status: user.status === 'disabled' ? 'active' : 'disabled', is_active: user.status === 'disabled' })
    message.success('User status updated.')
    await load()
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function resetPassword(user: any) {
  try {
    await adminApi.resetPassword(user.id, { new_password: 'ResetPass#2026' })
    message.success(`Password reset for ${user.username}.`)
  } catch (error) {
    message.error(extractApiError(error))
  }
}

const columns = [
  { title: 'Username', key: 'username' },
  { title: 'Role', key: 'role' },
  { title: 'Status', key: 'status', render: (row: any) => h(StatusBadge, { status: row.status }) },
  {
    title: 'Actions',
    key: 'actions',
    render: (row: any) => h('div', { style: 'display:flex; gap:8px; flex-wrap:wrap;' }, [
      h(NButton, { size: 'small', secondary: true, onClick: () => resetPassword(row) }, { default: () => 'Reset password' }),
      h(NButton, { size: 'small', type: row.status === 'disabled' ? 'success' : 'warning', onClick: () => toggleDisable(row) }, { default: () => row.status === 'disabled' ? 'Enable' : 'Disable' }),
    ]),
  },
]

onMounted(() => load().catch((error) => message.error(extractApiError(error))))
</script>

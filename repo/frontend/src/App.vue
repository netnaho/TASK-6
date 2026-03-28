<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-dialog-provider>
      <n-notification-provider>
        <n-message-provider>
          <n-loading-bar-provider>
            <router-view />
          </n-loading-bar-provider>
        </n-message-provider>
      </n-notification-provider>
    </n-dialog-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { NConfigProvider, NDialogProvider, NLoadingBarProvider, NMessageProvider, NNotificationProvider, type GlobalThemeOverrides } from 'naive-ui'

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#1e5eff',
    primaryColorHover: '#346eff',
    primaryColorPressed: '#184ecc',
    successColor: '#0f9f6e',
    warningColor: '#d97706',
    errorColor: '#cf2d4f',
    borderRadius: '16px',
    fontFamily: `'Satoshi', 'Avenir Next', 'Segoe UI', sans-serif`,
  },
  Card: {
    borderRadius: '22px',
  },
  Button: {
    borderRadiusMedium: '14px',
  },
  Input: {
    borderRadius: '14px',
  },
}
</script>

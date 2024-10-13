<template>
  <MetaSeoLayout>
    <NuxtLayout class="w-full overflow-x-hidden min-h-screen overflow-y-auto text-base-content">
      <NuxtLoadingIndicator />
      <NuxtPage />
    </NuxtLayout>
  </MetaSeoLayout>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import MetaSeoLayout from '~/layouts/MetaSeoLayout.vue'

export default defineComponent({
  components: { MetaSeoLayout },
})
</script>

<style>
html {
  font-size: 16px;
}
</style>

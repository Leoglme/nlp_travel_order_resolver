<template>
  <div class="relative md:grid md:grid-cols-[500px,1fr] h-[calc(100vh-72px)]">
    <div
        v-if="mapIsLoading"
        class="absolute inset-0 z-20 flex items-center justify-center"
    >
      <i class="animate-spin text-4xl text-secondary-700 fas fa-spinner"></i>
    </div>

    <!-- Map Div -->
    <div
        v-show="!mapIsLoading"
        class="absolute inset-0 md:relative"
    >
      <MapBox :is-loading="mapIsLoading" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import MapBox from '~/components/navigations/MapBox.vue'

const mapIsLoading = ref(true)

setTimeout(() => {
  mapIsLoading.value = false
}, 2000)
</script>

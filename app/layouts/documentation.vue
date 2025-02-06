<template>
  <Body class="bg-slate-100 overflow-y-hidden">
    <EpiNavbar />
    <div class="grid grid-cols-[240px,1fr]">
      <DocumentationSidebar />
      <div ref="scrollContainer" class="px-8 py-6 h-[calc(100vh-125px)] overflow-y-auto">
        <slot />
      </div>
    </div>
  </Body>
</template>

<script setup lang="ts">
import 'notyf/notyf.min.css'
import EpiNavbar from '~/components/navigations/EpiNavbar.vue'
import DocumentationSidebar from "~/components/navigations/DocumentationSidebar.vue";
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const scrollContainer = ref<HTMLElement | null>(null)

watch(() => route.fullPath, () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTo({ top: 0, behavior: 'smooth' })
  }
}, { immediate: true })
</script>
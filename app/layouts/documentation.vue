<template>
  <Body class="bg-slate-100 overflow-y-hidden">
  <EpiNavbar />
   <div class="grid grid-cols-[240px,1fr]">
     <DocumentationSidebar />
     <slot />
   </div>
  </Body>
</template>
<script setup lang="ts">
import 'notyf/notyf.min.css'
import EpiNavbar from '~/components/navigations/EpiNavbar.vue'
import DocumentationSidebar from "~/components/navigations/DocumentationSidebar.vue";
</script>

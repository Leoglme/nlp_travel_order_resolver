<template>
  <Body class="bg-slate-100">
  <EpiNavbar />
  <slot />
  </Body>
</template>
<script setup lang="ts">
import EpiNavbar from '~/components/navigations/EpiNavbar.vue'
import 'notyf/notyf.min.css'
</script>

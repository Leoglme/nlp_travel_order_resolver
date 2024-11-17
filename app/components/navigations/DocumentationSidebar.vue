<template>
  <aside
      class="block h-screen max-h-screen pt-5 pb-3 px-3 overflow-scroll bg-white z-20">
    <div class="absolute inset-0 flex items-center justify-end w-full h-full">
      <div class="fixed top-[10px] w-px h-full bg-neutral-200"></div>
    </div>
    <h4 class="relative px-2 py-1 mb-2 text-sm font-semibold rounded-md">Getting Started</h4>
    <div class="relative grid grid-flow-row text-sm mb-7 auto-rows-max">
      <a href="/pines/docs/introduction"
         :class="{ 'bg-gray-100 border-gray-200/60' : activeMenuItem == 'introduction', 'hover:underline border-transparent' : activeMenuItem != 'introduction' }"
         class="group flex w-full items-center rounded-md border px-2 py-1.5 hover:underline border-transparent">
        Introduction
      </a>
      <a href="/pines/docs/how-to-use" :class="{ 'bg-gray-100 border-gray-200/60' : activeMenuItem == 'how-to-use', 'hover:underline border-transparent' : activeMenuItem != 'how-to-use' }"
         class="group flex w-full items-center rounded-md border px-2 py-1.5 hover:underline border-transparent">
        How to Use
      </a>
    </div>
  </aside>
</template>


<script lang="ts" setup>
const activeMenuItem = ref('introduction')
</script>

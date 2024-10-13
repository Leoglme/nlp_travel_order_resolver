<template>
  <header
      :class="isTop ? 'relative' : 'fixed md:sticky top-0 w-full'"
      class="z-50"
  >
    <nav
        :class="isTop ? 'border-b top-0 sticky' : 'w-full md:w-auto md:border md:rounded-lg md:absolute md:top-4'"
        class="bg-white z-20 transition-all duration-300 ease-in-out border-b border-zinc-300 backdrop-blur-[20px] flex-row gap-4 lg:gap-0 lg:flex-row flex items-center justify-between lg:h-[72px] box-border mx-auto my-0 p-3 inset-x-4"
    >
      <div class="flex-1 justify-center flex items-center">
        <EpiLogo large />
      </div>
    </nav>
  </header>
</template>
<script lang="ts" setup>
import { onMounted, onUnmounted, ref } from 'vue'
import type { Ref } from 'vue'
import EpiLogo from '~/components/ui/EpiLogo.vue'

/* REFS */
const isTop: Ref<boolean> = ref(true)

/* METHODS */

const handleScroll = (): void => {
  isTop.value = window.scrollY <= 50
}

/* LIFECYCLE */
onMounted((): void => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted((): void => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
@keyframes fadeIn {
  0% {
    opacity: 0;
    transform: rotateX(-25deg);
  }
  100% {
    opacity: 1;
    transform: rotateX(0deg);
  }
}

.animate-fadeIn {
  animation: 0.25s ease 0s 1 normal none running fadeIn;
}
</style>

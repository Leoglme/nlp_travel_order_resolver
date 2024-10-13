<template>
  <i
      v-if="props.name"
      class="fa-solid"
      :class="props.name"
  />
</template>

<script lang="ts" setup>
/* PROPS */
const props = defineProps({
  name: {
    type: String,
    default: null,
  },
})
</script>

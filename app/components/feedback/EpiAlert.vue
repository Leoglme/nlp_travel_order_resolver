<template>
  <div v-if="props.message" class="flex items-center p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
    <EpiIcon v-if="props.icon" :name="props.icon" class="mr-3 text-red-600" />
    <span class="flex-1">{{ props.message }}</span>
    <button
        v-if="props.dismissible"
        @click="clearAlert"
        class="text-red-700 hover:text-red-900">
      <EpiIcon name="fa-times" />
    </button>
  </div>
</template>

<script setup lang="ts">
import EpiIcon from '~/components/ui/EpiIcon.vue'

/* PROPS */
const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  icon: {
    type: String,
    default: 'fa-exclamation-circle',
  },
  dismissible: {
    type: Boolean,
    default: false,
  },
})

/* EMITS */
const emit = defineEmits(['clear'])

/* METHODS */
const clearAlert = () => {
  emit('clear')
}
</script>

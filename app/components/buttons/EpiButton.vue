<template>
  <button
      :disabled="props.disabled"
      :class="[
      'flex group items-center justify-center gap-2 rounded-full py-3 px-4 text-[14px] font-medium transition-all ' +
        'duration-300 ease-in-out cursor-pointer active:scale-95',
      computedButtonClass,
      props.iconPosition === 'right' ? 'flex-row-reverse' : 'flex-row',
    ]"
  >
    <i
        v-if="props.icon"
        :class="[
        'fa',
        props.icon,
        'text-base transition-all duration-300 ease-in-out',
        props.buttonType === 'fill'
          ? props.disabled
            ? 'text-gray-500'
            : 'text-white'
          : 'text-secondary-600 hover:text-white group-hover:text-white',
      ]"
    ></i>
    <slot />
  </button>
</template>

<script setup lang="ts">
import type { PropType } from 'vue'

/*  PROPS */
const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  buttonType: {
    type: String as PropType<'fill' | 'outline'>,
    default: 'fill',
  },
  icon: {
    type: String,
    default: '',
  },
  iconPosition: {
    type: String as PropType<'left' | 'right'>,
    default: 'left',
  },
  variant: {
    type: String as PropType<'secondary' | 'red'>,
    default: 'secondary',
  },
})

/* COMPUTED */
const computedButtonClass = computed(() => {
  if (props.disabled) {
    return 'bg-gray-300 text-gray-500 cursor-not-allowed pointer-events-none'
  }

  switch (props.variant) {
    case 'red':
      return props.buttonType === 'fill'
          ? 'bg-red-600 text-white hover:bg-red-700'
          : 'bg-transparent text-red-600 border border-red-600 hover:bg-red-600 hover:text-white'
    default:
      return props.buttonType === 'fill'
          ? 'bg-secondary-600 text-white hover:bg-secondary-700'
          : 'bg-transparent text-secondary-600 border border-secondary-600 hover:bg-secondary-600 hover:text-white'
  }
})
</script>

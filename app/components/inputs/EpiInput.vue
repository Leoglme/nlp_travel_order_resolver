<template>
  <div>
    <label
        v-if="props.label"
        class="block mb-2 text-sm font-bold text-gray-800"
        :for="props.name"
    >
      {{ props.label }}
    </label>
    <Field
        :id="props.name"
        v-model="inputValue"
        :name="props.name"
        :type="props.type"
        :class="props.inputClass"
        class="w-full px-4 py-2.5 mb-3 text-gray-700 bg-gray-100 border-gray-200 rounded-md border-2 focus:border-2 focus:border-secondary-600 focus:bg-white focus:ring-0 outline-none"
        :placeholder="props.placeholder"
        :rules="props.rules"
        @input="handleInput($event)"
    />
    <ErrorMessage
        :name="props.name"
        class="text-red-600"
    />
  </div>
</template>
<script setup lang="ts">
import { Field, ErrorMessage } from 'vee-validate'
import type {Ref} from "vue";
/* PROPS */
const props = defineProps({
  value: {
    type: String,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: false,
    default: null,
  },
  type: {
    type: String,
    required: false,
    default: 'text',
  },
  placeholder: {
    type: String,
    required: false,
    default: null,
  },
  rules: {
    type: String,
    required: false,
    default: null,
  },
  inputClass: {
    type: String,
    required: false,
    default: null,
  },
})

/* REFS */
const inputValue: Ref<string> = ref(props.value)

/*  EMITS  */
const emit = defineEmits<{
  'update:value': [value: string]
}>()

/* METHODS */
const handleInput = (event: InputEvent) => {
  emit('update:value', (event.target as HTMLInputElement).value)
}

/* WATCHERS */
watch(() => props.value, (value) => {
  console.log('Value: ', value)
  inputValue.value = value
})
</script>

<template>
  <EpiButton
      :disabled="props.disabled"
      :icon-position="'left'"
      @click="toggleRecording"
  >
    <EpiIcon :name="props.isRecording ? 'fa-stop' : 'fa-microphone'" />
  </EpiButton>
</template>

<script setup lang="ts">
import EpiButton from "~/components/buttons/EpiButton.vue";
import EpiIcon from "~/components/ui/EpiIcon.vue";

const props = defineProps({
  isRecording: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['start-recording', 'stop-recording'])

const toggleRecording = () => {
  if (props.isRecording) {
    emit('stop-recording')
  } else {
    emit('start-recording')
  }
}
</script>

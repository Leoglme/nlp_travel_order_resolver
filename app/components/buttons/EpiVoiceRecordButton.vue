<template>
  <EpiButton
      class="w-[45px] h-[45px] rounded-full"
      :disabled="props.disabled"
      :icon-position="'left'"
      :class="{'animate-pulse': props.isRecording}"
      :variant="props.isRecording ? 'red' : 'secondary'"
      @click="toggleRecording"
  >
    <EpiIcon :name="props.isRecording ? 'fa-stop' : 'fa-microphone'" />
  </EpiButton>
</template>

<script setup lang="ts">
import type {Ref} from "vue";
import EpiButton from "~/components/buttons/EpiButton.vue";
import EpiIcon from "~/components/ui/EpiIcon.vue";

/* Props */
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

/* Emit events */
const emit = defineEmits(['start-recording', 'stop-recording', 'audio-ready'])

/* Ref for media recorder and audio */
const mediaRecorder: Ref<MediaRecorder | null> = ref(null)
const audioChunks: Ref<BlobPart[]> = ref([])

/* Methods */

/* Start recording */
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)

    audioChunks.value = [] // Clear previous audio chunks

    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }

    mediaRecorder.value.onstop = () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
      const audioUrl = URL.createObjectURL(audioBlob)
      emit('audio-ready', audioUrl)
    }

    mediaRecorder.value.start()
    emit('start-recording')
  } catch (error) {
    console.error('Error accessing audio device: ', error)
  }
}

/* Stop recording */
const stopRecording = () => {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop()
  }
  emit('stop-recording')
}

/* Toggle recording state */
const toggleRecording = () => {
  if (props.isRecording) {
    stopRecording()
  } else {
    startRecording()
  }
}
</script>

<style scoped>
.animate-pulse {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}
</style>

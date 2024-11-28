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
import { ref, onMounted } from "vue";
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
});

/* Emit events */
const emit = defineEmits(["start-recording", "stop-recording", "audio-ready"]);

/* References */
const audioContext = ref<AudioContext | null>(null);
const mediaRecorder = ref<MediaRecorder | null>(null);
const audioChunks = ref<BlobPart[]>([]);
const isRecording = ref(false);

/* Initialize AudioContext */
onMounted(() => {
  if (typeof window !== "undefined" && window.AudioContext) {
    audioContext.value = new (window.AudioContext || window.webkitAudioContext)();
    console.log("AudioContext initialized:", audioContext.value);
  } else {
    console.error("AudioContext is not supported in this environment.");
  }
});

/* Convert collected audio to PCM WAV */
const encodeWAV = async (audioBuffer: Float32Array, sampleRate: number): Promise<Blob> => {
  const bufferLength = audioBuffer.length;
  const wavBuffer = new ArrayBuffer(44 + bufferLength * 2); // WAV header + PCM data
  const view = new DataView(wavBuffer);

  // Write WAV Header
  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + bufferLength * 2, true); // File size - 8
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true); // Format chunk size
  view.setUint16(20, 1, true); // Audio format (1 = PCM)
  view.setUint16(22, 1, true); // Number of channels (1 = mono)
  view.setUint32(24, sampleRate, true); // Sample rate
  view.setUint32(28, sampleRate * 2, true); // Byte rate (SampleRate * NumChannels * BitsPerSample/8)
  view.setUint16(32, 2, true); // Block align (NumChannels * BitsPerSample/8)
  view.setUint16(34, 16, true); // Bits per sample (16 bits)
  writeString(view, 36, "data");
  view.setUint32(40, bufferLength * 2, true); // Data size

  // Write PCM data
  let offset = 44;
  for (let i = 0; i < bufferLength; i++) {
    const sample = Math.max(-1, Math.min(1, audioBuffer[i]));
    view.setInt16(offset, sample * 0x7fff, true);
    offset += 2;
  }

  return new Blob([view], { type: "audio/wav" });
};

/* Helper to write strings into the WAV header */
const writeString = (view: DataView, offset: number, string: string) => {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
};

/* Start recording */
const startRecording = async () => {
  if (!audioContext.value) {
    console.error("AudioContext is not initialized.");
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.value = new MediaRecorder(stream);
    audioChunks.value = []; // Reset audio chunks

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data);
      }
    };

    mediaRecorder.value.onstop = async () => {
      const blob = new Blob(audioChunks.value);
      const arrayBuffer = await blob.arrayBuffer();
      const audioBuffer = await audioContext.value!.decodeAudioData(arrayBuffer);
      const wavBlob = await encodeWAV(audioBuffer.getChannelData(0), audioBuffer.sampleRate);

      emit("audio-ready", wavBlob);
    };

    mediaRecorder.value.start();
    isRecording.value = true;
    emit("start-recording");
  } catch (error) {
    console.error("Error accessing microphone:", error);
  }
};

/* Stop recording */
const stopRecording = () => {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop();
    mediaRecorder.value.stream.getTracks().forEach((track) => track.stop());
  }
  isRecording.value = false;
  emit("stop-recording");
};

/* Toggle recording state */
const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording();
  } else {
    startRecording();
  }
};
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

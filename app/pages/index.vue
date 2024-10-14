<template>
  <div class="min-h-screen bg-[#FFE9D3] text-gray-700 pb-16">
    <div class="absolute left-0 right-0 top-0 z-0 h-screen w-full mix-blend-multiply">
      <img
          class="w-full h-full object-cover opacity-[0.1]"
          src="/images/t2.jpg"
          alt=""
      />
    </div>

    <div class="p-4">
      <section class="z-2 relative h-[80vh] flex flex-col justify-center gap-12">
        <h1 class="font-serif text-4xl md:text-5xl lg:text-6xl font-bold text-center mb-2 tracking-tighter">
          Transformer votre voyage
          <br />
          en une
          <span class="underline-yellow">aventure</span>.
        </h1>

        <div class="w-full flex gap-4 justify-center items-center">

          <div class="w-full flex flex-col gap-4 justify-center items-center min-w-[280px] max-w-3xl">
            <div class="group bg-white px-5 py-6 shadow-lg rounded-lg flex w-full text-gray-700">
              <div class="grid md:grid-cols-[auto,1fr,auto] items-center gap-4 w-full">
                <EpiVoiceRecordButton
                    class="relative top-1"
                    :isRecording="voiceIsRecording"
                    :disabled="false"
                    @start-recording="voiceStartRecording"
                    @stop-recording="voiceStopRecording"
                    @audio-ready="handleAudio"
                />
                <EpiInput
                    v-model:value="sentence"
                    name="travel_intent"
                    type="text"
                    label="Quel trajet voulez-vous faire ?"
                    placeholder="Je pars de Rennes pour aller à Biarritz"
                    rules="required"
                    class="flex-1"
                />
                <EpiButton
                    class="w-full md:w-fit relative top-1"
                    icon="fa-magnifying-glass"
                    :disabled="!sentence"
                    @click="validateSentenceAndRedirectToMap"
                >
                  GO
                </EpiButton>
              </div>
            </div>
            <EpiAlert
                v-if="validateSentenceErrorMessage !== ''"
                :message="validateSentenceErrorMessage"
                class="w-full"
            />
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type {Ref} from "vue";
import EpiButton from '~/components/buttons/EpiButton.vue'
import EpiInput from "~/components/inputs/EpiInput.vue";
import EpiVoiceRecordButton from "~/components/buttons/EpiVoiceRecordButton.vue";
import TravelOrderResolverService from "~/core/services/TravelOrderResolverService";
import type {
  ValidateTravelIntentResponse
} from "~/core/services/TravelOrderResolverService";
import type { ErrorResponse } from '~/core/types/response'
import NotyfService from "~/lib/services/NotyfService";
import EpiAlert from "~/components/feedback/EpiAlert.vue";

/* METAS */
useHead({
  title: 'Bienvenue',
})

/* HOOKS */
const router = useRouter()

/* REFS */
const sentence: Ref<string> = ref('')
const voiceIsRecording: Ref<boolean> = ref(false)
const validateSentenceErrorMessage: Ref<string> = ref('')

/* METHODS */
const dismissValidateSentenceError = () => {
  validateSentenceErrorMessage.value = ''
}

const validateSentenceAndRedirectToMap = async () => {
  const validateTravelIntentResponse: ValidateTravelIntentResponse | ErrorResponse = await TravelOrderResolverService.validateTravelIntent(sentence.value)
  const notyfService = new NotyfService()


  if('detail' in validateTravelIntentResponse) {
    return notyfService.error(validateTravelIntentResponse.detail)
  }


  if(validateTravelIntentResponse.is_valid) {
    const query = {
      q: sentence.value
    }
    await router.push({
      name: 'map',
      query
    })
  } else if (!validateTravelIntentResponse.is_trip_related) {
    validateSentenceErrorMessage.value = 'La phrase ne semble pas être liée à un trajet. Veuillez formuler une phrase indiquant un départ et une destination.'
  } else if (!validateTravelIntentResponse.is_correct_language) {
    validateSentenceErrorMessage.value = 'Le texte soumis est dans une autre langue. Merci de formuler votre phrase en français.'
  } else {
    validateSentenceErrorMessage.value = 'Une erreur est survenue lors du traitement de votre demande.'
  }
}

const voiceStartRecording = () => {
  voiceIsRecording.value = true
}

const voiceStopRecording = () => {
  voiceIsRecording.value = false
}

/* Handle the audio when it's ready */
const handleAudio = async (audioUrl: string) => {
  console.log('Audio URL: ', audioUrl)

  // Convert the audioUrl into a Blob and send it to the API
  const response = await fetch(audioUrl)
  const audioBlob = await response.blob()
  const file = new File([audioBlob], "audio.wav", { type: "audio/wav" })

  // Call the API to convert the audio to text
  const audioTextResponse: { sentence: string } | ErrorResponse = await TravelOrderResolverService.audioToText(file)

  if ('detail' in audioTextResponse) {
    console.error('Error while converting audio to text:', audioTextResponse.detail)
    const notyfService = new NotyfService()
    notyfService.error(audioTextResponse.detail)
    return
  }

  // Update the sentence with the transcribed text
  sentence.value = audioTextResponse.sentence
  dismissValidateSentenceError()
  console.log("Transcribed text: ", audioTextResponse.sentence)
}

/* LIFECYCLE */
onUnmounted(() => {
  dismissValidateSentenceError()
})
</script>

<style>
.underline-yellow {
  position: relative;
  display: inline-block;
  z-index: 1;
}

.underline-yellow::after {
  content: '';
  position: absolute;
  top: 100%;
  right: -2px;
  left: -2px;
  height: 10px;
  border-radius: 6.75px;
  margin-top: -6px;
  background-color: #ffd400;
  z-index: 0;
}
</style>

<template>
  <div
      v-html="travelIntentClassifierEvaluationHtml"
  />
</template>


<script lang="ts" setup>
import DocumentationService from "~/core/services/DocumentationService";
import type { HtmlDocumentationResponse } from "~/core/services/DocumentationService";
import type { ErrorResponse } from "~/core/types/response";
import type {Ref} from "vue";

// Define page meta
definePageMeta({ layout: 'documentation' })

// Refs
const travelIntentClassifierEvaluationHtml: Ref<HtmlDocumentationResponse | null> = ref(null)

const travelIntentClassifierEvaluationResponse: HtmlDocumentationResponse | ErrorResponse = await DocumentationService.getTravelIntentClassifierEvaluation()
if(typeof travelIntentClassifierEvaluationResponse === 'object' && 'error' in travelIntentClassifierEvaluationResponse) {
  console.error(travelIntentClassifierEvaluationResponse.error)
} else {
  travelIntentClassifierEvaluationHtml.value = travelIntentClassifierEvaluationResponse
}
</script>

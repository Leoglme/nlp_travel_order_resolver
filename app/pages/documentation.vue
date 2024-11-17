<template>
  <div
      v-html="travelIntentClassifierEvaluationHtml"
      class="ml-6"
  />
</template>


<script lang="ts" setup>
import DocumentationHtmlService, { type HtmlDocumentationResponse } from "~/core/services/DocumentationHtmlService";
import type { ErrorResponse } from "~/core/types/response";

// Define page meta
definePageMeta({ layout: 'documentation' })

// Refs
const travelIntentClassifierEvaluationHtml = ref<HtmlDocumentationResponse | null>(null)

const travelIntentClassifierEvaluationResponse: HtmlDocumentationResponse | ErrorResponse = await DocumentationHtmlService.getTravelIntentClassifierEvaluation()
if(typeof travelIntentClassifierEvaluationResponse === 'object' && 'detail' in travelIntentClassifierEvaluationResponse) {
  console.error(travelIntentClassifierEvaluationResponse.detail)
} else {
  travelIntentClassifierEvaluationHtml.value = travelIntentClassifierEvaluationResponse
}
</script>

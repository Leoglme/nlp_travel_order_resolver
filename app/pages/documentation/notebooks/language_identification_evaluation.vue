<template>
  <div
      v-html="languageIdentificationEvaluationHtml"
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
const languageIdentificationEvaluationHtml: Ref<HtmlDocumentationResponse | null> = ref(null)

const languageIdentificationEvaluationResponse: HtmlDocumentationResponse | ErrorResponse = await DocumentationService.getLanguageIdentificationEvaluation()
if(typeof languageIdentificationEvaluationResponse === 'object' && 'error' in languageIdentificationEvaluationResponse) {
  console.error(languageIdentificationEvaluationResponse.error)
} else {
  languageIdentificationEvaluationHtml.value = languageIdentificationEvaluationResponse
}
</script>

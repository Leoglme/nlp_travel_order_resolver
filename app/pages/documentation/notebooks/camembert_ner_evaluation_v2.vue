<template>
  <div
      v-html="camembertNERModelEvaluationHtml"
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
const camembertNERModelEvaluationHtml: Ref<HtmlDocumentationResponse | null> = ref(null)

const camembertNERModelEvaluationResponse: HtmlDocumentationResponse | ErrorResponse = await DocumentationService.getCamembertNERModelEvaluationV2()
if(typeof camembertNERModelEvaluationResponse === 'object' && 'error' in camembertNERModelEvaluationResponse) {
  console.error(camembertNERModelEvaluationResponse.error)
} else {
  camembertNERModelEvaluationHtml.value = camembertNERModelEvaluationResponse
}
</script>
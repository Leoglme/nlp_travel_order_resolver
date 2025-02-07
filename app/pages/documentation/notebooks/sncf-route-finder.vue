<template>
  <div>
    <EpiPreCopyButton />
    <div
        v-html="sncfRouteFinderEvaluationHtml"
    />
  </div>
</template>


<script lang="ts" setup>
import DocumentationService from "~/core/services/DocumentationService";
import type { HtmlDocumentationResponse } from "~/core/services/DocumentationService";
import type { ErrorResponse } from "~/core/types/response";
import type {Ref} from "vue";
import EpiPreCopyButton from "~/components/buttons/EpiPreCopyButton.vue";

// Define page meta
definePageMeta({ layout: 'documentation' })

// Refs
const sncfRouteFinderEvaluationHtml: Ref<HtmlDocumentationResponse | null> = ref(null)

const sncfRouteFinderEvaluationResponse: HtmlDocumentationResponse | ErrorResponse = await DocumentationService.getSncfRouteFinderEvaluation()
if(typeof sncfRouteFinderEvaluationResponse === 'object' && 'error' in sncfRouteFinderEvaluationResponse) {
  console.error(sncfRouteFinderEvaluationResponse.error)
} else {
  sncfRouteFinderEvaluationHtml.value = sncfRouteFinderEvaluationResponse
}
</script>

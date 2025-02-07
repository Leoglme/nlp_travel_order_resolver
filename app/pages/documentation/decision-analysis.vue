<template>
  <div>
    <div
        v-if="decisionAnalysisMarkdown"
        v-html="decisionAnalysisMarkdown"
        class="prose text-[14px] max-w-full"
    />
    <p v-else class="text-gray-500">
      Chargement...
    </p>
  </div>
</template>

<script lang="ts" setup>
import { marked } from "marked";
import DocumentationService from "~/core/services/DocumentationService";
import type { MarkdownDocumentationResponse } from "~/core/services/DocumentationService";
import type { ErrorResponse } from "~/core/types/response";
import type { Ref } from "vue";

// Define page meta
definePageMeta({ layout: 'documentation' })

// Refs
const decisionAnalysisMarkdown: Ref<MarkdownDocumentationResponse | null> = ref(null)

// Fetch the Exemple Processing Markdown content
const decisionAnalysisMarkdownResponse: MarkdownDocumentationResponse | ErrorResponse = await DocumentationService.getDecisionAnalysisMarkdown()

if (typeof decisionAnalysisMarkdownResponse === 'object' && 'error' in decisionAnalysisMarkdownResponse) {
  console.error(decisionAnalysisMarkdownResponse.error)
} else {
  decisionAnalysisMarkdown.value = await marked(decisionAnalysisMarkdownResponse)
}
</script>

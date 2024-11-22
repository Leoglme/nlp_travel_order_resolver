<template>
  <div>
    <div
        v-if="exempleProcessingMarkdown"
        v-html="exempleProcessingMarkdown"
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
const exempleProcessingMarkdown: Ref<MarkdownDocumentationResponse | null> = ref(null)

// Fetch the Exemple Processing Markdown content
const exempleProcessingMarkdownResponse: MarkdownDocumentationResponse | ErrorResponse = await DocumentationService.getExempleProcessingMarkdown()

if (typeof exempleProcessingMarkdownResponse === 'object' && 'error' in exempleProcessingMarkdownResponse) {
  console.error(exempleProcessingMarkdownResponse.error)
} else {
  exempleProcessingMarkdown.value = await marked(exempleProcessingMarkdownResponse)
}
</script>

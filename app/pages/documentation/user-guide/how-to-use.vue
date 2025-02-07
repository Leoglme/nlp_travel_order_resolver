<template>
  <div>
    <div
        v-if="howToUseMarkdown"
        v-html="howToUseMarkdown"
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
const howToUseMarkdown: Ref<MarkdownDocumentationResponse | null> = ref(null)

// Fetch the How To Use Markdown content
const howToUseMarkdownResponse: MarkdownDocumentationResponse | ErrorResponse = await DocumentationService.getHowToUseMarkdown()

if (typeof howToUseMarkdownResponse === 'object' && 'error' in howToUseMarkdownResponse) {
  console.error(howToUseMarkdownResponse.error)
} else {
  howToUseMarkdown.value = await marked(howToUseMarkdownResponse)
}
</script>

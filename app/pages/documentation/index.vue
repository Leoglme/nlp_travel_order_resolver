<template>
  <div>
    <EpiPreCopyButton />
    <div
        v-if="projectIntroductionMarkdown"
        v-html="projectIntroductionMarkdown"
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
import type {Ref} from "vue";
import EpiPreCopyButton from "~/components/buttons/EpiPreCopyButton.vue";

// Define page meta
definePageMeta({ layout: 'documentation' })

// Refs
const projectIntroductionMarkdown: Ref<MarkdownDocumentationResponse | null> = ref(null)

// Fetch the project introduction Markdown content
const projectIntroductionMarkdownResponse: MarkdownDocumentationResponse | ErrorResponse = await DocumentationService.getProjectIntroductionMarkdown()

if (typeof projectIntroductionMarkdownResponse === 'object' && 'error' in projectIntroductionMarkdownResponse) {
  console.error(projectIntroductionMarkdownResponse.error)
} else {
  projectIntroductionMarkdown.value = await marked(projectIntroductionMarkdownResponse)
}
</script>

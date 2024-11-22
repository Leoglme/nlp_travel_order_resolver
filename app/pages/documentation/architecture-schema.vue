<template>
  <div>
    <div v-if="pdfBlobUrl" class="flex justify-center">
      <iframe
          :src="pdfBlobUrl"
          class="w-full h-[calc(100vh-75px)] border-0"
          title="Schema Architecture"
      ></iframe>
    </div>
    <p v-else class="text-gray-500 text-center">
      Chargement du PDF...
    </p>
  </div>
</template>

<script lang="ts" setup>
import type { Ref } from "vue";
import {ref, onMounted} from 'vue';
import DocumentationService from '~/core/services/DocumentationService';
import type { ErrorResponse } from '~/core/types/response';

// Define page meta
definePageMeta({ layout: 'documentation-pdf' })

// Refs
const pdfBlobUrl: Ref<string | null> = ref(null);

// Fetch the PDF on component mount
onMounted(async () => {
  const response: Blob | ErrorResponse = await DocumentationService.getArchitectureSchemaPdf();

  if (response instanceof Blob) {
    // Create a Blob URL to display the PDF
    pdfBlobUrl.value = URL.createObjectURL(response);
  } else {
    console.error(response.error || 'Failed to fetch the PDF');
  }
});
</script>

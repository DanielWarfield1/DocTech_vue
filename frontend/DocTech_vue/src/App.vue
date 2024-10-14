<template>
  <div>
    <!-- Existing content, e.g., the speech recognition component -->
    <SpeechRecognitionComponent @api-response="handleApiResponse" />

    <!-- Include the PDF Viewer component -->
    <PdfViewer :apiResponse="apiResponse" />
  </div>
</template>

<script>
import PdfViewer from './components/PdfViewer.vue';
import SpeechRecognitionComponent from './components/SpeechRecognitionComponent.vue';

export default {
  components: {
    PdfViewer,
    SpeechRecognitionComponent,
  },
  data() {
    return {
      apiResponse: {},
    };
  },
  methods: {
    handleApiResponse(response) {
      this.apiResponse = response;
    },
  },
};
</script>

<template>
  <div>
    <button v-if="!audioInitialized" @click="initializeAudio">Start Listening</button>
    <div v-else>
      <div :style="circleStyle" class="circle"></div>
      <div class="transcribed-text">
        <h3>Transcribed Text:</h3>
        <div class="text-content">{{ allTranscribedText }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onBeforeUnmount } from 'vue';

export default {
  name: 'SpeechRecognitionComponent',
  props: {
    currentPage: {
      type: Number,
      default: 1,
    },
  },
  setup(props, { emit }) {
    const audioContext = ref(null);
    const isListening = ref(false);
    const isActivated = ref(false);
    const audioInitialized = ref(false);
    const circleSize = ref(50);
    const logText = ref('');
    const lastLogIndex = ref(0);
    const allTranscribedText = ref('');
    let sr = null;
    let idleTimeout = null;
    const silenceDelay = 10000;

    const circleStyle = computed(() => ({
      width: `${circleSize.value}px`,
      height: `${circleSize.value}px`,
      backgroundColor: isActivated.value ? 'white' : '#333',
      borderRadius: '50%',
      transition: 'all 0.1s ease',
    }));

    const startListening = () => {
      isListening.value = true;
      isActivated.value = true;
      resetIdleTimeout();
    };

    const resetActivationState = () => {
      isListening.value = false;
      isActivated.value = false;
      clearIdleTimeout();
    };

    const processTranscript = () => {
      const newLogText = logText.value.slice(lastLogIndex.value).trim();
      if (newLogText.toLowerCase().includes('hey doc')) {
        console.log('Logged Text:', newLogText);

        // Send the transcribed text to the API
        const queryText = encodeURIComponent(newLogText);
        const currentPageNumber = props.currentPage || 1; // Use current page if available

        fetch(`http://127.0.0.1:5000/query?query=${queryText}&current_page=${currentPageNumber}`)
          .then(response => response.json())
          .then(data => {
            console.log('API Response:', data);
            emit('api-response', data); // Emit the API response
          })
          .catch(error => {
            console.error('Error calling API:', error);
          });
      }
      lastLogIndex.value = logText.value.length;
      resetActivationState();
    };

    const resetIdleTimeout = () => {
      if (idleTimeout) {
        clearTimeout(idleTimeout);
      }
      idleTimeout = setTimeout(() => {
        if (isListening.value) {
          processTranscript();
        }
      }, silenceDelay);
    };

    const clearIdleTimeout = () => {
      if (idleTimeout) {
        clearTimeout(idleTimeout);
        idleTimeout = null;
      }
    };

    const setupSpeechRecognition = () => {
      const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      sr = new Recognition();

      sr.continuous = true;
      sr.interimResults = false;

      sr.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }

        const lowerTranscript = transcript.toLowerCase();

        // Append to allTranscribedText regardless of activation state
        allTranscribedText.value += ' ' + transcript.trim();

        if (!isActivated.value && (lowerTranscript.includes('hey doc tech') || lowerTranscript.includes('hey doc'))) {
          startListening();
        }

        if (isListening.value) {
          logText.value += ' ' + transcript.trim();
          resetIdleTimeout(); // Reset idle timeout on new speech input
        }
      };

      sr.onerror = (event) => {
        console.error('Speech Recognition Error:', event.error);
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          sr.stop();
        } else {
          // Restart speech recognition on other errors
          sr.stop();
          sr.start();
        }
      };

      sr.onend = () => {
        // Restart the recognizer to keep listening
        sr.start();
      };

      sr.start();
    };

    const initializeAudio = async () => {
      try {
        audioContext.value = new (window.AudioContext || window.webkitAudioContext)();
        await navigator.mediaDevices.getUserMedia({ audio: true });

        audioInitialized.value = true;
        setupSpeechRecognition();
        animateCircle();
      } catch (error) {
        console.error('Error accessing microphone:', error);
      }
    };

    const animateCircle = () => {
      if (isListening.value) {
        // Increase circle size to simulate activity
        circleSize.value = 60;
      } else {
        circleSize.value = 50;
      }
      requestAnimationFrame(animateCircle);
    };

    onBeforeUnmount(() => {
      if (audioContext.value) audioContext.value.close();
      if (sr) sr.stop();
      clearIdleTimeout();
    });

    return {
      circleStyle,
      audioInitialized,
      initializeAudio,
      allTranscribedText,
    };
  },
};
</script>

<style scoped>
.circle {
  display: inline-block;
  margin-top: 20px;
}

.transcribed-text {
  margin-top: 20px;
}

.text-content {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 10px;
  white-space: pre-wrap;
}

button {
  padding: 10px 20px;
  margin-top: 20px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #555;
}
</style>

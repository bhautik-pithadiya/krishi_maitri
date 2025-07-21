<template>
    <div>
      <h2>Text to Speech (TTS)</h2>
      <input v-model="text" placeholder="Enter text" />
      <button @click="sendText" :disabled="loading || !text">Speak</button>
      <span v-if="loading">Loading...</span>
      <audio v-if="audioUrl" :src="audioUrl" controls autoplay></audio>
      <p v-if="error" style="color: red;">{{ error }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const text = ref('');
  const audioUrl = ref('');
  const loading = ref(false);
  const error = ref('');
  
  function sendText() {
    if (!text.value) return;
    loading.value = true;
    error.value = '';
    audioUrl.value = '';
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/tts');
    ws.binaryType = 'arraybuffer';
    ws.onopen = () => {
      ws.send(text.value);
    };
    ws.onmessage = (event) => {
      const audioBlob = new Blob([event.data]);
      audioUrl.value = URL.createObjectURL(audioBlob);
      loading.value = false;
      ws.close();
    };
    ws.onerror = () => {
      error.value = 'WebSocket error. Please try again.';
      loading.value = false;
      ws.close();
    };
  }
  </script>
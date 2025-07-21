<template>
    <div>
      <h2>Speech to Text (STT)</h2>
      <button @click="startRecording" :disabled="recording">Start Recording</button>
      <button @click="stopRecording" :disabled="!recording">Stop & Transcribe</button>
      <span v-if="recording">Recording...</span>
      <span v-if="loading">Transcribing...</span>
      <p v-if="transcript">Transcript: {{ transcript }}</p>
      <p v-if="error" style="color: red;">{{ error }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const recording = ref(false);
  const loading = ref(false);
  const transcript = ref('');
  const error = ref('');
  let mediaRecorder;
  let audioChunks = [];
  
  function startRecording() {
    transcript.value = '';
    error.value = '';
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      recording.value = true;
      audioChunks = [];
      mediaRecorder.ondataavailable = e => {
        audioChunks.push(e.data);
      };
    }).catch(() => {
      error.value = 'Could not access microphone.';
    });
  }
  
  function stopRecording() {
    if (!mediaRecorder) return;
    loading.value = true;
    recording.value = false;
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      audioBlob.arrayBuffer().then(buffer => {
        const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stt');
        ws.onopen = () => {
          ws.send(buffer);
        };
        ws.onmessage = (event) => {
          transcript.value = event.data;
          loading.value = false;
          ws.close();
        };
        ws.onerror = () => {
          error.value = 'WebSocket error. Please try again.';
          loading.value = false;
          ws.close();
        };
      });
    };
  }
  </script>
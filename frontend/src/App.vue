<script setup>
import TTSComponent from './components/TTSComponent.vue';
import STTComponent from './components/STTComponent.vue';
</script>

<template>
  <div class="container">
    <h1 class="main-title">Krishi Maitri - STT & TTS Demo</h1>
    <TTSComponent />
    <STTComponent />
  </div>
</template>

<style scoped>
body {
  background: #fff; /* or #f7f7f7 for a very light grey */
}

.container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 40px;
}

.main-title {
  color: #34495E;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: bold;
  letter-spacing: 1px;
  text-align: center;
}

/* Button style */
button {
  background: #41B883;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0.5em 1.2em;
  font-size: 1em;
  margin: 0.5em 0.5em 0.5em 0;
  cursor: pointer;
  transition: background 0.2s;
}
button:disabled {
  background: #2c8a67;
  cursor: not-allowed;
}
button:hover:enabled {
  background: #369f6b;
}

/* Input style */
input[type='text'], input[type='file'] {
  padding: 0.5em;
  border-radius: 4px;
  border: 1px solid #41B883;
  margin: 0.5em 0;
  font-size: 1em;
  color: #34495E;
}

audio {
  margin-top: 1em;
}
</style>
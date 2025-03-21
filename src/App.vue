<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import axios from 'axios'

const messages = ref([{ text: 'Hi, How can I help you?', type: 'output' }])

const newMessage = ref('')

const sendMessage = async () => {
  if (newMessage.value.trim() !== '') {
    messages.value.push({ text: newMessage.value, type: 'input' })
    const userMessage = newMessage.value
    newMessage.value = ''

    try {
      const response = await axios.post('http://localhost:8000/ask', {
        question: userMessage,
      })
      const data = response.data

      messages.value.push({ text: data, type: 'output' })
    } catch (error) {
      console.error('Error sending message:', error)
      messages.value.push({ text: 'An error occurred', type: 'output' })
    }
  }
}
watch(messages, async () => {
  await nextTick()
  const messageElem = document.getElementsByClassName('chat-messages')
  const lastMessage = messageElem[messageElem.length - 1]
  lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' })
})

// Handle Enter key press on the input field
const handleKeyPress = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    sendMessage()
  }
}
</script>

<template>
  <div class="container">
    <div class="chat-window">
      <div class="chat-header">Chat</div>
      <div class="chat-messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.type]"
          v-html="message.text"
        ></div>
      </div>
      <div class="chat-input">
        <input
          v-model="newMessage"
          type="text"
          placeholder="Type a message..."
          @keypress="handleKeyPress"
        />
        <button @click="sendMessage">Send</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 70v7;
  width: 100%;
}

.chat-window {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 700px;
  max-height: 700px;
  border: 1px;
  background-color: #1a1a1a; /* Dark background */
}

.chat-header {
  background-color: #333; /* Darker header background */
  padding: 10px;
  text-align: center;
  font-weight: bold;
  color: #fff; /* White text */
}

.chat-messages {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  background-color: #2a2a2a; /* Darker messages background */
  display: flex;
  flex-direction: column;
}

.message {
  display: inline-block;
  margin-bottom: 10px;
  padding: 5px;
  border-radius: 5px;
  background-color: #444; /* Darker message background */
  color: #fff; /* White text */
  max-width: 70%; /* Maximum width for messages */
  word-wrap: break-word; /* Wrap long words */
}

.message.input {
  align-self: flex-end;
  margin-left: auto; /* Push the message to the right */
  background-color: #007bff; /* Blue background for input messages */
  text-align: left;
}

.message.output {
  align-self: flex-start;
  background-color: #444; /* Darker background for output messages */
  text-align: left;
}

.chat-input {
  display: flex;
  padding: 10px;
  background-color: #333; /* Darker input background */
}

.chat-input input {
  flex: 1;
  padding: 5px;
  border: 1px solid #555; /* Darker border */
  border-radius: 5px;
  background-color: #444; /* Darker input background */
  color: #fff; /* White text */
}

.chat-input button {
  margin-left: 10px;
  padding: 5px 10px;
  border: none;
  border-radius: 5px;
  background-color: #007bff;
  color: #fff;
  cursor: pointer;
}

.chat-input button:hover {
  background-color: #0056b3;
}

::v-deep table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  font-family: sans-serif;
  background-color: #1a1a1a;
  color: #e0e0e0;
}

::v-deep table th,
::v-deep table td {
  border: 1px solid #444;
  padding: 8px;
  text-align: left;
}

::v-deep table th {
  background-color: #333;
  font-weight: bold;
}

::v-deep table tr:nth-child(even) {
  background-color: #2a2a2a;
}

::v-deep table tr:hover {
  background-color: #3a3a3a;
}
</style>

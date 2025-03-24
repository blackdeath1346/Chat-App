<template>
  <div class="chat-container">
    <h2>Global Chat</h2>
    <div class="messages">
      <div
        v-for="msg in messages"
        :key="msg.timestamp"
        class="message"
      >
        <strong>{{ msg.sender }}:</strong> {{ msg.content }}
      </div>
    </div>
    <div class="message-input">
      <input v-model="newMessage" type="text" placeholder="Type a message..." @keyup.enter="sendMessage" />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import { getGlobalMessages, postGlobalMessage } from "../api/api.js";

export default {
  data() {
    return {
      currentUser: localStorage.getItem("currentUser") || "",
      messages: [],
      newMessage: "",
      socket: null, // WebSocket for real-time updates
    };
  },
  async created() {
    if (!this.currentUser) {
      this.$router.push("/");
      return;
    }
    await this.fetchMessages();
    this.setupWebSocket();
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  },
  methods: {
    async fetchMessages() {
      try {
        const data = await getGlobalMessages();
        this.messages = data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      } catch (error) {
        alert("Error fetching global messages.");
      }
    },
    setupWebSocket() {
      this.socket = new WebSocket("ws://127.0.0.1:8000/ws/broadcast/");

      this.socket.onopen = () => {
        console.log("Broadcast WebSocket connected");
      };

      this.socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.messages.push(message);
      };

      this.socket.onclose = () => {
        console.log("Broadcast WebSocket disconnected");
      };
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return;

      const messageData = {
        sender: this.currentUser,
        content: this.newMessage,
      };

      try {
        await postGlobalMessage(this.currentUser, this.newMessage); // Store in database
        this.socket.send(JSON.stringify(messageData)); // Send via WebSocket
        this.newMessage = ""; // Clear input
      } catch (error) {
        alert("Error sending global message.");
      }
    },
  },
};
</script>

<style scoped>
.chat-container {
  max-width: 600px;
  margin: auto;
  text-align: center;
}
.messages {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  padding: 10px;
  margin-bottom: 10px;
}
.message {
  background-color: #f1f1f1;
  padding: 5px;
  margin: 5px;
  border-radius: 5px;
}
.message-input {
  display: flex;
  justify-content: space-between;
}
input {
  flex: 1;
  padding: 8px;
}
button {
  padding: 8px 16px;
  cursor: pointer;
}
</style>

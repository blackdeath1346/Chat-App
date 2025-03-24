<template>
  <div class="chat-container">
    <h2>Chat with {{ receiver }}</h2>
    <div class="messages">
      <div
        v-for="msg in messages"
        :key="msg.timestamp"
        :class="{ sent: msg.sender === currentUser, received: msg.sender !== currentUser }"
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
import { getChat, postChat } from "../api/api.js";

export default {
  props: ["username"],
  data() {
    return {
      currentUser: localStorage.getItem("currentUser") || "",
      receiver: this.username,
      messages: [],
      newMessage: "",
    };
  },
  async created() {
    if (!this.currentUser) {
      this.$router.push("/");
      return;
    }
    await this.fetchMessages();
  },
  methods: {
    async fetchMessages() {
      try {
        const { senderMessages, receiverMessages } = await getChat(this.currentUser, this.receiver);
        //console.log("a");
        //console.log(receiverMessages);
        this.messages = [...senderMessages, ...receiverMessages].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        console.log(this.messages);
      } catch (error) {
        alert("Error fetching messages.");
      }
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return;
      try {
        await postChat(this.currentUser, this.receiver, this.newMessage);
        this.newMessage = "";
        await this.fetchMessages();
      } catch (error) {
        alert("Error sending message.");
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
.sent {
  text-align: right;
  background-color: #dcf8c6;
  padding: 5px;
  margin: 5px;
  border-radius: 5px;
}
.received {
  text-align: left;
  background-color: #fff;
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

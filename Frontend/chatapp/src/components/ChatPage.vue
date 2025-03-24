<template>
  <div :class="['chat-container', { dark: darkMode }]">
    <!-- Dark Mode Toggle Slider -->
    <div class="dark-mode-toggle">
      <label class="switch">
        <input type="checkbox" v-model="darkMode" />
        <span class="slider round"></span>
      </label>
    </div>

    <h2 class="chat-header">Chat with {{ receiver }}</h2>
    <div ref="messagesContainer" class="messages">
      <div
        v-for="msg in messages"
        :key="msg.timestamp"
        :id="'msg-' + msg.id"
        @contextmenu.prevent="setReply(msg)"
        :class="{
          message: true,
          sent: msg.sender === currentUser,
          received: msg.sender !== currentUser
        }"
      >
        <strong>{{ msg.sender }}</strong><br />
        <!-- If the message is a reply, show a reply snippet (clicking it highlights the original) -->
        <div
          v-if="msg.reply_to"
          class="reply-snippet"
          :class="{
            'sent-reply-snippet': msg.sender === currentUser,
            'received-reply-snippet': msg.sender !== currentUser
          }"
          @click="highlightReply(msg.reply_to)"
        >
          <span class="reply-snippet-text">
            {{ getTruncatedReply(getOriginalMessage(msg.reply_to)) }}
          </span>
        </div>
        <span>{{ msg.content }}</span>
        <div v-if="msg.file_attachment" class="file-attachment">
          <!-- If it's an image, show thumbnail; otherwise, show a file box -->
          <div
            v-if="isImage(msg.file_attachment)"
            class="image-preview"
            @click="openFile(msg.file_attachment)"
          >
            <img :src="msg.file_attachment" alt="Attachment" />
          </div>
          <div
            v-else
            class="file-box"
            @click="openFile(msg.file_attachment)"
          >
            <span class="file-icon">📎</span>
            <span class="file-name">
              {{ extractFileName(msg.file_attachment) }}
            </span>
          </div>
        </div>
        <div class="timestamp">{{ formatTimestamp(msg.timestamp) }}</div>
      </div>
    </div>
    <!-- Reply preview (shown when composing a reply) -->
    <div
      v-if="replyTo"
      class="reply-preview"
      :class="{
        'sent-reply': replyTo.sender === currentUser,
        'received-reply': replyTo.sender !== currentUser
      }"
    >
      <span class="reply-text">{{ truncatedReply }}</span>
      <span class="cancel-reply" @click="cancelReply">×</span>
    </div>
    <div class="message-input">
      <input
        v-model="newMessage"
        type="text"
        placeholder="Type a message..."
        @keyup.enter="sendMessage"
      />
      <!-- Hidden file input triggered by the Attach File button -->
      <input
        type="file"
        ref="fileInput"
        @change="handleFileChange"
        style="display: none"
      />
      <button @click="triggerFileSelect">📎 Attach File</button>
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import { getChat, postChat } from "../api/api.js";
import API from "../api/api.js";

export default {
  props: ["username"],
  data() {
    return {
      selectedFile: null,
      currentUser: localStorage.getItem("currentUser") || "",
      receiver: this.username,
      messages: [],
      newMessage: "",
      replyTo: null, // Holds the message being replied to
      socket: null, // WebSocket connection
      darkMode: false // Dark mode toggle
    };
  },
  computed: {
    truncatedReply() {
      if (this.replyTo && this.replyTo.content) {
        const limit = 50; // character limit for reply preview
        return this.replyTo.content.length > limit
          ? this.replyTo.content.substring(0, limit) + "..."
          : this.replyTo.content;
      }
      return "";
    }
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
      this.socket.close(); // Close WebSocket when leaving chat
    }
  },
  methods: {
    isImage(fileUrl) {
      return /\.(jpeg|jpg|gif|png)$/i.test(fileUrl);
    },
    extractFileName(url) {
      return url.split("/").pop();
    },
    openFile(url) {
      // Open the file in a new tab to view it
      window.open(url, "_blank");
    },
    setReply(msg) {
      // Set the selected message as the one being replied to
      this.replyTo = msg;
    },
    cancelReply() {
      this.replyTo = null;
    },
    async fetchMessages() {
      try {
        const { senderMessages, receiverMessages } = await getChat(
          this.currentUser,
          this.receiver
        );
        this.messages = [...senderMessages, ...receiverMessages].sort(
          (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
        );
        this.messages.forEach((msg) => {
          // Simplify sender display
          msg.sender = msg.sender.split("/").slice(-2, -1)[0];
        });
        this.scrollToBottom();
      } catch (error) {
        alert("Error fetching messages.");
      }
    },
    async setupWebSocket() {
      const chatId = [this.currentUser, this.receiver].sort().join("-");
      this.socket = new WebSocket(`ws://127.0.0.1:8000/ws/chat/${chatId}/`);
      this.socket.onopen = () => {
        console.log("WebSocket connected");
      };
      this.socket.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        if (message.file_attachment) {
          try {
            const fileResponse = await API.get(message.file_attachment, {
              responseType: "blob"
            });
            message.file_attachment = URL.createObjectURL(fileResponse.data);
          } catch (error) {
            console.error("Error fetching file for message:", message, error);
          }
        }
        this.messages.push(message);
        this.scrollToBottom();
      };
      this.socket.onclose = () => {
        console.log("WebSocket disconnected");
      };
    },
    async sendMessage() {
      // Use the file name if a file is selected; otherwise, use newMessage.
      let content = this.selectedFile
        ? this.selectedFile.name
        : this.newMessage;
      if (!content.trim()) return;

      // Build URLs as required by your API
      const [user1, user2] = [this.currentUser, this.receiver].sort();
      const chatId = `http://localhost:8000/Chats/${user1}-${user2}/`;
      const senderID = `http://localhost:8000/Users/${this.currentUser}/`;

      try {
        if (this.selectedFile) {
          const formData = new FormData();
          formData.append("chat", chatId);
          formData.append("sender", senderID);
          formData.append("content", content);
          formData.append("file_attachment", this.selectedFile);
          // If replying, append reply_to
          if (this.replyTo) {
            formData.append("reply_to", this.replyTo.id);
          }
          await API.post("/Messages/", formData, {
            headers: {
              "Content-Type": "multipart/form-data"
            }
          });
          setTimeout(() => {
            this.fetchMessages();
          }, 1000);
        } else {
          const payload = {
            chat: chatId,
            sender: senderID,
            content: content
          };
          if (this.replyTo) {
            payload.reply_to = this.replyTo.id;
          }
          await API.post("/Messages/", payload);
        }
        this.newMessage = "";
        this.selectedFile = null;
        this.$refs.fileInput.value = "";
        // Clear the reply selection after sending
        this.cancelReply();
      } catch (error) {
        console.error(error);
        alert("Error sending message.");
      }
    },
    triggerFileSelect() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const files = event.target.files;
      if (files.length > 0) {
        this.selectedFile = files[0];
        this.sendMessage();
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },
    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleString();
    },
    // Returns the original message object for a given reply id (if found)
    getOriginalMessage(replyId) {
      return this.messages.find(m => m.id === replyId) || {};
    },
    // Returns a truncated version of the given message's content
    getTruncatedReply(message) {
      if (message && message.content) {
        const limit = 50;
        return message.content.length > limit
          ? message.content.substring(0, limit) + "..."
          : message.content;
      }
      return "";
    },
    // When clicking a reply snippet, temporarily highlight the original message
    highlightReply(replyId) {
      const element = document.getElementById(`msg-${replyId}`);
      if (element) {
        element.classList.add("highlight");
        setTimeout(() => {
          element.classList.remove("highlight");
        }, 2000);
      }
    }
  }
};
</script>

<style scoped>
.chat-container {
  position: relative;
  max-width: 600px;
  margin: 20px auto;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: background 0.3s, color 0.3s;
}
.chat-container.dark {
  background: #2c2c2c;
  color: #f5f5f5;
}
.chat-header {
  margin-bottom: 20px;
  font-size: 1.5em;
  color: #333;
}
.chat-container.dark .chat-header {
  color: #f5f5f5;
}
.messages {
  height: 400px;
  overflow-y: auto;
  background: #f7f7f7;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}
.message {
  max-width: 80%;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 8px;
  line-height: 1.4;
  word-wrap: break-word;
  position: relative;
}
.sent {
  background-color: #d0f0c0;
  margin-left: auto;
  text-align: right;
}
.received {
  background-color: #f1f1f1;
  margin-right: auto;
  text-align: left;
}
.timestamp {
  font-size: 0.75em;
  color: #999;
  text-align: right;
  margin-top: 5px;
}
.message-input {
  display: flex;
  gap: 10px;
}
.message-input input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  outline: none;
  transition: border 0.3s, background 0.3s, color 0.3s;
}
.message-input input:focus {
  border-color: #007bff;
}
.message-input button {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  background: #007bff;
  color: #fff;
  cursor: pointer;
  transition: background 0.3s;
}
.message-input button:hover {
  background: #0056b3;
}
/* Styles for the file box (WhatsApp-like) */
.file-attachment {
  margin-top: 10px;
}
.file-box,
.image-preview {
  cursor: pointer;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 8px;
  background: #f0f0f0;
  display: inline-flex;
  align-items: center;
}
.file-box:hover,
.image-preview:hover {
  background: #e0e0e0;
}
.file-icon {
  font-size: 1.5em;
  margin-right: 8px;
}
.file-name {
  font-size: 0.9em;
  color: #333;
}
.image-preview {
  max-width: 150px;
  max-height: 150px;
  overflow: hidden;
}
.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

/* Reply preview styles for composing a reply */
/* Removed "Replying to:" text and blue left border; now using different colours */
.reply-preview {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}
.sent-reply {
  background: #d0f0c0;
}
.received-reply {
  background: #f1f1f1;
}
.reply-text {
  flex: 1;
  font-size: 0.9em;
  color: #333;
}
.cancel-reply {
  cursor: pointer;
  font-size: 1.2em;
  padding: 0 5px;
  color: #999;
}

/* Reply snippet styles inside each message bubble */
.reply-snippet {
  margin-bottom: 5px;
  padding: 5px;
  border-radius: 4px;
  cursor: pointer;
}
.sent-reply-snippet {
  background: #cdeac0;
}
.received-reply-snippet {
  background: #e2e2e2;
}
.reply-snippet-text {
  font-size: 0.85em;
  color: #555;
}

/* Highlight style for temporary highlight */
.highlight {
  border: 2px solid #ffeb3b;
}

/* Dark Mode Styles */
.chat-container.dark .messages {
  background: #424242;
  border-color: #555;
}
.chat-container.dark .message {
  background: #555;
  color: #f5f5f5;
}
.chat-container.dark .sent {
  background-color: #388e3c;
}
.chat-container.dark .received {
  background-color: #616161;
}
.chat-container.dark .timestamp {
  color: #bbb;
}
.chat-container.dark .message-input input {
  background: #616161;
  border-color: #777;
  color: #f5f5f5;
}
.chat-container.dark .message-input button {
  background: #1e88e5;
}
.chat-container.dark .reply-preview {
  background: #333;
}
.chat-container.dark .reply-text {
  color: #f5f5f5;
}
.chat-container.dark .cancel-reply {
  color: #ccc;
}
/* Dark Mode Toggle Slider Styles */
.dark-mode-toggle {
  position: absolute;
  top: 10px;
  right: 20px;
  z-index: 10;
}
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 34px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: #2196f3;
}
input:checked + .slider:before {
  transform: translateX(26px);
}
</style>

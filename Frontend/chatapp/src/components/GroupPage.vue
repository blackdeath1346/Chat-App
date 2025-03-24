<template>
  <div :class="['chat-container', { dark: darkMode }]">
    <h2 class="chat-header">Group Chat: {{ groupName }}</h2>
    <div class="chat-content">
      <div class="messages-container">
        <div ref="messagesContainer" class="messages">
          <div
            v-for="msg in messages"
            :key="msg.timestamp"
            :class="{
              message: true,
              sent: msg.sender === currentUser,
              received: msg.sender !== currentUser,
            }"
          >
            <strong>{{ msg.sender }}</strong
            ><br />
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
                <span class="file-name">{{
                  extractFileName(msg.file_attachment)
                }}</span>
              </div>
            </div>
            <div class="timestamp">{{ formatTimestamp(msg.timestamp) }}</div>
          </div>
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
      <!-- Members Sidebar -->
      <div class="group-users">
        <h3>Members</h3>
        <ul>
          <li v-for="user in groupUsers" :key="user.username" class="member">
            <div class="avatar">
              {{ user.username.charAt(0).toUpperCase() }}
            </div>
            <div class="member-info">{{ user.username }}</div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import {
  getGroupMessages,
  getGroupName,
  getGroupUsers,
  postGroupMessage,
} from "../api/api.js";
import API from "../api/api.js";

export default {
  data() {
    return {
      currentUser: localStorage.getItem("currentUser") || "",
      groupName: "Loading...",
      groupUsers: [],
      messages: [],
      newMessage: "",
      selectedFile: null,
      socket: null,
      darkMode: false,
    };
  },
  computed: {
    group() {
      return this.$route.params.groupId; // Group ID from URL params
    },
  },
  async created() {
    if (!this.currentUser) {
      this.$router.push("/");
      return;
    }
    await this.fetchGroupName();
    await this.fetchMessages();
    await this.fetchGroupUsers();
    this.setupWebSocket();
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
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
      window.open(url, "_blank");
    },
    async fetchGroupName() {
      try {
        this.groupName = await getGroupName(
          `http://localhost:8000/Groups/${this.group}/`
        );
      } catch (error) {
        this.groupName = "Unknown Group";
      }
    },
    async fetchMessages() {
      try {
        let msgs = await getGroupMessages(this.group);
        msgs.forEach((msg) => {
          msg.sender = msg.sender.split("/").slice(-2, -1)[0];
        });
        this.messages = msgs;
        this.scrollToBottom();
      } catch (error) {
        alert("Error fetching group messages.");
      }
    },
    async fetchGroupUsers() {
      try {
        const users = await getGroupUsers(this.group);
        this.groupUsers = users;
      } catch (error) {
        console.error("Error fetching group users:", error);
      }
    },
    async setupWebSocket() {
      this.socket = new WebSocket(
        `ws://127.0.0.1:8000/ws/group/${this.group}/`
      );
      this.socket.onopen = () => console.log("WebSocket connected");
      this.socket.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        if (message.file_attachment) {
          setTimeout(async () => {
            try {
              const fileResponse = await API.get(message.file_attachment, {
                responseType: "blob",
              });
              message.file_attachment = URL.createObjectURL(fileResponse.data);
            } catch (error) {
              console.error("Error fetching file for message:", message, error);
            }
            this.messages.push(message);
            this.scrollToBottom();
          }, 500);
        } else {
          this.messages.push(message);
          this.scrollToBottom();
        }

        //this.messages.push(message);
        //this.scrollToBottom();
      };
      this.socket.onclose = () => console.log("WebSocket disconnected");
    },
    async sendMessage() {
      let content = this.selectedFile
        ? this.selectedFile.name
        : this.newMessage;
      if (!content.trim()) return;

      const groupID = `http://localhost:8000/Groups/${this.group}/`;
      const senderID = `http://localhost:8000/Users/${this.currentUser}/`;

      try {
        if (this.selectedFile) {
          // For a file message, use FormData and post directly.
          const formData = new FormData();
          formData.append("group", groupID);
          formData.append("sender", senderID);
          formData.append("content", content);
          formData.append("file_attachment", this.selectedFile);

          await API.post("/GroupMessages/", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });

          // Delay and re-fetch messages to update the file URL.
          setTimeout(() => {
            this.fetchMessages();
          }, 1000);
        } else {
          // For text-only messages, call the helper.
          await postGroupMessage(this.group, this.currentUser, content);
        }
        this.newMessage = "";
        this.selectedFile = null;
        this.$refs.fileInput.value = "";
      } catch (error) {
        console.error(error);
        alert("Error sending group message.");
      }
    },
    triggerFileSelect() {
      this.$refs.fileInput.click();
    },
    async handleFileChange(event) {
      const files = event.target.files;
      if (files.length > 0) {
        this.selectedFile = files[0];
        await this.sendMessage();
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
      if (typeof timestamp === "string" && timestamp.indexOf("T") === -1) {
        timestamp = timestamp.replace(" ", "T") + "+05:30";
      }
      return new Date(timestamp).toLocaleString("en-IN", {
        timeZone: "Asia/Kolkata",
      });
    },
  },
};
</script>

<style scoped>
/* Chat container */
.chat-container {
  max-width: 800px;
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
.chat-content {
  display: flex;
  gap: 20px;
}
.messages-container {
  flex: 2;
  display: flex;
  flex-direction: column;
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
  transition: border 0.3s;
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
/* File attachment styles */
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
/* Group users sidebar */
.group-users {
  flex: 1;
  max-width: 200px;
  background: #f7f7f7;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
}
.group-users h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.2em;
  color: #333;
  text-align: center;
}
.group-users ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.member {
  display: flex;
  align-items: center;
  background: #ffffff;
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}
.member:hover {
  transform: scale(1.02);
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #007bff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 10px;
  flex-shrink: 0;
}
.member-info {
  font-size: 1em;
  color: #333;
}
/* Dark Mode styles */
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
.chat-container.dark .group-users {
  background: #424242;
  border-color: #555;
}
.chat-container.dark .group-users h3 {
  color: #f5f5f5;
}
.chat-container.dark .member {
  background: #555;
  color: #f5f5f5;
}
.chat-container.dark .avatar {
  background: #1e88e5;
}
.chat-container.dark .member-info {
  color: #f5f5f5;
}
</style>

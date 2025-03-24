<template>
  <div :class="['home-container', { dark: darkMode }]">
    <!-- Dark Mode Toggle Slider -->
    <div class="dark-mode-toggle">
      <label class="switch">
        <input type="checkbox" v-model="darkMode" />
        <span class="slider round"></span>
      </label>
    </div>

    <h2 class="welcome">Welcome, {{ currentUser }}</h2>
    
    <!-- Action Buttons for Join and Create Group -->
    <div class="action-buttons">
      <button @click="openModal('join')">Join Group</button>
      <button @click="openModal('create')">Create Group</button>
    </div>
    
    <div class="content-container">
      <!-- Chat List -->
      <div class="column users-column">
        <h3>Your Chats</h3>
        <ul class="user-list">
          <li v-for="user in sortedUsers" :key="user" @click="goToChat(user)">
            {{ user }}
          </li>
        </ul>
      </div>
      
      <!-- Group List -->
      <div class="column groups-column">
        <h3>Your Groups</h3>
        <ul class="group-list">
          <!-- Global Chat always remains on top -->
          <li class="global-chat" @click="goToGlobalChat">Global Chat</li>
          <li v-for="(group, index) in sortedGroups" :key="index" @click="goToGroup(group.id)">
            {{ group.name || "Loading..." }}
          </li>
        </ul>
      </div>
    </div>
    
    <!-- Modal -->
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <h3>{{ modalType === 'join' ? 'Join a Group' : 'Create a Group' }}</h3>
        <div v-if="modalType === 'join'" class="modal-inputs">
          <input v-model="joinGroupId" placeholder="Enter Group ID" />
          <button @click="joinGroup">Join</button>
        </div>
        <div v-if="modalType === 'create'" class="modal-inputs">
          <input v-model="newGroupId" placeholder="Group ID" />
          <input v-model="newGroupName" placeholder="Group Name" />
          <button @click="createGroup">Create</button>
        </div>
        <button class="close-btn" @click="closeModal">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import { getUsers, getUserGroups, getGroupName, getGroupId, postGroupUser, postGroup } from "../api/api.js";

export default {
  data() {
    return {
      currentUser: localStorage.getItem("currentUser") || "",
      users: [],
      groups: [],
      joinGroupId: "",
      newGroupId: "",
      newGroupName: "",
      showModal: false,
      modalType: "",
      darkMode: false
    };
  },
  async created() {
    if (!this.currentUser) {
      this.$router.push("/");
      return;
    }
    await this.fetchData();
  },
  computed: {
    sortedUsers() {
      // Returns a sorted copy of the users array alphabetically
      return [...this.users].sort((a, b) => a.localeCompare(b));
    },
    sortedGroups() {
      // Returns a sorted copy of the groups array alphabetically by group name
      return [...this.groups].sort((a, b) => a.name.localeCompare(b.name));
    }
  },
  methods: {
    async fetchData() {
      try {
        const response = await getUsers(this.currentUser);
        if (response.error) {
          alert(response.error);
        } else {
          this.users = response;
        }

        const groupUrls = await getUserGroups(this.currentUser);
        const groupData = await Promise.all(
          groupUrls.map(async (url) => {
            const name = await getGroupName(url);
            return { id: getGroupId(url), name };
          })
        );
        this.groups = groupData;
      } catch (error) {
        alert("Error fetching users or groups.");
      }
    },
    async joinGroup() {
      if (!this.joinGroupId.trim()) {
        alert("Please enter a valid Group ID");
        return;
      }
      const response = await postGroupUser(this.joinGroupId, this.currentUser);
      if (response.error) {
        alert(response.error);
      } else {
        alert("Joined group successfully!");
        this.fetchData();
        this.closeModal();
      }
    },
    async createGroup() {
      if (!this.newGroupId.trim() || !this.newGroupName.trim()) {
        alert("Please enter valid Group ID and Name");
        return;
      }
      const response = await postGroup(this.currentUser, this.newGroupId, this.newGroupName);
      if (response.error) {
        alert(response.error);
      } else {
        alert("Group created successfully!");
        await postGroupUser(this.newGroupId, this.currentUser);
        this.fetchData();
        this.closeModal();
      }
    },
    openModal(type) {
      this.modalType = type;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    goToChat(username) {
      this.$router.push(`/chat/${username}`);
    },
    goToGroup(groupId) {
      this.$router.push(`/group/${groupId}`);
    },
    goToGlobalChat() {
      this.$router.push("/global-chat");
    }
  }
};
</script>

<style scoped>
.home-container {
  text-align: center;
  margin: 20px auto;
  max-width: 900px;
  background: #ffffff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  position: relative;
  color: #000;
}

.welcome {
  margin-bottom: 10px;
}

.action-buttons {
  margin-bottom: 20px;
}
.action-buttons button {
  padding: 12px;
  border-radius: 8px;
  margin: 5px;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}
.action-buttons button:hover {
  background: #0056b3;
}

.content-container {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.column {
  flex: 1;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.user-list, .group-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.user-list li, .group-list li {
  cursor: pointer;
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  background: #e3f2fd;
  transition: background 0.3s;
}
.user-list li:hover, .group-list li:hover {
  background: #bbdefb;
}

/* Global Chat specific styles */
.global-chat {
  background: #ffa726;
  color: white;
  font-weight: bold;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: background 0.3s;
}
.global-chat:hover {
  background: #fb8c00;
}

/* Modal Styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
  width: 90%;
  max-width: 400px;
  text-align: center;
}
.modal-content h3 {
  margin-bottom: 20px;
}
.modal-inputs {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}
.modal-inputs input {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
}
.modal-inputs button {
  padding: 12px;
  border-radius: 8px;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}
.modal-inputs button:hover {
  background: #0056b3;
}
.close-btn {
  padding: 12px;
  border-radius: 8px;
  background: #dc3545;
  color: white;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}
.close-btn:hover {
  background: #c82333;
}

/* Dark Mode Styles */
.home-container.dark {
  background: #2c2c2c;
  color: #f5f5f5;
}
.home-container.dark .action-buttons button {
  background: #1e88e5;
}
.home-container.dark .action-buttons button:hover {
  background: #1565c0;
}
.home-container.dark .column {
  background: #424242;
  box-shadow: 0 2px 6px rgba(255, 255, 255, 0.15);
}
.home-container.dark .user-list li, 
.home-container.dark .group-list li {
  background: #616161;
  color: #f5f5f5;
}
.home-container.dark .user-list li:hover, 
.home-container.dark .group-list li:hover {
  background: #757575;
}
.home-container.dark .global-chat {
  background: #fb8c00;
}
.home-container.dark .global-chat:hover {
  background: #f57c00;
}
.home-container.dark .modal-content {
  background: #424242;
  color: #f5f5f5;
}
.home-container.dark .modal-inputs input {
  background: #616161;
  color: #f5f5f5;
  border: 1px solid #757575;
}
.home-container.dark .modal-inputs button {
  background: #1e88e5;
}
.home-container.dark .modal-inputs button:hover {
  background: #1565c0;
}
.home-container.dark .close-btn {
  background: #e53935;
}
.home-container.dark .close-btn:hover {
  background: #c62828;
}

/* Dark Mode Toggle Slider Styles */
.dark-mode-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1100;
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
  background-color: #2196F3;
}

input:checked + .slider:before {
  transform: translateX(26px);
}
</style>

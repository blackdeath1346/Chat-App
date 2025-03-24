<template>
  <div id="app">
    <h1>User Management</h1>
    <form @submit.prevent="handleFetchUsers">
      <label for="username">Enter your username:</label>
      <input v-model="username" type="text" id="username" placeholder="Username" required />
      <button type="submit">Fetch Users</button>
    </form>

    <div v-if="otherUsers.length > 0">
      <h2>Other Users</h2>
      <ul>
        <li v-for="user in otherUsers" :key="user.id">{{ user.username }}</li>
      </ul>
    </div>

    <div v-else-if="fetched">
      <p>No other users found.</p>
    </div>
  </div>
</template>

<script>
import API from "../api/api";

export default {
  name: "App",
  data() {
    return {
      username: "", // The username input by the user
      otherUsers: [], // Array to store users except the current one
      fetched: false, // Flag to track if users were fetched
    };
  },
  methods: {
    async handleFetchUsers() {
      try {
        // Ensure the user has entered a username
        if (!this.username.trim()) {
          alert("Please enter a username.");
          return;
        }

        // Fetch all users from the database, excluding the entered username
        const allUsers = await API.getUsersExcept(this.username);

        if (!allUsers || allUsers.length === 0) {
          alert("No users found in the database.");
          return;
        }

        // Filter users (this is redundant here as the API already filters, but kept for clarity)
        this.otherUsers = allUsers;
      } catch (error) {
        console.error("Error fetching users:", error);
        alert("Failed to fetch users. Check the console for details.");
      } finally {
        this.fetched = true; // Mark as fetched
      }
    },
  },
};
</script>


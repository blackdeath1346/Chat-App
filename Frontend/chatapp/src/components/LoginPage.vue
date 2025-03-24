<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Welcome</h2>
      <p>Please sign in or sign up to continue</p>
      <input v-model="username" type="text" placeholder="Enter your username" />
      <button @click="login">Login / Signup</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { addUser } from "../api/api.js";

export default {
  data() {
    return {
      username: "",
    };
  },
  methods: {
    async login() {
      if (!this.username.trim()) {
        alert("Username is required");
        return;
      }
      try {
        // Fetch existing users
        const response = await axios.get("http://localhost:8000/Users/");
        const users = response.data;
        const userExists = users.some((user) => user.username === this.username);
        
        // If user doesn't exist, sign them up
        if (!userExists) {
          const signupResponse = await addUser(this.username, this.username);
          if (signupResponse.error) {
            alert(signupResponse.error);
            return;
          }
        }
        
        // Store username and navigate to home
        localStorage.setItem("currentUser", this.username);
        this.$router.push("/home");
      } catch (error) {
        console.error("Error during login/signup:", error);
        alert("An error occurred. Please try again.");
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  /* Background gradient for a modern look */
  background: linear-gradient(135deg, #74ebd5, #acb6e5);
}

.login-card {
  background: #ffffff;
  padding: 40px 60px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 350px;
}

.login-card h2 {
  margin-bottom: 10px;
  font-size: 2em;
  color: #333;
}

.login-card p {
  margin-bottom: 20px;
  color: #777;
  font-size: 0.9em;
}

.login-card input {
  width: 100%;
  padding: 12px 16px;
  margin-bottom: 20px;
  border: 2px solid #eee;
  border-radius: 6px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.login-card input:focus {
  border-color: #74ebd5;
  outline: none;
}

.login-card button {
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-radius: 6px;
  background: #74ebd5;
  color: #fff;
  font-size: 1em;
  cursor: pointer;
  transition: background 0.3s ease;
}

.login-card button:hover {
  background: #67d5bd;
}
</style>

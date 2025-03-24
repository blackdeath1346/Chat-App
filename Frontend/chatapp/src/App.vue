<template>
  <div id="app" :class="{ dark: darkMode }">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>
      <!-- Dark Mode Toggle in the nav -->
      <div class="dark-mode-toggle">
        <label class="switch">
          <input type="checkbox" v-model="darkMode" />
          <span class="slider round"></span>
        </label>
      </div>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  data() {
    return {
      darkMode: false
    };
  },
  watch: {
    darkMode(newVal) {
      // Optionally update the body background color too
      document.body.style.backgroundColor = newVal ? "#2c2c2c" : "#ffffff";
    }
  },
  created() {
    // Set initial body background to match the default dark mode value
    document.body.style.backgroundColor = this.darkMode ? "#2c2c2c" : "#ffffff";
  }
};
</script>

<style>
/* Global container styling */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  background-color: #ffffff;
  transition: background-color 0.3s, color 0.3s;
  min-height: 100vh;
}

/* When dark mode is active on the #app container */
#app.dark {
  background-color: #2c2c2c;
  color: #f5f5f5;
}

nav {
  padding: 30px;
  position: relative;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

#app.dark nav a {
  color: #f5f5f5;
}

nav a.router-link-exact-active {
  color: #42b983;
}

/* Dark Mode Toggle Slider Styles */
.dark-mode-toggle {
  position: absolute;
  top: 10px;
  right: 20px;
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

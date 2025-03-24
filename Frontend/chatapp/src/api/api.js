import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

// Fetch messages for a chat between two users
export const getChat = async (sender, receiver) => {
  try {
    console.log("fetching2");
    
    const [user1, user2] = [sender, receiver].sort();
    const chatId = `http://localhost:8000/Chats/${user1}-${user2}/`;
    const senderID = `http://localhost:8000/Users/${sender}/`;
    const receiverID = `http://localhost:8000/Users/${receiver}/`;
    console.log(senderID);
    
    const response = await API.get(`/Messages/`);
    
    let messages = response.data.filter(msg => msg.chat === chatId);
    console.log(messages);
    
    // Sort messages by timestamp
    messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // For each message with a file_attachment URL, fetch the file content
    messages = await Promise.all(messages.map(async msg => {
      if (msg.file_attachment) {
        try {
          const fileResponse = await API.get(msg.file_attachment, { responseType: 'blob' });
          msg.file_attachment = URL.createObjectURL(fileResponse.data);
        } catch (error) {
          console.error("Error fetching file for message:", msg, error);
        }
      }
      return msg;
    }));
    
    const receiverMessages = messages.filter(msg => msg.sender === receiverID);
    const senderMessages = messages.filter(msg => msg.sender === senderID);
    console.log(receiverMessages);
    console.log(senderMessages);
    return { senderMessages, receiverMessages };
  } catch (error) {
    console.error("Error fetching chat messages:", error);
    throw error;
  }
};

// Post a new message in a chat
export const postChat = async (sender, receiver, message, fileUrl = null, replyTo = null) => {
  try {
    const [user1, user2] = [sender, receiver].sort();
    const chatId = `http://localhost:8000/Chats/${user1}-${user2}/`;
    const senderID = `http://localhost:8000/Users/${sender}/`;
    
    // Build the payload and include the file_attachment and reply_to if provided
    const payload = {
      chat: chatId,
      sender: senderID,
      content: message,
    };
    
    if (fileUrl) {
      payload.file_attachment = fileUrl;
    }
    if (replyTo) {
      payload.reply_to = replyTo;
    }
    
    const response = await API.post("/Messages/", payload);
    return response.data;
  } catch (error) {
    console.error("Error posting chat message:", error);
    throw error;
  }
};

// Add a new user if username is not taken
export const addUser = async (name, username) => {
  try {
    const response = await API.get("/Users/");
    const existingUsernames = response.data.map(user => user.username);
    
    if (existingUsernames.includes(username)) {
      return { error: "User already exists" };
    }
    
    const newUser = await API.post("/Users/", { name, username });
    return newUser.data;
  } catch (error) {
    console.error("Error adding user:", error);
    throw error;
  }
};

// Get all users except the given username
export const getUsers = async (username) => {
  try {
    const response = await API.get("/Users/");
    const users = response.data.filter(user => user.username !== username);
    
    if (users.length === 0) {
      return { error: "No other users found. Add users first." };
    }
    
    return users.map(user => user.username);
  } catch (error) {
    console.error("Error fetching users:", error);
    throw error;
  }
};

// 1. Get all groups a user is part of
export const getUserGroups = async (userId) => {
  try {
    console.log("In api.js");
    console.log(userId);
    const response = await API.get("/GroupUsers/");
    const userGroups = response.data.filter(entry => entry.user === `http://localhost:8000/Users/${userId}/`);
    
    const groupIds = userGroups.map(entry => entry.group);
    return groupIds;
  } catch (error) {
    console.error("Error fetching user groups:", error);
    throw error;
  }
};

// 2. Get all messages for a given group ID, sorted by timestamp
export const getGroupMessages = async (groupId) => {
  try {
    const response = await API.get("/GroupMessages/");
    let groupMessages = response.data.filter(
      msg => msg.group === `http://localhost:8000/Groups/${groupId}/`
    );
    
    groupMessages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // For each group message with a file_attachment URL, fetch the file content
    groupMessages = await Promise.all(groupMessages.map(async msg => {
      if (msg.file_attachment) {
        try {
          const fileResponse = await API.get(msg.file_attachment, { responseType: 'blob' });
          msg.file_attachment = URL.createObjectURL(fileResponse.data);
        } catch (error) {
          console.error("Error fetching file for group message:", msg, error);
        }
      }
      return msg;
    }));
    
    return groupMessages;
  } catch (error) {
    console.error("Error fetching group messages:", error);
    throw error;
  }
};

// 3. Post a message to a group (modified to handle file attachments and reply_to)
export const postGroupMessage = async (groupId, sender, message, fileUrl = null, replyTo = null) => {
  try {
    const senderID = `http://localhost:8000/Users/${sender}/`;
    const groupID = `http://localhost:8000/Groups/${groupId}/`;
    
    const payload = {
      group: groupID,
      sender: senderID,
      content: message,
    };
    
    if (fileUrl) {
      payload.file_attachment = fileUrl;
    }
    if (replyTo) {
      payload.reply_to = replyTo;
    }
    
    const response = await API.post("/GroupMessages/", payload);
    return response.data;
  } catch (error) {
    console.error("Error posting group message:", error);
    throw error;
  }
};

export const getGroupName = async (groupUrl) => {
  try {
    const response = await API.get(groupUrl);
    return response.data.name; // Assuming the response has a "name" attribute
  } catch (error) {
    console.error("Error fetching group name:", error);
    throw error;
  }
};

// Extract group ID from a given group URL
export const getGroupId = (groupUrl) => {
  const parts = groupUrl.split("/");
  return parts[parts.length - 2]; // Extract ID from the URL pattern
};

export const postGroupUser = async (groupId, userId) => {
  try {
    const groupResponse = await API.get(`/Groups/${groupId}/`);
    if (!groupResponse.data) {
      throw new Error("Group does not exist.");
    }

    const response = await API.post("/GroupUsers/", {
      group: `http://localhost:8000/Groups/${groupId}/`,
      user: `http://localhost:8000/Users/${userId}/`,
    });
    return response.data;
  } catch (error) {
    console.error("Error adding user to group:", error);
    throw error;
  }
};

// Function to create a new group with a unique group ID
export const postGroup = async (userId, groupId, groupName) => {
  try {
    const groupResponse = await API.get("/Groups/");
    const existingGroup = groupResponse.data.find(group => group.id === groupId);
    
    if (existingGroup) {
      throw new Error("Group ID already exists. Please choose another ID.");
    }
    console.log("called here");
    console.log(groupName);
    console.log(groupId);
    const response = await API.post("/Groups/", {
      id: groupId,
      name: groupName,
      admin: `http://localhost:8000/Users/${userId}/`,
    });
    return response.data;
  } catch (error) {
    console.error("Error creating group:", error);
    throw error;
  }
};

export const getGroupUsers = async (groupId) => {
  try {
    const response = await API.get("/GroupUsers/");
    const groupEntries = response.data.filter(
      (entry) => entry.group === `http://localhost:8000/Groups/${groupId}/`
    );
    const userUrls = groupEntries.map((entry) => entry.user);
    const userPromises = userUrls.map((url) => API.get(url));
    const userResponses = await Promise.all(userPromises);
    return userResponses.map((res) => res.data);
  } catch (error) {
    console.error("Error fetching group users:", error);
    throw error;
  }
};

export const getGlobalMessages = async () => {
  try {
    const response = await API.get("/CommonMessages/");
    return response.data;
  } catch (error) {
    console.error("Error fetching global messages:", error);
    return [];
  }
};

// 🔹 Post a new global message
export const postGlobalMessage = async (sender, content) => {
  try {
    const senderID = `http://localhost:8000/Users/${sender}/`;
    await API.post("/CommonMessages/", { sender: senderID, content: content });
  } catch (error) {
    console.error("Error posting global message:", error);
  }
};

// New function: Given a message URL, fetch and return its content.
export const getMessageContent = async (messageUrl) => {
  try {
    const response = await API.get(messageUrl);
    return response.data.content;
  } catch (error) {
    console.error("Error fetching message content:", error);
    throw error;
  }
};

export default API;

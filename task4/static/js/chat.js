/**
 * Real-time chat WebSocket client with file sharing
 */
(function () {
  if (typeof ROOM_ID === "undefined") return;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/chat/${ROOM_ID}/`;
  const messagesEl = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const statusEl = document.getElementById("connection-status");
  const fileInput = document.getElementById("file-input");
  const fileList = document.getElementById("file-list");

  let socket = null;
  let reconnectTimer = null;

  function getCsrfToken() {
    const cookie = document.cookie
      .split(";")
      .map((c) => c.trim())
      .find((c) => c.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }

  function setStatus(state) {
    if (!statusEl) return;
    statusEl.className = "connection-status " + state;
    statusEl.textContent =
      state === "connected"
        ? "Connected"
        : state === "disconnected"
        ? "Disconnected"
        : "Connecting...";
  }

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function appendMessage(data) {
    const isOwn = data.username === CURRENT_USER;
    const div = document.createElement("div");
    div.className = `message ${isOwn ? "message-own" : "message-other"}`;
    div.innerHTML = `
      <div class="message-header">
        <span class="message-author">${escapeHtml(data.username)}</span>
        <span class="message-time">${data.timestamp || ""}</span>
      </div>
      <div class="message-body">${escapeHtml(data.message)}</div>
    `;
    messagesEl.appendChild(div);
    scrollToBottom();
  }

  function appendFileMessage(data) {
    const isOwn = data.username === CURRENT_USER;
    const div = document.createElement("div");
    div.className = `message message-file ${isOwn ? "message-own" : "message-other"}`;
    div.innerHTML = `
      <div class="message-header">
        <span class="message-author">${escapeHtml(data.username)}</span>
        <span class="message-time">${data.timestamp || ""}</span>
      </div>
      <div class="message-body">
        📎 <a href="${escapeHtml(data.url)}" target="_blank" download>${escapeHtml(data.filename)}</a>
      </div>
    `;
    messagesEl.appendChild(div);
    scrollToBottom();
    addFileToList(data);
  }

  function appendSystemMessage(text) {
    const div = document.createElement("div");
    div.className = "message message-system";
    div.textContent = text;
    messagesEl.appendChild(div);
    scrollToBottom();
  }

  function addFileToList(data) {
    if (!fileList) return;
    const empty = document.getElementById("no-files-msg");
    if (empty) empty.remove();

    const li = document.createElement("li");
    li.className = "file-item";
    li.innerHTML = `
      <a href="${escapeHtml(data.url)}" target="_blank" download>${escapeHtml(data.filename)}</a>
      <span class="file-meta">${escapeHtml(data.username)} · just now</span>
    `;
    fileList.prepend(li);
  }

  async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    const resp = await fetch(UPLOAD_URL, {
      method: "POST",
      headers: { "X-CSRFToken": getCsrfToken() },
      body: formData,
    });

    const data = await resp.json();
    if (!resp.ok) {
      appendSystemMessage(data.error || "Upload failed.");
      return;
    }

    appendFileMessage(data);
  }

  function connect() {
    setStatus("connecting");
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setStatus("connected");
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case "chat_message":
          appendMessage(data);
          break;
        case "file_shared":
          if (data.username !== CURRENT_USER) {
            appendFileMessage(data);
          }
          break;
        case "user_join":
          if (data.username !== CURRENT_USER) {
            appendSystemMessage(`${data.username} joined the room`);
          }
          break;
        case "user_leave":
          appendSystemMessage(`${data.username} left the room`);
          break;
      }
    };

    socket.onclose = () => {
      setStatus("disconnected");
      reconnectTimer = setTimeout(connect, 3000);
    };

    socket.onerror = () => socket.close();
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message || !socket || socket.readyState !== WebSocket.OPEN) return;
    socket.send(JSON.stringify({ type: "chat_message", message }));
    chatInput.value = "";
    chatInput.focus();
  });

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      if (file) uploadFile(file);
      fileInput.value = "";
    });
  }

  scrollToBottom();
  connect();
})();

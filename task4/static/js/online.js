/**
 * Online users presence via WebSocket
 */
(function () {
  const userList = document.getElementById("user-list");
  if (!userList) return;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/online/`;
  const onlineUsers = new Set();

  function updateUserStatus(username, isOnline) {
    const items = userList.querySelectorAll(`[data-username="${username}"]`);
    items.forEach((item) => {
      const dot = item.querySelector(".status-dot");
      if (dot) {
        dot.classList.toggle("online", isOnline);
        dot.classList.toggle("offline", !isOnline);
      }
      item.classList.toggle("online", isOnline);
    });
  }

  function connect() {
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case "user_online":
          onlineUsers.add(data.username);
          updateUserStatus(data.username, true);
          break;
        case "user_offline":
          onlineUsers.delete(data.username);
          updateUserStatus(data.username, false);
          break;
        case "online_list":
          data.users.forEach((u) => {
            onlineUsers.add(u);
            updateUserStatus(u, true);
          });
          break;
      }
    };

    socket.onclose = () => {
      setTimeout(connect, 5000);
    };
  }

  connect();
})();

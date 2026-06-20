/**
 * WebRTC client — audio calls, video calls, and screen sharing
 */
(function () {
  if (typeof ROOM_ID === "undefined") return;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/call/${ROOM_ID}/`;
  const isVideo = CALL_TYPE === "video";

  const localVideo = document.getElementById("local-video");
  const localTile = document.getElementById("local-tile");
  const videoGrid = document.getElementById("video-grid");
  const statusEl = document.getElementById("call-status");
  const participantsList = document.getElementById("participants-list");
  const participantCount = document.getElementById("participant-count");
  const btnMute = document.getElementById("btn-mute");
  const btnVideo = document.getElementById("btn-video");
  const btnScreen = document.getElementById("btn-screen");
  const btnHangup = document.getElementById("btn-hangup");

  let socket = null;
  let localStream = null;
  let cameraStream = null;
  let screenSharing = false;
  let muted = false;
  let videoEnabled = true;
  const peers = {};
  const knownUsers = new Set([CURRENT_USER]);

  const rtcConfig = {
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
  };

  function setStatus(text, state) {
    statusEl.textContent = text;
    statusEl.className = "connection-status " + (state || "");
  }

  function updateParticipantCount() {
    participantCount.textContent = knownUsers.size;
  }

  function addParticipant(username) {
    if (knownUsers.has(username)) return;
    knownUsers.add(username);
    updateParticipantCount();

    const li = document.createElement("li");
    li.className = "user-item online";
    li.id = `participant-${username}`;
    li.innerHTML = `
      <span class="status-dot online"></span>
      <span class="user-name">${username}</span>
    `;
    participantsList.appendChild(li);
  }

  function removeParticipant(username) {
    knownUsers.delete(username);
    updateParticipantCount();
    document.getElementById(`participant-${username}`)?.remove();
    removePeer(username);
  }

  function createVideoTile(username) {
    const tile = document.createElement("div");
    tile.className = "video-tile remote-tile";
    tile.id = `tile-${username}`;
    tile.innerHTML = `
      <video id="video-${username}" autoplay playsinline></video>
      <span class="video-label">${username}</span>
    `;
    videoGrid.appendChild(tile);
    return document.getElementById(`video-${username}`);
  }

  function removePeer(username) {
    if (peers[username]) {
      peers[username].close();
      delete peers[username];
    }
    document.getElementById(`tile-${username}`)?.remove();
  }

  function createPeerConnection(username, isInitiator) {
    if (peers[username]) return peers[username];

    const pc = new RTCPeerConnection(rtcConfig);
    peers[username] = pc;

    localStream.getTracks().forEach((track) => {
      pc.addTrack(track, localStream);
    });

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        sendSignal({
          type: "ice-candidate",
          target: username,
          candidate: event.candidate,
        });
      }
    };

    pc.ontrack = (event) => {
      let videoEl = document.getElementById(`video-${username}`);
      if (!videoEl) {
        videoEl = createVideoTile(username);
      }
      videoEl.srcObject = event.streams[0];
    };

    pc.onconnectionstatechange = () => {
      if (pc.connectionState === "failed" || pc.connectionState === "disconnected") {
        removePeer(username);
      }
    };

    if (isInitiator) {
      pc.createOffer()
        .then((offer) => pc.setLocalDescription(offer))
        .then(() => {
          sendSignal({
            type: "offer",
            target: username,
            sdp: pc.localDescription,
          });
        })
        .catch(console.error);
    }

    return pc;
  }

  function sendSignal(data) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(data));
    }
  }

  async function handleOffer(data) {
    const pc = createPeerConnection(data.sender, false);
    await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    sendSignal({ type: "answer", target: data.sender, sdp: pc.localDescription });
  }

  async function handleAnswer(data) {
    const pc = peers[data.sender];
    if (pc) {
      await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
    }
  }

  async function handleIceCandidate(data) {
    const pc = peers[data.sender];
    if (pc && data.candidate) {
      await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
    }
  }

  function connectSignaling() {
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setStatus("Connected", "connected");
      sendSignal({ type: "join", callType: CALL_TYPE });
    };

    socket.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "participants":
          data.users.forEach((username) => {
            addParticipant(username);
            createPeerConnection(username, true);
          });
          break;
        case "join":
          addParticipant(data.sender);
          if (data.sender !== CURRENT_USER) {
            createPeerConnection(data.sender, true);
          }
          break;
        case "leave":
          removeParticipant(data.sender);
          break;
        case "offer":
          await handleOffer(data);
          break;
        case "answer":
          await handleAnswer(data);
          break;
        case "ice-candidate":
          await handleIceCandidate(data);
          break;
      }
    };

    socket.onclose = () => setStatus("Disconnected", "disconnected");
  }

  async function startLocalMedia() {
    const constraints = isVideo
      ? { audio: true, video: { width: 640, height: 480 } }
      : { audio: true, video: false };

    try {
      localStream = await navigator.mediaDevices.getUserMedia(constraints);
      cameraStream = localStream;

      if (isVideo && localVideo) {
        localVideo.srcObject = localStream;
      } else if (localTile) {
        localTile.classList.add("audio-only");
      }
    } catch (err) {
      setStatus("Microphone access denied", "disconnected");
      console.error(err);
    }
  }

  function toggleMute() {
    if (!localStream) return;
    muted = !muted;
    localStream.getAudioTracks().forEach((t) => (t.enabled = !muted));
    btnMute.classList.toggle("ctrl-active", muted);
    btnMute.textContent = muted ? "🔇" : "🎙️";
  }

  function toggleVideo() {
    if (!localStream || !isVideo) return;
    videoEnabled = !videoEnabled;
    localStream.getVideoTracks().forEach((t) => (t.enabled = videoEnabled));
    btnVideo.classList.toggle("ctrl-active", !videoEnabled);
    localTile.classList.toggle("video-off", !videoEnabled);
  }

  async function toggleScreenShare() {
    if (!isVideo) return;

    if (screenSharing) {
      const videoTrack = cameraStream.getVideoTracks()[0];
      localStream.removeTrack(localStream.getVideoTracks()[0]);
      localStream.addTrack(videoTrack);
      localVideo.srcObject = localStream;
      Object.values(peers).forEach((pc) => {
        const sender = pc.getSenders().find((s) => s.track?.kind === "video");
        if (sender) sender.replaceTrack(videoTrack);
      });
      screenSharing = false;
      btnScreen.classList.remove("ctrl-active");
    } else {
      try {
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
        });
        const screenTrack = screenStream.getVideoTracks()[0];
        const oldTrack = localStream.getVideoTracks()[0];
        localStream.removeTrack(oldTrack);
        localStream.addTrack(screenTrack);
        localVideo.srcObject = localStream;

        Object.values(peers).forEach((pc) => {
          const sender = pc.getSenders().find((s) => s.track?.kind === "video");
          if (sender) sender.replaceTrack(screenTrack);
        });

        screenTrack.onended = () => {
          if (screenSharing) toggleScreenShare();
        };

        screenSharing = true;
        btnScreen.classList.add("ctrl-active");
      } catch (err) {
        console.error("Screen share cancelled:", err);
      }
    }
  }

  function hangUp() {
    sendSignal({ type: "leave" });
    Object.keys(peers).forEach(removePeer);
    localStream?.getTracks().forEach((t) => t.stop());
    socket?.close();
    window.location.href = `/room/${ROOM_ID}/`;
  }

  btnMute?.addEventListener("click", toggleMute);
  btnVideo?.addEventListener("click", toggleVideo);
  btnScreen?.addEventListener("click", toggleScreenShare);
  btnHangup?.addEventListener("click", hangUp);

  window.addEventListener("beforeunload", () => {
    sendSignal({ type: "leave" });
  });

  startLocalMedia().then(connectSignaling);
})();

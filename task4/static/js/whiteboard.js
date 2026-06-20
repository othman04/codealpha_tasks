/**
 * Collaborative whiteboard — real-time drawing via WebSocket
 */
(function () {
  if (typeof ROOM_ID === "undefined") return;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/whiteboard/${ROOM_ID}/`;

  const canvas = document.getElementById("whiteboard-canvas");
  const ctx = canvas.getContext("2d");
  const statusEl = document.getElementById("wb-status");
  const colorInput = document.getElementById("wb-color");
  const sizeInput = document.getElementById("wb-size");
  const sizeVal = document.getElementById("wb-size-val");
  const btnPen = document.getElementById("wb-pen");
  const btnEraser = document.getElementById("wb-eraser");
  const btnClear = document.getElementById("wb-clear");

  let socket = null;
  let drawing = false;
  let isEraser = false;
  let lastX = 0;
  let lastY = 0;
  let allStrokes = [];

  function setStatus(text, state) {
    statusEl.textContent = text;
    statusEl.className = "connection-status " + (state || "");
  }

  function resizeCanvas() {
    const wrapper = canvas.parentElement;
    const rect = wrapper.getBoundingClientRect();
    canvas.width = rect.width - 2;
    canvas.height = Math.max(500, window.innerHeight - 280);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    redrawHistory(allStrokes);
  }

  function drawStroke(stroke, emit) {
    ctx.beginPath();
    ctx.strokeStyle = stroke.color;
    ctx.lineWidth = stroke.size;
    ctx.globalCompositeOperation = stroke.eraser ? "destination-out" : "source-over";
    ctx.moveTo(stroke.x0, stroke.y0);
    ctx.lineTo(stroke.x1, stroke.y1);
    ctx.stroke();
    ctx.globalCompositeOperation = "source-over";

    if (emit) {
      allStrokes.push(stroke);
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "draw", stroke }));
      }
    }
  }

  function redrawHistory(strokes) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    strokes.forEach((s) => drawStroke(s, false));
  }

  function getPointerPos(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
  }

  function startDraw(e) {
    e.preventDefault();
    drawing = true;
    const pos = getPointerPos(e);
    lastX = pos.x;
    lastY = pos.y;
  }

  function draw(e) {
    if (!drawing) return;
    e.preventDefault();
    const pos = getPointerPos(e);
    const stroke = {
      x0: lastX,
      y0: lastY,
      x1: pos.x,
      y1: pos.y,
      color: isEraser ? "#000000" : colorInput.value,
      size: isEraser ? parseInt(sizeInput.value) * 3 : parseInt(sizeInput.value),
      eraser: isEraser,
    };
    drawStroke(stroke, true);
    lastX = pos.x;
    lastY = pos.y;
  }

  function stopDraw() {
    drawing = false;
  }

  function connect() {
    socket = new WebSocket(wsUrl);

    socket.onopen = () => setStatus("Connected", "connected");

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "history") {
        allStrokes = data.strokes;
        redrawHistory(allStrokes);
      } else if (data.type === "draw") {
        allStrokes.push(data.stroke);
        drawStroke(data.stroke, false);
      } else if (data.type === "clear") {
        allStrokes = [];
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    };

    socket.onclose = () => setStatus("Disconnected", "disconnected");
  }

  canvas.addEventListener("mousedown", startDraw);
  canvas.addEventListener("mousemove", draw);
  canvas.addEventListener("mouseup", stopDraw);
  canvas.addEventListener("mouseleave", stopDraw);
  canvas.addEventListener("touchstart", startDraw, { passive: false });
  canvas.addEventListener("touchmove", draw, { passive: false });
  canvas.addEventListener("touchend", stopDraw);

  sizeInput.addEventListener("input", () => {
    sizeVal.textContent = sizeInput.value;
  });

  btnPen.addEventListener("click", () => {
    isEraser = false;
    btnPen.classList.add("tool-active");
    btnEraser.classList.remove("tool-active");
  });

  btnEraser.addEventListener("click", () => {
    isEraser = true;
    btnEraser.classList.add("tool-active");
    btnPen.classList.remove("tool-active");
  });

  btnClear.addEventListener("click", () => {
    if (!confirm("Clear the entire whiteboard for everyone?")) return;
    allStrokes = [];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "clear" }));
    }
  });

  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();
  connect();
})();

# Real-Time Communication App (TASK 4)

A video conferencing and collaboration tool built with **Django**, **Django Channels**, and **WebSockets**. This project follows a phased roadmap — **Version 1 (MVP)** is fully implemented.

## Features
- User registration and login
- Real-time chat via WebSockets
- Room creation and listing
- Online user presence
- File sharing
- Audio calls (WebRTC
- Video calls
- Screen sharing
- Collaborative whiteboard

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Django 5, Django Channels |
| Real-time  | WebSockets              |
| Frontend   | HTML, CSS, JavaScript   |
| Video      | WebRTC (v2/v3)          |
| Database   | SQLite (dev)            |

## Project Structure

```
realtime_app/
├── accounts/       # Authentication (login, register)
├── chat/           # Rooms, messages, WebSocket chat
├── calls/          # WebRTC signaling (v2/v3)
├── whiteboard/     # Collaborative whiteboard (v3)
├── config/         # Django settings, ASGI routing
├── templates/      # HTML templates (English UI)
└── static/         # CSS & JavaScript
```

## Architecture

```
Browser → JavaScript → WebSocket → Django Channels → Database
```

For video calls (v2/v3):

```
User A ←── WebRTC ──→ User B
         ↑           ↑
    Django Channels (signaling)
```

## Quick Start

### 1. Create a virtual environment

```bash
py -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
py manage.py migrate
```

### 4. Create a superuser (optional)

```bash
py manage.py createsuperuser
```

### 5. Start the server

```bash
py manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Pages

| URL              | Description              |
|------------------|--------------------------|
| `/login`         | Sign in                  |
| `/register`      | Create account           |
| `/rooms`         | List rooms & users       |
| `/room/<id>`     | Real-time chat room      |
| `/call/<id>`     | Call page (v2/v3)        |

## Models

- **Room** — `name`, `created_by`, `created_at`
- **Message** — `room`, `sender`, `content`, `created_at`
- **File** — `room`, `sender`, `file`, `created_at` (v2)

## Testing Real-Time Chat

1. Open two browser windows (or use incognito mode).
2. Register two different users.
3. Create a room with one user.
4. Join the same room with the other user.
5. Send messages — they appear instantly via WebSocket.

## WebSocket Endpoints

| Endpoint                  | Purpose              |
|---------------------------|----------------------|
| `ws/chat/<room_id>/`      | Room chat messages   |
| `ws/online/`              | User presence        |
| `ws/call/<room_id>/`      | WebRTC signaling (v2/v3) |

## License

Educational project — TASK 4.

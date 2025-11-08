# 🚁 ParrotAI Terminal Chat Client

Simple terminal-based chat client to test the FastAPI WebSocket server.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

1. **Start the FastAPI server** (from the Olympe-web-server directory):
```bash
python fastapi_entrypoint.py
```

2. **Run the chat client**:
```bash
python chat_client.py
```

3. **Send messages**:
Type natural language messages to interact with the drone AI:
```
You: go inspect the tower
You: fly to the industrial zone
You: return to base
```

4. **Exit**:
Type `quit`, `exit`, or `q` to disconnect

## Features

- 🔌 Real-time WebSocket connection
- 📤 Send natural language messages
- 📨 Receive mission DSL and responses
- 🎨 Color-coded terminal output
- 🚁 Display drone mission confirmations
- ⚠️ Error handling and display

## Message Format

The client automatically formats messages as:
```json
{
    "id": "msg-xxx",
    "message": "your message here",
    "source": "debug-client",
    "user_id": "user-xxx"
}
```

## Example Interactions

```
You: fly 50 meters north

✅ Mission created successfully
   Status: processed
   📋 Mission DSL Generated:
      - Mission ID: mission-abc123
      - Segments: 3
        1. takeoff: None
        2. move: fly
        3. land: None
```

## Troubleshooting

- **Connection refused**: Make sure FastAPI server is running on `ws://localhost:8000/ws`
- **websockets not found**: Run `pip install -r requirements.txt`
- **Cannot send messages**: Check server logs for NLP processing errors


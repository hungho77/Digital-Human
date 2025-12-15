# API Reference

Complete API documentation for the Digital Human Restaurant Assistant system.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [REST API Endpoints](#rest-api-endpoints)
4. [WebSocket API](#websocket-api)
5. [Agent API](#agent-api)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

## Overview

### Base URL

```
Development: http://localhost:8010
Production:  https://your-domain.com
```

### API Versioning

Current version: `v1`

All API endpoints are prefixed with `/api/v1/`

### Content Types

```
Request:  application/json
Response: application/json
WebSocket: application/json (over WS)
```

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-12-16T10:30:00Z"
}
```

Error response:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid party size",
    "details": { ... }
  },
  "timestamp": "2025-12-16T10:30:00Z"
}
```

## Authentication

### API Key Authentication

```http
Authorization: Bearer YOUR_API_KEY
```

Example:

```bash
curl -H "Authorization: Bearer sk_test_abc123..." \
  https://api.example.com/api/v1/sessions
```

### Session Authentication

For WebSocket connections, session authentication is required:

```javascript
const ws = new WebSocket('wss://api.example.com/ws?session_id=sess_123&token=abc...');
```

## REST API Endpoints

### Health & Status

#### GET /health

Check system health status.

**Response:**

```json
{
  "status": "healthy",
  "services": {
    "database": "up",
    "redis": "up",
    "vllm": "up",
    "whisper": "up",
    "qdrant": "up"
  },
  "version": "1.0.0",
  "uptime_seconds": 86400
}
```

#### GET /metrics

Prometheus metrics endpoint.

**Response:** Prometheus text format

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health"} 1234
```

### Session Management

#### POST /api/v1/sessions

Create a new conversation session.

**Request:**

```json
{
  "customer_name": "Nguyen Van A",
  "phone": "0901234567",
  "metadata": {
    "source": "web",
    "referrer": "google"
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123def456",
    "websocket_url": "wss://api.example.com/ws?session_id=sess_abc123def456",
    "expires_at": "2025-12-16T11:30:00Z"
  }
}
```

#### GET /api/v1/sessions/{session_id}

Get session details.

**Response:**

```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123def456",
    "status": "active",
    "customer_name": "Nguyen Van A",
    "created_at": "2025-12-16T10:30:00Z",
    "messages_count": 12,
    "reservations": [
      {
        "id": "res_123",
        "date": "2025-12-20T19:00:00Z",
        "party_size": 4,
        "status": "confirmed"
      }
    ]
  }
}
```

#### DELETE /api/v1/sessions/{session_id}

End a session.

**Response:**

```json
{
  "success": true,
  "message": "Session ended successfully"
}
```

### Conversation

#### POST /api/v1/conversations/message

Send a text message to the agent.

**Request:**

```json
{
  "session_id": "sess_abc123def456",
  "message": "Tôi muốn đặt bàn cho 4 người",
  "metadata": {
    "timestamp": "2025-12-16T10:30:00Z"
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "message_id": "msg_789xyz",
    "agent_response": "Dạ vâng, quý khách muốn đặt bàn cho 4 người. Quý khách muốn đặt vào ngày nào ạ?",
    "intent": "reservation_inquiry",
    "confidence": 0.95,
    "context": {
      "party_size": 4,
      "state": "collecting_date"
    }
  }
}
```

#### POST /api/v1/conversations/audio

Send audio for transcription and processing.

**Request:** `multipart/form-data`

```
audio: (binary audio file)
session_id: sess_abc123def456
format: wav
sample_rate: 16000
```

**Response:**

```json
{
  "success": true,
  "data": {
    "transcript": "Tôi muốn đặt bàn cho 4 người",
    "confidence": 0.92,
    "agent_response": "Dạ vâng, quý khách muốn đặt bàn cho 4 người...",
    "audio_url": "https://api.example.com/audio/response_123.mp3"
  }
}
```

### Reservations

#### POST /api/v1/reservations

Create a new reservation.

**Request:**

```json
{
  "session_id": "sess_abc123def456",
  "date": "2025-12-20T19:00:00Z",
  "party_size": 4,
  "customer_name": "Nguyen Van A",
  "phone": "0901234567",
  "preferences": {
    "seating": "window",
    "dietary": ["vegetarian"],
    "occasion": "birthday"
  },
  "notes": "Birthday celebration"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "reservation_id": "res_abc123",
    "confirmation_code": "ABC123",
    "status": "confirmed",
    "date": "2025-12-20T19:00:00Z",
    "party_size": 4,
    "table_number": 12,
    "estimated_duration_minutes": 120,
    "customer": {
      "name": "Nguyen Van A",
      "phone": "0901234567"
    },
    "preferences": {
      "seating": "window",
      "dietary": ["vegetarian"],
      "occasion": "birthday"
    }
  }
}
```

#### GET /api/v1/reservations/{reservation_id}

Get reservation details.

**Response:**

```json
{
  "success": true,
  "data": {
    "reservation_id": "res_abc123",
    "confirmation_code": "ABC123",
    "status": "confirmed",
    "date": "2025-12-20T19:00:00Z",
    "party_size": 4,
    "table_number": 12,
    "customer": {
      "name": "Nguyen Van A",
      "phone": "0901234567"
    },
    "created_at": "2025-12-16T10:30:00Z",
    "modified_at": "2025-12-16T10:30:00Z"
  }
}
```

#### PUT /api/v1/reservations/{reservation_id}

Update a reservation.

**Request:**

```json
{
  "date": "2025-12-20T20:00:00Z",
  "party_size": 5,
  "notes": "Added one more person"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "reservation_id": "res_abc123",
    "status": "confirmed",
    "date": "2025-12-20T20:00:00Z",
    "party_size": 5,
    "table_number": 15,
    "message": "Reservation updated successfully"
  }
}
```

#### DELETE /api/v1/reservations/{reservation_id}

Cancel a reservation.

**Response:**

```json
{
  "success": true,
  "message": "Reservation cancelled successfully"
}
```

### Table Availability

#### GET /api/v1/availability

Check table availability.

**Query Parameters:**

- `date`: ISO 8601 datetime (required)
- `party_size`: Number of guests (required)
- `duration_minutes`: Estimated duration (optional, default: 120)

**Example:**

```
GET /api/v1/availability?date=2025-12-20T19:00:00Z&party_size=4
```

**Response:**

```json
{
  "success": true,
  "data": {
    "available": true,
    "tables": [
      {
        "table_id": 12,
        "table_number": "T12",
        "capacity": 4,
        "location": "window"
      },
      {
        "table_id": 15,
        "table_number": "T15",
        "capacity": 6,
        "location": "main_hall"
      }
    ],
    "alternatives": [
      {
        "date": "2025-12-20T18:00:00Z",
        "available_tables": 3
      },
      {
        "date": "2025-12-20T20:00:00Z",
        "available_tables": 5
      }
    ]
  }
}
```

### Knowledge Base

#### POST /api/v1/knowledge/query

Query the restaurant knowledge base (RAG).

**Request:**

```json
{
  "question": "Món ăn đặc sản của nhà hàng là gì?",
  "top_k": 3,
  "filters": {
    "category": "menu"
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "answer": "Món ăn đặc sản của nhà hàng bao gồm Phở bò đặc biệt, Bún chả Hà Nội, và Cơm tấm sườn nướng.",
    "sources": [
      {
        "content": "Phở bò đặc biệt là món ăn signature...",
        "score": 0.95,
        "metadata": {
          "category": "menu",
          "item": "pho_bo"
        }
      }
    ],
    "confidence": 0.92
  }
}
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://api.example.com/ws?session_id=sess_abc123');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

### Message Types

#### Client → Server

**Audio Stream:**

```json
{
  "type": "audio_chunk",
  "data": {
    "audio": "base64_encoded_audio_data",
    "format": "pcm",
    "sample_rate": 16000,
    "sequence": 123
  }
}
```

**Text Message:**

```json
{
  "type": "text_message",
  "data": {
    "text": "Tôi muốn đặt bàn",
    "timestamp": "2025-12-16T10:30:00Z"
  }
}
```

**Ping:**

```json
{
  "type": "ping"
}
```

#### Server → Client

**Transcription:**

```json
{
  "type": "transcription",
  "data": {
    "text": "Tôi muốn đặt bàn",
    "confidence": 0.92,
    "is_final": true
  }
}
```

**Agent Response:**

```json
{
  "type": "agent_response",
  "data": {
    "text": "Dạ vâng, quý khách muốn đặt bàn. Quý khách muốn đặt vào ngày nào ạ?",
    "intent": "reservation_inquiry",
    "context": {
      "state": "collecting_date"
    }
  }
}
```

**Avatar Animation:**

```json
{
  "type": "avatar_animation",
  "data": {
    "audio_url": "https://cdn.example.com/audio/response_123.mp3",
    "visemes": [
      {"time": 0.0, "viseme": "aa"},
      {"time": 0.1, "viseme": "ee"}
    ],
    "emotion": "friendly",
    "gesture": "greeting"
  }
}
```

**Status Update:**

```json
{
  "type": "status",
  "data": {
    "status": "processing",
    "message": "Đang xử lý yêu cầu của quý khách..."
  }
}
```

**Error:**

```json
{
  "type": "error",
  "data": {
    "code": "TRANSCRIPTION_FAILED",
    "message": "Unable to transcribe audio",
    "retry": true
  }
}
```

**Pong:**

```json
{
  "type": "pong"
}
```

## Agent API

### LangGraph State

#### Dialogue State

```python
class DialogueState(TypedDict):
    """State structure for dialogue agent."""
    session_id: str
    messages: List[Message]
    customer_name: Optional[str]
    intent: Optional[str]
    context: Dict[str, Any]
    conversation_history: List[Dict]
```

#### Reservation State

```python
class ReservationState(TypedDict):
    """State structure for reservation agent."""
    date: Optional[datetime]
    party_size: Optional[int]
    customer_name: Optional[str]
    phone: Optional[str]
    preferences: Dict[str, Any]
    available_tables: List[int]
    selected_table: Optional[int]
    status: str
```

### Agent Endpoints

#### POST /api/v1/agents/dialogue

Invoke dialogue agent directly.

**Request:**

```json
{
  "state": {
    "session_id": "sess_abc123",
    "messages": [
      {"role": "user", "content": "Tôi muốn đặt bàn"}
    ],
    "context": {}
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "state": {
      "session_id": "sess_abc123",
      "messages": [
        {"role": "user", "content": "Tôi muốn đặt bàn"},
        {"role": "assistant", "content": "Dạ vâng..."}
      ],
      "intent": "reservation",
      "context": {
        "state": "collecting_date"
      }
    }
  }
}
```

#### POST /api/v1/agents/reservation

Invoke reservation agent directly.

**Request:**

```json
{
  "state": {
    "date": "2025-12-20T19:00:00Z",
    "party_size": 4,
    "customer_name": "Nguyen Van A",
    "phone": "0901234567",
    "status": "searching"
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "state": {
      "date": "2025-12-20T19:00:00Z",
      "party_size": 4,
      "customer_name": "Nguyen Van A",
      "phone": "0901234567",
      "available_tables": [12, 15],
      "selected_table": 12,
      "status": "confirmed"
    },
    "reservation_id": "res_abc123"
  }
}
```

## Error Handling

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing authentication |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict (e.g., table already booked) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid party size",
    "details": {
      "field": "party_size",
      "value": 0,
      "constraint": "must be between 1 and 20"
    }
  },
  "timestamp": "2025-12-16T10:30:00Z",
  "request_id": "req_abc123"
}
```

## Rate Limiting

### Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/v1/sessions` | 10 | 1 minute |
| `/api/v1/conversations/*` | 100 | 1 minute |
| `/api/v1/reservations` | 20 | 1 minute |
| `/api/v1/knowledge/query` | 30 | 1 minute |
| WebSocket messages | 60 | 1 minute |

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702734600
```

### Rate Limit Error

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 30 seconds.",
    "retry_after": 30
  }
}
```

## Examples

### Complete Reservation Flow

```python
import requests

BASE_URL = "https://api.example.com/api/v1"
API_KEY = "your_api_key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 1. Create session
session_resp = requests.post(
    f"{BASE_URL}/sessions",
    json={
        "customer_name": "Nguyen Van A",
        "phone": "0901234567"
    },
    headers=headers
)
session_id = session_resp.json()["data"]["session_id"]

# 2. Check availability
availability_resp = requests.get(
    f"{BASE_URL}/availability",
    params={
        "date": "2025-12-20T19:00:00Z",
        "party_size": 4
    },
    headers=headers
)
tables = availability_resp.json()["data"]["tables"]

# 3. Create reservation
reservation_resp = requests.post(
    f"{BASE_URL}/reservations",
    json={
        "session_id": session_id,
        "date": "2025-12-20T19:00:00Z",
        "party_size": 4,
        "customer_name": "Nguyen Van A",
        "phone": "0901234567",
        "preferences": {
            "seating": "window"
        }
    },
    headers=headers
)
reservation = reservation_resp.json()["data"]
print(f"Reservation confirmed: {reservation['confirmation_code']}")
```

### WebSocket Conversation

```javascript
const session_id = 'sess_abc123';
const ws = new WebSocket(`wss://api.example.com/ws?session_id=${session_id}`);

ws.onopen = () => {
  // Send text message
  ws.send(JSON.stringify({
    type: 'text_message',
    data: {
      text: 'Tôi muốn đặt bàn cho 4 người vào tối mai',
      timestamp: new Date().toISOString()
    }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch(message.type) {
    case 'agent_response':
      console.log('Agent:', message.data.text);
      // Display response to user
      break;

    case 'avatar_animation':
      // Play avatar audio and animation
      playAvatarResponse(message.data);
      break;

    case 'status':
      console.log('Status:', message.data.message);
      break;

    case 'error':
      console.error('Error:', message.data.message);
      break;
  }
};

function playAvatarResponse(data) {
  // Play audio
  const audio = new Audio(data.audio_url);
  audio.play();

  // Animate avatar with visemes
  animateAvatar(data.visemes, data.emotion);
}
```

## SDK Support

### Python SDK

```python
from digital_human import Client

client = Client(api_key="your_api_key")

# Create session
session = client.sessions.create(
    customer_name="Nguyen Van A",
    phone="0901234567"
)

# Send message
response = client.conversations.send_message(
    session_id=session.id,
    message="Tôi muốn đặt bàn"
)

# Create reservation
reservation = client.reservations.create(
    session_id=session.id,
    date="2025-12-20T19:00:00Z",
    party_size=4,
    customer_name="Nguyen Van A",
    phone="0901234567"
)
```

### JavaScript/TypeScript SDK

```typescript
import { DigitalHumanClient } from '@digital-human/client';

const client = new DigitalHumanClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.example.com'
});

// Create session
const session = await client.sessions.create({
  customerName: 'Nguyen Van A',
  phone: '0901234567'
});

// Send message
const response = await client.conversations.sendMessage({
  sessionId: session.id,
  message: 'Tôi muốn đặt bàn'
});

// Create reservation
const reservation = await client.reservations.create({
  sessionId: session.id,
  date: '2025-12-20T19:00:00Z',
  partySize: 4,
  customerName: 'Nguyen Van A',
  phone: '0901234567'
});
```

## Next Steps

- 📖 Review [Architecture](./architecture.md)
- 💻 Check [Development Guide](./development.md)
- 🚀 Follow [Deployment Guide](./deployment.md)
- ⚙️ Setup [Environment](./environment-setup.md)

## Support

For API support:
- Email: api-support@example.com
- Discord: https://discord.gg/digital-human
- GitHub Issues: https://github.com/YOUR_USERNAME/Digital-Human/issues


# AI-Powered Database Chat System

A comprehensive system that allows users to interact with databases through a natural language chat interface powered by LLM agents with multi-layer guardrails.

## Architecture

```
Frontend (Next.js)
       ↓
Backend (FastAPI + Python)
       ↓
LangChain Agent
       ↓
Supabase Database
```

## Tech Stack

- **Frontend**: Next.js 14 + React + TypeScript
- **Backend**: Python + FastAPI
- **Agent**: LangChain
- **LLM**: OpenAI GPT-3.5-turbo
- **Database**: Supabase (PostgreSQL)
- **Security**: 6-layer guardrail architecture

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── database.py             # Supabase client
│   ├── agent/
│   │   ├── tools.py           # Database query tools
│   │   └── agent.py           # LangChain agent setup
│   ├── guardrails/
│   │   ├── input_layer.py     # Input validation
│   │   ├── policy_layer.py    # Policy enforcement
│   │   ├── instruction_layer.py # Prompt injection prevention
│   │   ├── execution_layer.py # Tool execution safety
│   │   ├── output_layer.py    # Output filtering
│   │   └── monitoring_layer.py # Audit logging
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main page
│   │   └── layout.tsx         # Root layout
│   ├── components/
│   │   ├── ChatInterface.tsx  # Chat UI
│   │   ├── MessageList.tsx    # Message display
│   │   └── InputBox.tsx       # User input
│   ├── lib/
│   │   ├── api.ts             # API client
│   │   └── types.ts           # TypeScript types
│   ├── styles/
│   │   └── globals.css        # Global styles
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   └── tsconfig.node.json
├── scripts/
│   └── seed_database.py       # Database seeding script
└── .env.example               # Environment template

```

## Database Schema

### Students Table
- `id` (UUID): Primary key
- `name` (TEXT): Student name
- `email` (TEXT): Unique email
- `enrollment_date` (TIMESTAMP): Enrollment date
- `major` (TEXT): Major/field of study
- `gpa` (NUMERIC): Grade point average

### Courses Table
- `id` (UUID): Primary key
- `name` (TEXT): Course name
- `code` (TEXT): Unique course code
- `instructor` (TEXT): Instructor name
- `credits` (INTEGER): Number of credits
- `capacity` (INTEGER): Course capacity

### Transactions Table
- `id` (UUID): Primary key
- `student_id` (UUID): Foreign key to students
- `course_id` (UUID): Foreign key to courses
- `transaction_type` (TEXT): enrollment, payment, grade_submission, course_drop
- `amount` (NUMERIC): Amount (nullable)
- `status` (TEXT): pending, completed, failed
- `timestamp` (TIMESTAMP): Transaction timestamp
- `description` (TEXT): Transaction description

## Database Tools (7 Total)

1. **query_students**: Query students by name, major, or GPA range
2. **query_courses**: Query courses by name, instructor, or credits
3. **query_transactions**: Query transactions by student, course, type, or status
4. **get_student_courses**: Get all courses for a specific student
5. **get_course_students**: Get all students in a specific course
6. **get_student_transaction_summary**: Get transaction statistics for a student
7. **get_course_statistics**: Get enrollment stats for a course

## Guardrails Architecture (6 Layers)

### 1. Input Layer
- Maximum input length validation (2000 chars)
- SQL injection pattern detection and blocking
- Rate limiting (10 requests/min per session)
- Input sanitization

### 2. Policy Layer
- Tool allowlist enforcement (only 7 tools allowed)
- Query result limits (10,000 max results)
- Execution time limits (30 seconds max)
- Resource constraint validation

### 3. Instruction Layer
- Prompt injection attack detection
- System prompt integrity validation
- Suspicious pattern detection
- Instruction override prevention

### 4. Execution Layer
- Tool parameter type validation
- Execution timeout enforcement
- Read-only mode enforcement
- Resource usage monitoring

### 5. Output Layer
- Sensitive field redaction
- Result truncation (500 items max)
- JSON structure validation
- Data leakage prevention

### 6. Monitoring Layer
- Comprehensive audit logging
- Request/response tracking
- Guardrail action logging
- Alert generation
- Session tracking

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account
- OpenAI API key

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env with your credentials:
# SUPABASE_URL=your_url
# SUPABASE_KEY=your_key
# OPENAI_API_KEY=your_key
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 3. Database Seeding

```bash
cd scripts
python seed_database.py
```

This creates:
- 100 students
- 50 courses
- 850 transactions
- **Total: 1000+ data points**

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

### POST /chat
Send a message to the database agent.

**Request:**
```json
{
  "message": "Show me students with GPA > 3.5",
  "session_id": "optional_session_uuid"
}
```

**Response:**
```json
{
  "response": "Found 15 students with GPA above 3.5...",
  "tools_used": ["query_students"],
  "execution_time_ms": 245.5,
  "filtered": false,
  "metadata": {"session_id": "..."}
}
```

### GET /health
Health check endpoint.

### GET /logs/summary
Get audit log summary.

## Example Queries

- "How many students are enrolled in CS101?"
- "Show all courses taught by Dr. Smith"
- "Get transaction summary for student [ID]"
- "Which students have GPA above 3.5?"
- "What's the enrollment rate for course [CODE]?"
- "Show me all failed transactions"

## Monitoring & Logging

All system events are logged in JSON format to `logs/audit.log`:

```json
{
  "timestamp": "2026-05-14T10:30:00Z",
  "layer": "input_layer",
  "event_type": "request",
  "action": "received",
  "user_input_hash": "sha256_hash",
  "session_id": "session_uuid",
  "input_length": 45
}
```

Available log summaries via `/logs/summary` endpoint.

## Security Features

✓ **SQL Injection Prevention**: Parameterized queries only
✓ **Prompt Injection Prevention**: Input sanitization + pattern detection
✓ **Data Leakage Prevention**: Sensitive field redaction
✓ **Unauthorized Access Prevention**: Tool allowlist + read-only enforcement
✓ **Rate Limiting**: 10 requests per minute per session
✓ **Audit Trail**: Complete request/response logging
✓ **Resource Limits**: 30-second query timeout, 10K result limit
✓ **JSON Validation**: Depth checking, structure validation

## Performance

- Average query response time: 200-500ms
- Concurrent request handling: Multiple sessions supported
- Database connection pooling: Automatic via Supabase
- Session isolation: Per-session rate limiting

## Deployment

### Docker Deployment (Optional)

```bash
# Build images
docker build -t db-agent-backend ./backend
docker build -t db-agent-frontend ./frontend

# Run containers
docker run -p 8000:8000 db-agent-backend
docker run -p 3000:3000 db-agent-frontend
```

### Production Checklist

- [ ] Set secure OpenAI API key
- [ ] Configure Supabase security rules
- [ ] Enable HTTPS for production
- [ ] Set up log aggregation
- [ ] Configure monitoring alerts
- [ ] Enable database backups
- [ ] Review guardrail settings for your use case

## Troubleshooting

### Backend won't start
- Check SUPABASE_URL and SUPABASE_KEY in .env
- Verify OpenAI API key is valid
- Ensure port 8000 is available

### Database connection fails
- Verify Supabase credentials
- Check network connectivity
- Review Supabase security rules

### Frontend can't reach backend
- Check NEXT_PUBLIC_API_URL environment variable
- Verify backend is running on port 8000
- Check CORS configuration in FastAPI

## Support

For issues or questions, refer to:
- Backend logs: `logs/audit.log`
- API documentation: http://localhost:8000/docs
- Frontend console: Browser DevTools

## License

MIT License

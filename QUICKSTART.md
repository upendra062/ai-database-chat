# Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Copy your `Project URL` and `API Key` (anon/public)

### Step 2: Configure Environment
```bash
cp .env.example .env

# Edit .env with your credentials
# Get values from Supabase dashboard
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
OPENAI_API_KEY=sk-your-openai-key-here
FASTAPI_PORT=8000
LOG_LEVEL=INFO
```

### Step 3: Seed Database
```bash
cd scripts
pip install -r ../backend/requirements.txt
python seed_database.py
```

Expected output:
```
Creating tables...
✓ Tables created
Seeding 100 students...
✓ 100 students seeded
Seeding 50 courses...
✓ 50 courses seeded
Seeding 850 transactions...
✓ 850 transactions seeded
✓ Database seeding complete! Total records: 1000
```

### Step 4: Start Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Expected output:
```
✓ Supabase client initialized successfully
✓ Application initialized
INFO: Application startup complete [...]
```

Access API docs: http://localhost:8000/docs

### Step 5: Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Expected output:
```
> next dev
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

### Step 6: Test the System

Open http://localhost:3000 and try these queries:

1. **"Show me all students"**
   - Lists all 100 students

2. **"How many students have GPA above 3.5?"**
   - Filters students by GPA

3. **"Show me all courses"**
   - Lists all 50 courses

4. **"What courses are taught by Dr. Smith?"**
   - Filters courses by instructor

5. **"Show me all transactions"**
   - Lists all 850 transactions

## 🔍 Testing Guardrails

### Test Input Layer
```
" '; DROP TABLE students; --"
```
Expected: ✓ Blocked (SQL injection detected)

### Test Policy Layer
Try to call an invalid tool (handled internally by agent)

### Test Output Layer
Query that returns 100+ results should be formatted properly

## 📊 Monitoring

View audit logs:
```bash
curl http://localhost:8000/logs/summary
```

View raw logs:
```bash
tail -f logs/audit.log
```

## 🚀 Next Steps

1. **Customize Queries**: Edit `backend/agent/prompts.py` for system instructions
2. **Modify Guardrails**: Adjust thresholds in `backend/config.py`
3. **Add Tools**: Create new tools in `backend/agent/tools.py`
4. **Deploy**: Follow deployment section in README.md

## ⚠️ Troubleshooting

### Port Already in Use
```bash
# Backend (8000)
lsof -i :8000
kill -9 <PID>

# Frontend (3000)
lsof -i :3000
kill -9 <PID>
```

### Database Connection Error
```bash
# Verify Supabase credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test Supabase connection
curl -H "apikey: $SUPABASE_KEY" "$SUPABASE_URL/rest/v1/students?select=*"
```

### API Not Found (404)
- Check that backend is running on http://localhost:8000
- Verify NEXT_PUBLIC_API_URL in frontend/.env.local (if needed)

### CORS Error
- Backend already configured for localhost:3000
- For production, update CORS origins in `backend/config.py`

## 📚 Documentation

- **Architecture**: See Architecture Overview in README.md
- **API**: http://localhost:8000/docs (interactive Swagger UI)
- **Guardrails**: See 6-layer architecture in README.md
- **Database Schema**: See Database Schema section in README.md

## 💡 Tips

1. **Session Tracking**: Each chat session gets a unique ID
2. **Audit Trail**: Every action is logged to `logs/audit.log`
3. **Rate Limiting**: 10 requests per minute per session
4. **Agent Timeout**: Queries auto-timeout after 30 seconds
5. **Result Limit**: Max 10,000 results per query

## 🆘 Support

Check the following if something breaks:

1. **Backend issues**: Check `logs/audit.log` for detailed errors
2. **Database issues**: Verify Supabase credentials and network
3. **Frontend issues**: Check browser console (F12) for client errors
4. **API issues**: Visit http://localhost:8000/docs for API schema

## 🎯 Performance Baseline

- First query: 1-3 seconds (includes model warmup)
- Subsequent queries: 200-500ms average
- Concurrent users: Can handle multiple sessions
- Database: Handles 1000+ records efficiently

Happy chatting! 🎉

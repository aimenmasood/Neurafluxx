# NeuraFlux Chatbot - Setup & Website Integration Guide

Complete guide for Usman to set up the chatbot backend and integrate it into the website.

---

## 📦 What You Have

- **Package Size:** 1.61 MB (compressed)
- **Contains:** Full chatbot source code, vector database, documentation
- **Status:** Ready to deploy

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Extract & Install
```bash
# Extract the ZIP file
unzip neuraflux-chatbot-ready-to-integrate.zip
cd neuraflux-chatbot

# Install dependencies (first time only)
pip install -r requirements.txt
```

### Step 2: Configure API Keys
Edit `.env` file in root directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

Get API keys from:
- **Google:** https://ai.google.dev/
- **Groq:** https://console.groq.com/

### Step 3: Start Backend Server
```bash
python api/main.py
```

✅ **Server running at:** `http://localhost:8000`

**Test API:** Open browser → `http://localhost:8000/docs`

---

## 🌐 Add Chatbot to Your Website

### Option 1: Simple Embed (Recommended for Quick Integration)

Copy-paste this in your website's HTML `<body>`:

```html
<div id="neuraflux-chatbot"></div>

<script>
  (function() {
    const container = document.getElementById('neuraflux-chatbot');
    container.innerHTML = `
      <div style="width:400px; height:600px; background:white; border-radius:12px; box-shadow:0 10px 40px rgba(0,0,0,0.3); display:flex; flex-direction:column;">
        <div style="background:#667eea; color:white; padding:20px; border-radius:12px 12px 0 0; text-align:center;">
          <h2>NeuraFlux Chatbot</h2>
        </div>
        <div id="messages" style="flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; gap:10px;"></div>
        <div style="display:flex; gap:10px; padding:15px; border-top:1px solid #ddd;">
          <input id="input" type="text" placeholder="Ask me anything..." style="flex:1; padding:12px; border:1px solid #ddd; border-radius:6px; font-size:14px;"/>
          <button id="send" style="padding:12px 24px; background:#667eea; color:white; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">Send</button>
        </div>
      </div>
    `;

    const messagesDiv = document.getElementById('messages');
    const inputField = document.getElementById('input');
    const sendBtn = document.getElementById('send');

    function addMessage(text, sender) {
      const msg = document.createElement('div');
      msg.style.cssText = sender === 'user' 
        ? 'align-self:flex-end; background:#667eea; color:white; padding:10px 14px; border-radius:8px 0 8px 8px; max-width:80%; word-wrap:break-word;'
        : 'align-self:flex-start; background:#f0f0f0; color:#333; padding:10px 14px; border-radius:0 8px 8px 8px; max-width:80%; word-wrap:break-word;';
      msg.textContent = text;
      messagesDiv.appendChild(msg);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    async function send() {
      const query = inputField.value.trim();
      if (!query) return;
      
      inputField.value = '';
      sendBtn.disabled = true;
      addMessage(query, 'user');

      const loadingMsg = document.createElement('div');
      loadingMsg.style.cssText = 'align-self:flex-start; color:#999; font-style:italic;';
      loadingMsg.textContent = 'Thinking...';
      messagesDiv.appendChild(loadingMsg);
      
      try {
        const res = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query })
        });

        if (!res.ok) throw new Error('Network error');
        const data = await res.json();
        loadingMsg.remove();
        addMessage(data.response, 'bot');
      } catch(e) {
        console.error('Error:', e);
        loadingMsg.remove();
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
      } finally {
        sendBtn.disabled = false;
        inputField.focus();
      }
    }

    sendBtn.onclick = send;
    inputField.onkeypress = (e) => e.key === 'Enter' && send();
  })();
</script>
```

### Option 2: React Component

```jsx
import { useState, useRef, useEffect } from 'react';

export default function ChatBot() {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm the NeuraFlux Assistant. How can I help?", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEnd = useRef(null);

  useEffect(() => messagesEnd.current?.scrollIntoView({ behavior: 'smooth' }), [messages]);

  const send = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages(prev => [...prev, { text: input, sender: 'user' }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
      });
      
      const data = await res.json();
      setMessages(prev => [...prev, { text: data.response, sender: 'bot' }]);
    } catch (e) {
      setMessages(prev => [...prev, { text: 'Error occurred. Try again.', sender: 'bot' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.sender}`}>{m.text}</div>
        ))}
        <div ref={messagesEnd} />
      </div>
      <form onSubmit={send}>
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask..." disabled={loading} />
        <button type="submit" disabled={loading}>Send</button>
      </form>
    </div>
  );
}
```

---

## 📡 API Endpoint Details

### POST /chat

**URL:** `http://localhost:8000/chat` (development)

**Request:**
```json
{
  "query": "What is NeuraFlux?"
}
```

**Response:**
```json
{
  "response": "NeuraFlux is an AI solutions company that provides innovative AI solutions..."
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (invalid query)
- `500` - Server error

---

## 📂 Project Structure

```
neuraflux-chatbot/
├── api/
│   ├── main.py              # FastAPI server (run this to start)
│   └── engine.py            # Chatbot logic
├── rag/
│   ├── retriever.py         # Context retrieval from vector DB
│   └── prompt.py            # System prompts
├── ingest/
│   ├── ingest.py            # Data processing
│   └── kb_docs/             # Knowledge base documents
├── chroma_db/               # Vector database (pre-loaded)
├── requirements.txt         # Python dependencies
├── .env                     # Your API keys (edit this)
└── api/main.py             # START HERE
```

---

## 🚀 Production Deployment

### Option 1: Gunicorn (Simple & Reliable)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api.main:app
```

### Option 2: PM2 (Keep Running 24/7)
```bash
npm install -g pm2
pm2 start "python api/main.py" --name neuraflux
pm2 startup
pm2 save
```

### Option 3: Docker (Most Reliable)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "api/main.py"]
```

Build and run:
```bash
docker build -t neuraflux-chatbot .
docker run -p 8000:8000 --env-file .env neuraflux-chatbot
```

---

## ⚙️ Configuration

### Change Port
Edit `api/main.py`:
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)  # Change 8000 to 9000
```

### Allow Specific Domains (Production)
Edit `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourwebsite.com"],  # Change from ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## 🔒 Security

**For Development:** Current settings allow all origins (`"*"`)

**For Production:**
1. Update CORS to allow only your domain
2. Use HTTPS
3. Add rate limiting:
   ```bash
   pip install slowapi
   ```
   Then add to `api/main.py`:
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=lambda: "")
   @app.post("/chat")
   @limiter.limit("100/minute")
   def chat(request):
       ...
   ```

4. Keep `.env` private (never commit to git)

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| **CORS error in browser** | Update CORS in `api/main.py` → `allow_origins=["*"]` for dev |
| **Connection refused** | Ensure server is running: `python api/main.py` |
| **API returns 500 error** | Check `.env` has valid API keys (GOOGLE_API_KEY, GROQ_API_KEY) |
| **"Thinking..." never stops** | Server might be slow. Check terminal logs where server runs |
| **Port 8000 in use** | Change port in `api/main.py` or kill existing process |
| **Dependencies won't install** | Ensure Python 3.8+: `python --version` |

---

## 📋 Dependencies

```
fastapi              # Web framework
uvicorn              # ASGI server
python-docx          # Document processing
chromadb             # Vector database
sentence-transformers # Embeddings
groq                 # Groq API
google-generativeai  # Google Gemini API
python-dotenv        # Environment variables
```

---

## ✅ Checklist for Setup

- [ ] Extract ZIP file
- [ ] Run: `pip install -r requirements.txt`
- [ ] Create `.env` with GOOGLE_API_KEY and GROQ_API_KEY
- [ ] Run: `python api/main.py`
- [ ] Visit: `http://localhost:8000/docs` to test
- [ ] Copy-paste embed code into your website HTML
- [ ] Test chatbot in your website
- [ ] Deploy to production (use Gunicorn/Docker)

---

## 🆘 Quick Debugging

**Check if server is running:**
```bash
curl http://localhost:8000/docs
```

**Check logs:**
Look at terminal where you ran `python api/main.py`

**Test API directly:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"Hello"}'
```

---

## 📞 Support

For issues:
1. Check `.env` has correct API keys
2. Verify Python 3.8+
3. Check terminal logs for errors
4. Ensure port 8000 is available

**Default API URL:** `http://localhost:8000`
**Swagger Docs:** `http://localhost:8000/docs`

---

**Ready to integrate! 🚀**

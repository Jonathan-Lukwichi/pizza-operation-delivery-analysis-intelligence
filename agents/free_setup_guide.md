# Free AI Agent Setup Guide
## Zero Cost Implementation

This guide shows you how to run the AI Agent system **completely free**.

---

## Quick Start (5 Minutes)

### Option A: Ollama (Recommended - Best Quality)

**Step 1: Install Ollama**
```bash
# Windows: Download from https://ollama.ai/download
# Or use winget:
winget install Ollama.Ollama
```

**Step 2: Download a Model**
```bash
# Open terminal and run:
ollama pull llama3.1:8b

# Wait for download (~4.7GB)
```

**Step 3: Verify it's running**
```bash
# Ollama starts automatically. Test it:
ollama run llama3.1:8b "Hello, how are you?"
```

**Step 4: Use in Python**
```python
from agents.free_llm_providers import OllamaProvider

llm = OllamaProvider(model="llama3.1:8b")
response = await llm.generate("Analyze my delivery data")
print(response.content)  # Free!
```

---

### Option B: Groq (Fastest Cloud Option)

**Step 1: Get Free API Key**
1. Go to https://console.groq.com/
2. Click "Sign Up" (use Google/GitHub)
3. Go to "API Keys" → "Create API Key"
4. Copy the key

**Step 2: Set Environment Variable**
```bash
# Windows (Command Prompt)
set GROQ_API_KEY=your_key_here

# Windows (PowerShell)
$env:GROQ_API_KEY="your_key_here"

# Or add to .env file
echo GROQ_API_KEY=your_key_here >> .env
```

**Step 3: Use in Python**
```python
from agents.free_llm_providers import GroqProvider

llm = GroqProvider()  # Auto-reads from environment
response = await llm.generate("What are today's bottlenecks?")
print(response.content)  # Free! (14,400 requests/day)
```

---

### Option C: Google Gemini

**Step 1: Get Free API Key**
1. Go to https://aistudio.google.com/
2. Click "Get API Key"
3. Create new key (free)

**Step 2: Set Environment Variable**
```bash
set GOOGLE_API_KEY=your_key_here
```

**Step 3: Use in Python**
```python
from agents.free_llm_providers import GeminiProvider

llm = GeminiProvider()
response = await llm.generate("Predict tomorrow's demand")
print(response.content)  # Free! (1,500 requests/day)
```

---

## Complete Free Stack

### 1. Install Dependencies

```bash
# Core dependencies (most already installed)
pip install aiohttp requests

# For Groq (optional)
pip install groq

# For Gemini (optional)
pip install google-generativeai

# For Ollama - no pip install needed, just the app
```

### 2. Create .env File

```env
# .env file - add whichever you have

# Option 1: Groq (get free key at console.groq.com)
GROQ_API_KEY=gsk_xxxxxxxxxxxx

# Option 2: Google (get free key at aistudio.google.com)
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxx

# Option 3: Hugging Face (optional, for more models)
HF_TOKEN=hf_xxxxxxxxxxxx

# Ollama doesn't need a key - just install the app
```

### 3. Test Your Setup

```python
# test_free_llm.py

import asyncio
from agents.free_llm_providers import SmartFreeProvider

async def test():
    # Auto-detects best available free provider
    llm = SmartFreeProvider()

    response = await llm.generate(
        prompt="What are 3 ways to reduce pizza delivery time?",
        system_prompt="You are a business operations expert."
    )

    print(f"Provider: {llm.provider.__class__.__name__}")
    print(f"Response: {response.content}")
    print(f"Cost: ${response.cost}")  # Always $0!

asyncio.run(test())
```

---

## Free Tier Limits Comparison

| Provider | Requests/Day | Requests/Min | Speed | Quality |
|----------|-------------|--------------|-------|---------|
| **Ollama** | Unlimited | Unlimited | Fast | ⭐⭐⭐⭐⭐ |
| **Groq** | 14,400 | 30 | Very Fast | ⭐⭐⭐⭐ |
| **Gemini** | 1,500 | 60 | Fast | ⭐⭐⭐⭐ |
| **HuggingFace** | ~1,000 | 10 | Medium | ⭐⭐⭐ |

**Recommendation:**
- Use **Ollama** if you have a decent computer (8GB+ RAM)
- Use **Groq** if you want cloud-based with good limits
- Use both together for redundancy

---

## Hardware Requirements for Ollama

| Model | RAM Needed | Quality | Speed |
|-------|-----------|---------|-------|
| `phi3:mini` | 4GB | ⭐⭐⭐ | Very Fast |
| `llama3.1:8b` | 8GB | ⭐⭐⭐⭐ | Fast |
| `mistral:7b` | 8GB | ⭐⭐⭐⭐ | Fast |
| `llama3.1:70b` | 48GB | ⭐⭐⭐⭐⭐ | Slow |

**Your PC probably works!** Most modern computers can run the 8B models.

---

## Integration with Agent System

### Update Orchestrator to Use Free LLM

```python
# In agents/orchestrator.py, add:

from .free_llm_providers import SmartFreeProvider

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="orchestrator",
            description="central coordination",
            llm_client=SmartFreeProvider(),  # FREE!
        )
```

### Full Working Example

```python
# run_free_agents.py

import asyncio
from agents.free_llm_providers import SmartFreeProvider
from agents.orchestrator import OrchestratorAgent
from agents.data_agent import DataIngestionAgent
from agents.process_agent import ProcessMiningAgent

async def main():
    # Initialize with FREE LLM
    llm = SmartFreeProvider()

    # Create orchestrator with free LLM
    orchestrator = OrchestratorAgent(llm_client=llm)

    # Register agents
    orchestrator.register_agent(DataIngestionAgent(llm_client=llm))
    orchestrator.register_agent(ProcessMiningAgent(llm_client=llm))

    # Ask a question - costs $0!
    response = await orchestrator.process(
        "What are the main bottlenecks in our delivery process?"
    )

    print(response.content)
    print(f"\nTotal cost: $0 (using {llm.provider.__class__.__name__})")

asyncio.run(main())
```

---

## Free Communication Channels

### Email (Gmail SMTP - Free)

```python
import smtplib
from email.mime.text import MIMEText

def send_free_email(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "your_email@gmail.com"
    msg['To'] = to

    # Use Gmail SMTP (free, 500 emails/day)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login("your_email@gmail.com", "app_password")
        server.send_message(msg)
```

### Telegram Bot (Free, Unlimited)

```python
import requests

TELEGRAM_TOKEN = "your_bot_token"  # Get from @BotFather

def send_telegram(chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})
```

### Discord Bot (Free, Unlimited)

```python
import requests

DISCORD_WEBHOOK = "your_webhook_url"

def send_discord(message: str):
    requests.post(DISCORD_WEBHOOK, json={"content": message})
```

---

## Free Hosting Options

### 1. Streamlit Cloud (Recommended)

```bash
# 1. Push code to GitHub
# 2. Go to share.streamlit.io
# 3. Connect your repo
# 4. Deploy for free!
```

### 2. Hugging Face Spaces

```bash
# 1. Create account at huggingface.co
# 2. Create new Space (Streamlit template)
# 3. Push your code
# 4. Free hosting with GPU option!
```

### 3. Run Locally

```bash
# Just run on your PC - free!
streamlit run app.py
```

---

## Cost Summary

| Component | Cost |
|-----------|------|
| LLM (Ollama/Groq/Gemini) | $0 |
| Vector DB (ChromaDB) | $0 |
| Agent Framework | $0 |
| Email (Gmail) | $0 |
| Notifications (Telegram) | $0 |
| Hosting (Streamlit Cloud) | $0 |
| **TOTAL** | **$0** |

---

## Troubleshooting

### Ollama Not Detected
```bash
# Make sure Ollama is running
ollama serve

# Check if it's working
curl http://localhost:11434/api/tags
```

### Groq Rate Limited
```python
# Add delay between requests
import asyncio
await asyncio.sleep(2)  # Wait 2 seconds between calls
```

### Model Too Slow
```bash
# Use a smaller model
ollama pull phi3:mini  # Very fast, 2GB
```

---

## Next Steps

1. ✅ Install Ollama OR get Groq API key
2. ✅ Run the test script
3. ✅ Integrate with your agents
4. ✅ Start asking questions for FREE!

**Questions?** The system auto-detects what's available and uses the best free option!

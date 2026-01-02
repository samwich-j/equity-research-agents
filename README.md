# Algorithmic Equity Research Agent

Multi-agent AI system for stock analysis using parallel architecture with LangGraph.

## 📌 About This Project

This is a portfolio demonstration of multi-agent system architecture using LangGraph. I built this as a publicly-shareable example of the agent orchestration patterns I've implemented professionally (where the actual systems contain proprietary information that cannot be shared).

This project showcases:
- **LangGraph parallel agent workflows** with independent analysis streams
- **Multi-agent synthesis patterns** for combining specialized perspectives
- **Flexible LLM backend** (OpenAI or local Ollama) for cost and privacy options
- **Real-world data integration** with rate-limited API calls

## 🎯 How It Works

Three specialized AI analysts work in parallel to analyze stocks:
- **Fundamentalist**: Value-focused conservative analysis
- **Quant**: Data-driven peer comparison
- **Strategist**: Synthesizes findings into BUY/SELL/HOLD recommendations

## 📁 Project Structure

```
equity-research-agents/
├── config.py           # LLM configuration (switch between OpenAI/Ollama)
├── utils.py            # LLM factory function
├── data_tools.py       # yfinance integration and peer comparison
├── agents.py           # Agent prompts and state definitions
├── main.py             # LangGraph parallel architecture
├── test_yfinance.py    # Test yfinance connectivity
├── test_imports.py     # Validate code structure
└── requirements.txt    # Dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Choose Your LLM Backend

#### Option A: OpenAI (Recommended for Limited Storage)

**Pros:**
- No local storage required
- Fast and reliable
- Cost: ~$0.10-0.50 per analysis

**Cons:**
- Requires API key and internet
- Costs money per use

**Setup:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

In `config.py`:
```python
LLM_MODEL = 'openai'
```

#### Option B: Ollama (Free, but Requires Storage)

**Pros:**
- Completely free
- Works offline
- Privacy (local execution)

**Cons:**
- Requires 2-7GB storage per model
- Slower on CPU
- Requires local Ollama installation

**Setup:**

1. Install Ollama from https://ollama.ai
2. Download model:
   ```bash
   ollama pull llama3.2
   ```
3. In `config.py`:
   ```python
   LLM_MODEL = 'ollama'
   ```

**USB Drive Option:**
If you want to run Ollama from a USB drive due to storage constraints, you can set the `OLLAMA_MODELS` environment variable:

```bash
# Mount your USB drive, then:
export OLLAMA_MODELS=/path/to/usb/ollama_models
ollama pull llama3.2
```

### 3. Run Tests

```bash
# Test yfinance connectivity
python3 test_yfinance.py

# Validate code structure
python3 test_imports.py
```

### 4. Run the System

```bash
python3 main.py
```

Enter stock tickers when prompted (e.g., `AAPL`, `MSFT`, `TSLA`)

## 📊 Example Output

```
🔬 ALGORITHMIC EQUITY RESEARCH AGENT
======================================================================

Enter stock ticker: AAPL

[Research Node] Fetching data for AAPL...
[Fundamentalist Agent] Analyzing AAPL...
[Quant Agent] Analyzing AAPL...
[Strategist Agent] Synthesizing final report...

======================================================================
📊 FINAL INVESTMENT MEMO
======================================================================

Executive Summary:
Apple Inc. presents a mixed investment opportunity. While fundamentals
show strong market position, quantitative analysis reveals significant
premium to peers...

Recommendation: **HOLD**
Conviction: Medium
======================================================================
```

## 🧪 Testing Strategy (Limited Storage)

Since you have limited storage, here's the recommended testing approach:

### Phase 1: Non-LLM Testing ✓ (Already Completed)
- ✓ Syntax validation
- ✓ Import checks
- ✓ yfinance connectivity
- ✓ Peer comparison calculations
- ✓ Graph structure

### Phase 2: Single Analysis Test

**Using OpenAI (Minimal Storage):**
1. Get OpenAI API key from https://platform.openai.com
2. Set environment variable: `export OPENAI_API_KEY='sk-...'`
3. Run: `python3 main.py`
4. Test with one ticker (e.g., `AAPL`)
5. Cost: ~$0.10-0.30 for one full analysis

**Using Ollama (If you have ~5GB free):**
1. Install Ollama
2. Download model: `ollama pull llama3.2` (~4GB)
3. Change `config.py`: `LLM_MODEL = 'ollama'`
4. Run: `python3 main.py`

### Phase 3: Production Use

Once validated, you can analyze multiple stocks.

## ⚠️ Storage Considerations

**Current Storage Usage:**
- Python packages: ~500MB
- yfinance cache: ~10-50MB (grows with usage)

**If Using Ollama:**
- llama3.2 model: ~4GB
- Total: ~5GB minimum

**If Using OpenAI:**
- No additional storage needed
- Runs entirely via API

## 🔧 Configuration Options

Edit `config.py` to customize:

```python
# LLM Selection
LLM_MODEL = 'openai'  # or 'ollama'

# OpenAI Settings
OPENAI_MODEL = 'gpt-4o-mini'  # or 'gpt-4o' for better quality
OPENAI_TEMPERATURE = 0

# Ollama Settings
OLLAMA_MODEL = 'llama3.2'  # or 'llama3.1', 'mistral', etc.
OLLAMA_TEMPERATURE = 0
```

## 🐛 Troubleshooting

**"No module named 'langchain'"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"yfinance ticker not found"**
- Check internet connection
- Verify ticker symbol is correct
- Try a well-known ticker like 'AAPL'

**"OpenAI API key not found"**
```bash
export OPENAI_API_KEY='your-key-here'
```

**"Ollama connection error"**
```bash
# Start Ollama service
ollama serve

# In another terminal
python3 main.py
```

## 📈 Future Enhancements

- Save reports to markdown files
- Add sector analysis
- Technical indicators integration
- Portfolio optimization mode
- Email/Slack notifications

## 📝 License

MIT License - Free to use and modify

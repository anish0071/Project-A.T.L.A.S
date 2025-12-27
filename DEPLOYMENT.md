# Deployment Guide

## 1-Minute Quick Start

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run
streamlit run app.py

# Open
# http://localhost:8501
```

## Local Development

### Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit; print('✅ Streamlit ready')"
```

### Run Locally

```bash
# Terminal 1: Streamlit dashboard
streamlit run app.py

# Terminal 2: FastAPI (optional)
uvicorn api:app --reload --port 8000

# Open browser
# Dashboard: http://localhost:8501
# API: http://localhost:8000/docs
```

## Docker Deployment

```bash
# Build image
docker build -t quant-backtester .

# Run container
docker run -p 8501:8501 quant-backtester

# Or with environment variables
docker run -p 8501:8501 \
  -e STREAMLIT_SERVER_PORT=8501 \
  quant-backtester

# Push to Docker Hub
docker tag quant-backtester:latest username/quant-backtester:latest
docker push username/quant-backtester:latest
```

## Vercel Deployment (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel deploy

# Check deployment
vercel --prod
```

## Railway.app Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# View logs
railway logs
```

## Environment Configuration

Create `.env` file:

```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
API_HOST=0.0.0.0
API_PORT=8000
RISK_FREE_RATE=0.04
```

## Testing Before Deployment

```bash
# Run tests
pytest test_backtest.py -v --cov=.

# Check coverage
pytest test_backtest.py --cov-report=html

# Test API
curl http://localhost:8000/health
```

## Verification Checklist

- [ ] All 14 files present
- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests pass (`pytest -v`)
- [ ] Local app runs (`streamlit run app.py`)
- [ ] API responds (`curl http://localhost:8000/health`)
- [ ] No hardcoded secrets in code
- [ ] .env file created from .env.example

## Troubleshooting

**ImportError: No module named...**
```bash
pip install -r requirements.txt
```

**Streamlit app won't start**
```bash
# Clear cache
rm -rf ~/.streamlit
streamlit run app.py
```

**yfinance download fails**
```bash
# Check internet connection
pip install --upgrade yfinance
```

**Port 8501 already in use**
```bash
streamlit run app.py --server.port=8502
```

## Performance Optimization

- Enable data caching: `@st.cache_data`
- Limit historical period to 2-3 years
- Use vectorized operations (Pandas)
- Pre-calculate indicators

## Security Best Practices

- Never commit `.env` file
- Use environment variables for secrets
- Validate user inputs (Pydantic)
- Enable CORS only when needed
- Regular dependency updates

## Next Steps After Deployment

1. **Share URL** - Send to friends/investors
2. **Demo** - Record video of backtest
3. **Monitor** - Check logs regularly
4. **Update** - Add new strategies/tickers
5. **Optimize** - Improve performance

---

✅ Your app is deployed and ready!

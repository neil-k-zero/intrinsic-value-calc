const express = require('express');
const path = require('path');
const fs = require('fs');
const ValuationCalculator = require('./ValuationCalculator');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

// API Routes

// Get list of available companies
app.get('/api/companies', (req, res) => {
  try {
    const dataDir = path.join(__dirname, '..', 'data');
    const files = fs.readdirSync(dataDir)
      .filter(file => file.endsWith('.json'))
      .map(file => {
        const data = JSON.parse(fs.readFileSync(path.join(dataDir, file), 'utf8'));
        return {
          ticker: data.ticker,
          name: data.companyName,
          sector: data.sector,
          industry: data.industry
        };
      });
    
    res.json(files);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load company list' });
  }
});

// Get company data
app.get('/api/company/:ticker', (req, res) => {
  try {
    const ticker = req.params.ticker.toLowerCase();
    const dataPath = path.join(__dirname, '..', 'data', `${ticker}.json`);
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({ error: 'Company not found' });
    }
    
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load company data' });
  }
});

// Calculate intrinsic value
app.get('/api/valuation/:ticker', (req, res) => {
  try {
    const ticker = req.params.ticker.toLowerCase();
    const dataPath = path.join(__dirname, '..', 'data', `${ticker}.json`);
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({ error: 'Company not found' });
    }
    
    const companyData = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    const calculator = new ValuationCalculator(companyData);
    const results = calculator.calculateIntrinsicValue();
    
    res.json(results);
  } catch (error) {
    console.error('Valuation calculation error:', error);
    res.status(500).json({ error: 'Failed to calculate valuation' });
  }
});

// Batch valuation for comparison
app.post('/api/valuation/batch', (req, res) => {
  try {
    const { tickers } = req.body;
    
    if (!Array.isArray(tickers) || tickers.length === 0) {
      return res.status(400).json({ error: 'Invalid tickers array' });
    }
    
    const results = [];
    
    for (const ticker of tickers) {
      try {
        const dataPath = path.join(__dirname, '..', 'data', `${ticker.toLowerCase()}.json`);
        
        if (fs.existsSync(dataPath)) {
          const companyData = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
          const calculator = new ValuationCalculator(companyData);
          const valuation = calculator.calculateIntrinsicValue();
          
          results.push({
            ticker: ticker.toUpperCase(),
            success: true,
            data: valuation
          });
        } else {
          results.push({
            ticker: ticker.toUpperCase(),
            success: false,
            error: 'Company data not found'
          });
        }
      } catch (error) {
        results.push({
          ticker: ticker.toUpperCase(),
          success: false,
          error: error.message
        });
      }
    }
    
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: 'Failed to process batch valuation' });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Root route
app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>Company Value Calculator</title>
        <style>
          body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
          h1 { color: #333; }
          .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
          .method { color: #007acc; font-weight: bold; }
          .url { color: #666; }
          pre { background: #f0f0f0; padding: 10px; border-radius: 3px; overflow-x: auto; }
        </style>
      </head>
      <body>
        <h1>🏢 Company Value Calculator API</h1>
        <p>A comprehensive intrinsic value calculator using multiple valuation methods.</p>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
          <span class="method">GET</span> <span class="url">/api/companies</span>
          <p>Get list of available companies</p>
        </div>
        
        <div class="endpoint">
          <span class="method">GET</span> <span class="url">/api/company/:ticker</span>
          <p>Get detailed company data</p>
        </div>
        
        <div class="endpoint">
          <span class="method">GET</span> <span class="url">/api/valuation/:ticker</span>
          <p>Calculate intrinsic value for a company</p>
        </div>
        
        <div class="endpoint">
          <span class="method">POST</span> <span class="url">/api/valuation/batch</span>
          <p>Calculate valuations for multiple companies</p>
          <pre>{ "tickers": ["CAT", "AAPL", "MSFT"] }</pre>
        </div>
        
        <h2>Example Usage:</h2>
        <pre>
# Get Caterpillar valuation
curl http://localhost:3000/api/valuation/cat

# Get list of companies
curl http://localhost:3000/api/companies

# Batch valuation
curl -X POST http://localhost:3000/api/valuation/batch \\
  -H "Content-Type: application/json" \\
  -d '{"tickers": ["CAT"]}'
        </pre>
        
        <h2>Command Line Usage:</h2>
        <pre>
# Calculate Caterpillar intrinsic value
npm run calculate

# Calculate specific company
node src/calculate.js CAT
        </pre>
        
        <p><strong>Note:</strong> This tool is for educational purposes only and does not constitute investment advice.</p>
      </body>
    </html>
  `);
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Company Value Calculator API running on http://localhost:${PORT}`);
  console.log(`📊 Try: http://localhost:${PORT}/api/valuation/cat`);
  console.log(`📋 Available companies: http://localhost:${PORT}/api/companies`);
});

module.exports = app;

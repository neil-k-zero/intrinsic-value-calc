const fs = require('fs');
const path = require('path');

class CompanyDataBuilder {
  constructor() {
    this.template = this.loadTemplate();
  }

  loadTemplate() {
    const templatePath = path.join(__dirname, '..', 'data', 'template.json');
    return JSON.parse(fs.readFileSync(templatePath, 'utf8'));
  }

  createCompanyFile(ticker, companyData) {
    const data = { ...this.template, ...companyData };
    data.ticker = ticker.toUpperCase();
    data.lastUpdated = new Date().toISOString().split('T')[0];

    // Calculate derived metrics
    this.calculateDerivedMetrics(data);

    const filePath = path.join(__dirname, '..', 'data', `${ticker.toLowerCase()}.json`);
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    
    console.log(`✅ Company data file created: ${filePath}`);
    return filePath;
  }

  calculateDerivedMetrics(data) {
    const years = Object.keys(data.financialHistory).sort();
    
    years.forEach(year => {
      const yearData = data.financialHistory[year];
      
      // Calculate margins if missing
      if (yearData.revenue && yearData.grossProfit) {
        data.keyRatios.profitabilityRatios.grossMargin = yearData.grossProfit / yearData.revenue;
      }
      if (yearData.revenue && yearData.operatingIncome) {
        data.keyRatios.profitabilityRatios.operatingMargin = yearData.operatingIncome / yearData.revenue;
      }
      if (yearData.revenue && yearData.netIncome) {
        data.keyRatios.profitabilityRatios.netMargin = yearData.netIncome / yearData.revenue;
      }
      
      // Calculate ROE, ROA
      if (yearData.netIncome && yearData.shareholdersEquity) {
        data.keyRatios.profitabilityRatios.roe = yearData.netIncome / yearData.shareholdersEquity;
      }
      if (yearData.netIncome && yearData.totalAssets) {
        data.keyRatios.profitabilityRatios.roa = yearData.netIncome / yearData.totalAssets;
      }
      
      // Calculate leverage ratios
      if (yearData.totalDebt && yearData.shareholdersEquity) {
        data.keyRatios.leverageRatios.debtToEquity = yearData.totalDebt / yearData.shareholdersEquity;
      }
      if (yearData.totalDebt && yearData.totalAssets) {
        data.keyRatios.leverageRatios.debtToAssets = yearData.totalDebt / yearData.totalAssets;
      }
    });

    // Calculate growth rates
    if (years.length >= 2) {
      const oldestYear = years[0];
      const latestYear = years[years.length - 1];
      const numYears = years.length - 1;
      
      const oldestData = data.financialHistory[oldestYear];
      const latestData = data.financialHistory[latestYear];
      
      // Revenue growth
      if (oldestData.revenue && latestData.revenue) {
        data.growthMetrics.revenueGrowth5Y = Math.pow(latestData.revenue / oldestData.revenue, 1 / numYears) - 1;
      }
      
      // EPS growth
      if (oldestData.eps && latestData.eps) {
        data.growthMetrics.epsGrowth5Y = Math.pow(latestData.eps / oldestData.eps, 1 / numYears) - 1;
      }
      
      // FCF growth
      if (oldestData.freeCashFlow && latestData.freeCashFlow) {
        data.growthMetrics.fcfGrowth5Y = Math.pow(latestData.freeCashFlow / oldestData.freeCashFlow, 1 / numYears) - 1;
      }
    }
  }

  // Helper method to fetch data from APIs (placeholder)
  async fetchFromAPI(ticker) {
    console.log(`🔍 Note: API integration not implemented yet.`);
    console.log(`📝 Please manually populate the data for ${ticker}`);
    console.log(`💡 You can use financial websites like:`);
    console.log(`   - Yahoo Finance: https://finance.yahoo.com/quote/${ticker}`);
    console.log(`   - SEC Edgar: https://www.sec.gov/edgar/searchedgar/companysearch.html`);
    console.log(`   - Company annual reports (10-K forms)`);
    
    return this.template;
  }

  validateData(data) {
    const errors = [];
    const requiredFields = ['ticker', 'companyName', 'marketData', 'financialHistory'];
    
    requiredFields.forEach(field => {
      if (!data[field]) {
        errors.push(`Missing required field: ${field}`);
      }
    });

    // Validate financial history has at least one year
    if (data.financialHistory && Object.keys(data.financialHistory).length === 0) {
      errors.push('Financial history must contain at least one year of data');
    }

    // Validate market data
    if (data.marketData) {
      const requiredMarketFields = ['currentPrice', 'sharesOutstanding'];
      requiredMarketFields.forEach(field => {
        if (!data.marketData[field] || data.marketData[field] <= 0) {
          errors.push(`Invalid or missing market data field: ${field}`);
        }
      });
    }

    return errors;
  }

  generateReport(ticker) {
    const filePath = path.join(__dirname, '..', 'data', `${ticker.toLowerCase()}.json`);
    
    if (!fs.existsSync(filePath)) {
      console.log(`❌ Company data file not found: ${ticker.toUpperCase()}`);
      return;
    }

    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const errors = this.validateData(data);

    console.log(`\\n📊 DATA QUALITY REPORT: ${data.companyName} (${ticker.toUpperCase()})`);
    console.log('='.repeat(60));
    
    if (errors.length === 0) {
      console.log('✅ Data validation passed');
    } else {
      console.log('❌ Data validation failed:');
      errors.forEach(error => console.log(`   - ${error}`));
    }

    // Check data completeness
    const years = Object.keys(data.financialHistory);
    console.log(`\\n📈 Financial History: ${years.length} years (${years.join(', ')})`);
    
    const latestYear = years.sort().pop();
    const latestData = data.financialHistory[latestYear];
    
    console.log(`\\n💰 Latest Financial Data (${latestYear}):`);
    console.log(`   Revenue: $${(latestData.revenue / 1000000).toFixed(0)}M`);
    console.log(`   Net Income: $${(latestData.netIncome / 1000000).toFixed(0)}M`);
    console.log(`   Free Cash Flow: $${(latestData.freeCashFlow / 1000000).toFixed(0)}M`);
    console.log(`   Total Debt: $${(latestData.totalDebt / 1000000).toFixed(0)}M`);
    console.log(`   Shareholders Equity: $${(latestData.shareholdersEquity / 1000000).toFixed(0)}M`);

    console.log(`\\n📊 Key Ratios:`);
    console.log(`   P/E Ratio: ${data.keyRatios.valuationRatios.peRatio.toFixed(1)}x`);
    console.log(`   Debt/Equity: ${data.keyRatios.leverageRatios.debtToEquity.toFixed(2)}x`);
    console.log(`   ROE: ${(data.keyRatios.profitabilityRatios.roe * 100).toFixed(1)}%`);
    console.log(`   Current Ratio: ${data.keyRatios.liquidityRatios.currentRatio.toFixed(2)}x`);
  }

  listAvailableCompanies() {
    const dataDir = path.join(__dirname, '..', 'data');
    const files = fs.readdirSync(dataDir)
      .filter(file => file.endsWith('.json') && file !== 'template.json')
      .map(file => {
        const data = JSON.parse(fs.readFileSync(path.join(dataDir, file), 'utf8'));
        return {
          ticker: data.ticker,
          name: data.companyName,
          sector: data.sector,
          lastUpdated: data.lastUpdated
        };
      });

    console.log(`\\n📋 Available Companies (${files.length}):`);
    console.log('='.repeat(80));
    files.forEach(company => {
      console.log(`${company.ticker.padEnd(6)} | ${company.name.padEnd(30)} | ${company.sector || 'N/A'}`);
    });
  }
}

// CLI functionality
function main() {
  const builder = new CompanyDataBuilder();
  const command = process.argv[2];
  const ticker = process.argv[3];

  switch (command) {
    case 'create':
      if (!ticker) {
        console.log('Usage: node src/companyBuilder.js create <TICKER>');
        return;
      }
      console.log(`Creating data file for ${ticker.toUpperCase()}...`);
      builder.fetchFromAPI(ticker).then(data => {
        builder.createCompanyFile(ticker, data);
        console.log(`\\n💡 Next steps:`);
        console.log(`1. Edit data/${ticker.toLowerCase()}.json with real financial data`);
        console.log(`2. Run: node src/companyBuilder.js validate ${ticker}`);
        console.log(`3. Run: node src/calculate.js ${ticker}`);
      });
      break;

    case 'validate':
      if (!ticker) {
        console.log('Usage: node src/companyBuilder.js validate <TICKER>');
        return;
      }
      builder.generateReport(ticker);
      break;

    case 'list':
      builder.listAvailableCompanies();
      break;

    default:
      console.log(`\\n🏢 Company Data Builder\\n`);
      console.log('Available commands:');
      console.log('  create <TICKER>   - Create a new company data file');
      console.log('  validate <TICKER> - Validate existing company data');
      console.log('  list              - List all available companies');
      console.log('\\nExamples:');
      console.log('  node src/companyBuilder.js create AAPL');
      console.log('  node src/companyBuilder.js validate CAT');
      console.log('  node src/companyBuilder.js list');
  }
}

if (require.main === module) {
  main();
}

module.exports = CompanyDataBuilder;

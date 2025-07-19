const ValuationCalculator = require('./ValuationCalculator');
const fs = require('fs');
const path = require('path');

function loadCompanyData(ticker) {
  const dataPath = path.join(__dirname, '..', 'data', `${ticker.toLowerCase()}.json`);
  
  if (!fs.existsSync(dataPath)) {
    throw new Error(`Company data file not found: ${dataPath}`);
  }
  
  const rawData = fs.readFileSync(dataPath, 'utf8');
  return JSON.parse(rawData);
}

function formatCurrency(amount, currency = 'USD') {
  // Handle different currency formatting
  const locale = currency === 'DKK' ? 'da-DK' : 'en-US';
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
}

function formatPercent(value, decimals = 1) {
  return `${value.toFixed(decimals)}%`;
}

function printDivider(title = '') {
  const divider = '='.repeat(80);
  if (title) {
    const padding = Math.max(0, (80 - title.length - 2) / 2);
    console.log(divider);
    console.log(' '.repeat(Math.floor(padding)) + title + ' '.repeat(Math.ceil(padding)));
  }
  console.log(divider);
}

function printValuationResults(results, companyData) {
  // Get currency information from company data
  const baseCurrency = companyData.currency || 'USD';
  const displayCurrency = companyData.marketData?.currentPriceCurrency || 'USD';
  
  console.log('\\n')
  printDivider(`INTRINSIC VALUE ANALYSIS: ${results.companyName} (${results.ticker})`);
  
  // Display currency information if different from USD
  if (baseCurrency !== 'USD' || displayCurrency !== 'USD') {
    console.log(`\\n💱 CURRENCY INFORMATION:`);
    console.log(`Financial Data Currency: ${baseCurrency}`);
    console.log(`Stock Price Currency: ${displayCurrency}`);
    if (companyData.currencyNote) {
      console.log(`Note: ${companyData.currencyNote}`);
    }
  }
  
  console.log(`\\n📊 EXECUTIVE SUMMARY`);
  console.log(`Current Price:     ${formatCurrency(results.currentPrice, displayCurrency)}`);
  console.log(`Intrinsic Value:   ${formatCurrency(results.intrinsicValue, displayCurrency)}`);
  console.log(`Potential Upside:  ${formatPercent(results.upside)}`);
  console.log(`Margin of Safety:  ${formatPercent(results.marginOfSafety)}`);
  console.log(`Recommendation:    ${results.recommendation}`);
  console.log(`Confidence Level:  ${results.confidence}`);

  console.log(`\\n🔍 DETAILED VALUATION BREAKDOWN`);
  console.log(`\\n1. DISCOUNTED CASH FLOW MODELS:`);
  
  const fcfe = results.valuationBreakdown.fcfe;
  console.log(`   Free Cash Flow to Equity (FCFE):`);
  console.log(`   └─ Value per Share: ${formatCurrency(fcfe.valuePerShare, displayCurrency)}`);
  console.log(`   └─ Upside: ${formatPercent(fcfe.upside)}`);
  console.log(`   └─ Discount Rate: ${formatPercent(fcfe.assumptions.discountRate * 100)}`);
  console.log(`   └─ Growth Rate: ${formatPercent(fcfe.assumptions.initialGrowth * 100)}`);
  
  const fcff = results.valuationBreakdown.fcff;
  console.log(`\\n   Free Cash Flow to Firm (FCFF):`);
  console.log(`   └─ Value per Share: ${formatCurrency(fcff.valuePerShare, displayCurrency)}`);
  console.log(`   └─ Upside: ${formatPercent(fcff.upside)}`);
  console.log(`   └─ WACC: ${formatPercent(fcff.assumptions.wacc * 100)}`);
  console.log(`   └─ Net Debt: ${formatCurrency(fcff.assumptions.netDebt / 1000000, 'USD')}M`);

  const ddm = results.valuationBreakdown.ddm;
  console.log(`\\n   Dividend Discount Model:`);
  console.log(`   └─ Value per Share: ${formatCurrency(ddm.valuePerShare, displayCurrency)}`);
  console.log(`   └─ Upside: ${formatPercent(ddm.upside)}`);
  console.log(`   └─ Current Dividend: ${formatCurrency(ddm.assumptions.currentDividend, 'USD')}`);
  console.log(`   └─ Growth Rate: ${formatPercent(ddm.assumptions.dividendGrowthRate * 100)}`);

  console.log(`\\n2. RELATIVE VALUATION:`);
  const relative = results.valuationBreakdown.relative;
  
  console.log(`   P/E Ratio Analysis:`);
  console.log(`   └─ Value per Share: ${formatCurrency(relative.peValuation.valuePerShare, displayCurrency)}`);
  console.log(`   └─ Current P/E: ${relative.peValuation.currentPE.toFixed(1)}x`);
  console.log(`   └─ Fair P/E: ${relative.peValuation.fairPE.toFixed(1)}x`);
  console.log(`   └─ Upside: ${formatPercent(relative.peValuation.upside)}`);
  
  console.log(`\\n   EV/EBITDA Analysis:`);
  console.log(`   └─ Value per Share: ${formatCurrency(relative.evEbitdaValuation.valuePerShare, displayCurrency)}`);
  console.log(`   └─ Current Multiple: ${relative.evEbitdaValuation.currentMultiple.toFixed(1)}x`);
  console.log(`   └─ Fair Multiple: ${relative.evEbitdaValuation.fairMultiple.toFixed(1)}x`);
  console.log(`   └─ Upside: ${formatPercent(relative.evEbitdaValuation.upside)}`);

  console.log(`\\n3. ASSET-BASED VALUATION:`);
  const asset = results.valuationBreakdown.assetBased;
  
  console.log(`   Book Value: ${formatCurrency(asset.bookValue.valuePerShare, displayCurrency)} (${formatPercent(asset.bookValue.upside)} upside)`);
  console.log(`   Tangible Book Value: ${formatCurrency(asset.tangibleBookValue.valuePerShare, displayCurrency)} (${formatPercent(asset.tangibleBookValue.upside)} upside)`);
  console.log(`   Liquidation Value: ${formatCurrency(asset.liquidationValue.valuePerShare, displayCurrency)} (${formatPercent(asset.liquidationValue.upside)} upside)`);

  console.log(`\\n4. EARNINGS-BASED VALUATION:`);
  const earnings = results.valuationBreakdown.earningsBased;
  
  console.log(`   Capitalized Earnings: ${formatCurrency(earnings.capitalizedEarnings.valuePerShare, displayCurrency)} (${formatPercent(earnings.capitalizedEarnings.upside)} upside)`);
  console.log(`   Earnings Power Value: ${formatCurrency(earnings.earningsPowerValue.valuePerShare, displayCurrency)} (${formatPercent(earnings.earningsPowerValue.upside)} upside)`);

  console.log(`\\n📈 WEIGHTED VALUATION SUMMARY`);
  results.weightedValuations.forEach(val => {
    console.log(`   ${val.method.padEnd(35)} ${formatCurrency(val.value, displayCurrency).padStart(12)} (${formatPercent(val.weight * 100, 0)} weight)`);
  });

  console.log(`\\n⚠️  RISK ASSESSMENT`);
  const risk = results.riskMetrics;
  console.log(`Financial Risk:    ${risk.financial.riskLevel}`);
  console.log(`└─ Debt/Equity:    ${risk.financial.debtToEquity.toFixed(2)}x`);
  console.log(`└─ Current Ratio:  ${risk.financial.currentRatio.toFixed(2)}x`);
  console.log(`└─ Interest Cover: ${risk.financial.interestCoverage.toFixed(1)}x`);
  
  console.log(`\\nBusiness Risk:     ${risk.business.volatilityRisk}`);
  console.log(`└─ Beta:           ${risk.business.beta.toFixed(2)}`);
  console.log(`└─ Industry:       ${risk.business.industryRisk}`);
  
  console.log(`\\nValuation Risk:    ${risk.valuation.valuationRisk}`);
  console.log(`└─ P/E Ratio:      ${risk.valuation.peRatio.toFixed(1)}x`);
  console.log(`└─ P/B Ratio:      ${risk.valuation.pbRatio.toFixed(1)}x`);

  // Enhanced Dividend Analysis
  if (results.dividendAnalysis) {
    const dividend = results.dividendAnalysis;
    console.log(`\\n💰 COMPREHENSIVE DIVIDEND ANALYSIS`);
    console.log(`\\nCurrent Dividend Metrics:`);
    console.log(`   Annual Dividend:       ${formatCurrency(dividend.currentMetrics.annualDividend, 'USD')}`);
    
    // Show original currency amount if different currency
    if (baseCurrency !== 'USD' && companyData.dividendInfo?.currentAnnualDividend) {
      console.log(`   Annual Dividend (${baseCurrency}): ${formatCurrency(companyData.dividendInfo.currentAnnualDividend, baseCurrency)}`);
    }
    
    console.log(`   Dividend Yield:        ${formatPercent(dividend.currentMetrics.dividendYield * 100)}`);
    console.log(`   Payout Ratio:          ${formatPercent(dividend.currentMetrics.payoutRatio * 100)}`);
    console.log(`   Payment Frequency:     ${dividend.currentMetrics.payoutFrequency}`);
    console.log(`   Next Ex-Date:          ${dividend.currentMetrics.nextExDate}`);
    console.log(`   Next Payment:          ${dividend.currentMetrics.nextPayDate}`);

    console.log(`\\nDividend Growth Track Record:`);
    console.log(`   Status:                ${dividend.aristocratStatus.status}`);
    console.log(`   Consecutive Growth:    ${dividend.growthAnalysis.consecutiveYears} years`);
    console.log(`   5-Year Growth Rate:    ${formatPercent(dividend.growthAnalysis.growthRate5Y * 100)}`);
    console.log(`   10-Year Growth Rate:   ${formatPercent(dividend.growthAnalysis.growthRate10Y * 100)}`);
    console.log(`   Average Annual Increase: ${formatCurrency(dividend.growthAnalysis.averageIncrease, baseCurrency)}`);
    console.log(`   Last Dividend Cut:     ${dividend.growthAnalysis.lastCut}`);

    console.log(`\\nSustainability Analysis:`);
    console.log(`   Earnings Coverage:     ${dividend.sustainability.earningsCoverage.toFixed(1)}x`);
    console.log(`   FCF Coverage:          ${dividend.sustainability.fcfCoverage.toFixed(1)}x`);
    console.log(`   Retention Ratio:       ${formatPercent(dividend.sustainability.retentionRatio * 100)}`);
    console.log(`   Sustainability Score:  ${dividend.sustainability.sustainabilityScore}`);
    
    console.log(`\\nPeer Comparison:`);
    console.log(`   Industry Avg Yield:    ${formatPercent(dividend.peerComparison.industryAverageDividendYield * 100)}`);
    console.log(`   Relative Yield:        ${dividend.peerComparison.relativeYieldRanking}`);
    console.log(`   Relative Growth:       ${dividend.peerComparison.relativeGrowthRanking}`);
    console.log(`   Reliability Ranking:   ${dividend.peerComparison.reliabilityRanking}`);

    console.log(`\\nInvestment Projections (at current price):`);
    console.log(`   Yield on Cost (10Y):   ${dividend.dividendInvestmentMetrics.yieldOnCost10Y.toFixed(1)}%`);
    console.log(`   Yield on Cost (20Y):   ${dividend.dividendInvestmentMetrics.yieldOnCost20Y.toFixed(1)}%`);
    
    const totalReturn = dividend.dividendInvestmentMetrics.totalReturnContribution;
    console.log(`\\nTotal Return Breakdown:`);
    console.log(`   Dividend Component:    ${totalReturn.dividendComponent}`);
    console.log(`   Price Appreciation:    ${totalReturn.priceAppreciationComponent}`);
    console.log(`   Expected Total Return: ${totalReturn.totalExpectedReturn}`);

    console.log(`\\nDividend Reinvestment Scenarios ($10,000 investment):`);
    const drip = dividend.dividendInvestmentMetrics.reinvestmentValue;
    Object.keys(drip).forEach(period => {
      const data = drip[period];
      console.log(`   ${period}: ${formatCurrency(data.finalValue)} (${data.totalReturn} total, ${data.annualizedReturn} annually)`);
    });

    console.log(`\\nProjected Future Dividends:`);
    dividend.projectedDividends.slice(0, 5).forEach(proj => {
      console.log(`   ${proj.year}: ${formatCurrency(proj.projectedDividend)} (Yield on Cost: ${proj.yieldOnCost})`);
    });
  }

  console.log(`\\n💡 INVESTMENT SUMMARY`);
  console.log(`${results.summary.valuation}`);
  console.log(`${results.summary.opportunity}`);
  console.log(`${results.summary.risk}`);
  console.log(`${results.summary.recommendation}`);

  printDivider();
  console.log(`\\n⚠️  IMPORTANT DISCLAIMER:`);
  console.log(`This analysis is for educational purposes only and does not constitute`);
  console.log(`investment advice. Always consult with qualified financial professionals`);
  console.log(`and conduct your own research before making investment decisions.`);
  printDivider();
}

function main() {
  const ticker = process.argv[2] || 'CAT';
  
  try {
    console.log(`Loading data for ${ticker.toUpperCase()}...`);
    const companyData = loadCompanyData(ticker);
    
    console.log(`Calculating intrinsic value using multiple valuation methods...`);
    const calculator = new ValuationCalculator(companyData);
    const results = calculator.calculateIntrinsicValue();
    
    printValuationResults(results, companyData);
    
    // Optional: Save results to file
    const outputPath = path.join(__dirname, '..', 'output', `${ticker.toLowerCase()}_valuation_${new Date().toISOString().split('T')[0]}.json`);
    const outputDir = path.dirname(outputPath);
    
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
    console.log(`\\n📁 Detailed results saved to: ${outputPath}`);
    
  } catch (error) {
    console.error(`\\n❌ Error: ${error.message}`);
    console.log(`\\n💡 Available company data files:`);
    
    const dataDir = path.join(__dirname, '..', 'data');
    if (fs.existsSync(dataDir)) {
      const files = fs.readdirSync(dataDir)
        .filter(file => file.endsWith('.json'))
        .map(file => file.replace('.json', '').toUpperCase());
      
      if (files.length > 0) {
        files.forEach(file => console.log(`   - ${file}`));
        console.log(`\\nUsage: node src/calculate.js <TICKER>`);
        console.log(`Example: node src/calculate.js CAT`);
      } else {
        console.log(`   No company data files found in ${dataDir}`);
      }
    }
  }
}

if (require.main === module) {
  main();
}

module.exports = { loadCompanyData, formatCurrency, formatPercent, printValuationResults };

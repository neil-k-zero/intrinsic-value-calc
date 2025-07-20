const fs = require('fs');
const path = require('path');

class ValuationCalculator {
  constructor(companyData) {
    this.data = companyData;
    this.currentYear = new Date().getFullYear();
    
    // Handle currency conversion if needed
    this.normalizedData = this.convertToUSD(companyData);
  }

  // Currency conversion helper
  convertToUSD(data) {
    // If data is already in USD, return as-is
    if (!data.currency || data.currency === 'USD') {
      return data;
    }

    // Make a deep copy to avoid modifying original data
    const normalizedData = JSON.parse(JSON.stringify(data));
    
    if (data.currency === 'DKK' && data.exchangeRate) {
      const conversionRate = data.exchangeRate.dkkToUsd;
      
      // Convert financial history data from DKK to USD
      Object.keys(normalizedData.financialHistory).forEach(year => {
        const yearData = normalizedData.financialHistory[year];
        
        // Convert monetary values (but not ratios, percentages, or share counts)
        const monetaryFields = [
          'revenue', 'grossProfit', 'operatingIncome', 'netIncome', 
          'freeCashFlow', 'operatingCashFlow', 'capex', 'totalAssets', 
          'totalDebt', 'cashAndEquivalents', 'shareholdersEquity',
          'workingCapital', 'totalEquity', 'retainedEarnings'
        ];
        
        monetaryFields.forEach(field => {
          if (yearData[field] !== undefined && yearData[field] !== null) {
            yearData[field] = yearData[field] * conversionRate;
          }
        });
        
        // Convert per-share values
        if (yearData.bookValuePerShare) {
          yearData.bookValuePerShare = yearData.bookValuePerShare * conversionRate;
        }
        if (yearData.eps) {
          yearData.eps = yearData.eps * conversionRate;
        }
        if (yearData.dividend) {
          yearData.dividend = yearData.dividend * conversionRate;
        }
      });
      
      // Convert dividend info to USD
      if (normalizedData.dividendInfo) {
        if (normalizedData.dividendInfo.currentAnnualDividend) {
          normalizedData.dividendInfo.currentAnnualDividend = 
            normalizedData.dividendInfo.currentAnnualDividend * conversionRate;
        }
      }
      
      // Mark as converted to USD
      normalizedData.currency = 'USD';
      normalizedData.convertedFromCurrency = data.currency;
      normalizedData.conversionRate = conversionRate;
    }
    
    return normalizedData;
  }

  // Discounted Cash Flow to Equity (FCFE) Model
  calculateFCFE() {
    const years = Object.keys(this.normalizedData.financialHistory).sort();
    const latestYear = years[years.length - 1];
    const latestData = this.normalizedData.financialHistory[latestYear];
    
    // Check if latest FCF is negative or zero - FCFE model not meaningful
    if (latestData.freeCashFlow <= 0) {
      return {
        method: 'FCFE',
        totalValue: 0,
        valuePerShare: 0,
        currentPrice: this.data.marketData.currentPrice,
        upside: 0,
        notApplicable: true,
        reason: `FCFE model not applicable due to negative free cash flow (${(latestData.freeCashFlow / 1000000).toFixed(0)}M)`,
        assumptions: {
          initialGrowth: 0,
          terminalGrowth: this.data.assumptions.terminalGrowthRate,
          discountRate: this.calculateCostOfEquity(),
          yearsProjected: 5
        }
      };
    }
    
    // Calculate historical FCF growth
    const fcfHistory = years.map(year => this.normalizedData.financialHistory[year].freeCashFlow);
    const avgGrowthRate = this.calculateCAGR(fcfHistory);
    
    // Use conservative growth rate
    const initialGrowthRate = Math.min(avgGrowthRate, this.data.growthMetrics.fcfGrowth5Y, 0.15);
    const terminalGrowthRate = this.data.assumptions.terminalGrowthRate;
    const discountRate = this.calculateCostOfEquity();
    
    let intrinsicValue = 0;
    let currentFCF = latestData.freeCashFlow;
    
    // High growth period (years 1-5)
    for (let year = 1; year <= 5; year++) {
      const growthRate = initialGrowthRate * Math.pow(0.85, year - 1); // Declining growth
      currentFCF = currentFCF * (1 + growthRate);
      const presentValue = currentFCF / Math.pow(1 + discountRate, year);
      intrinsicValue += presentValue;
    }
    
    // Stable growth period (terminal value)
    const terminalFCF = currentFCF * (1 + terminalGrowthRate);
    const terminalValue = terminalFCF / (discountRate - terminalGrowthRate);
    const presentTerminalValue = terminalValue / Math.pow(1 + discountRate, 5);
    intrinsicValue += presentTerminalValue;
    
    const valuePerShare = intrinsicValue / this.data.marketData.sharesOutstanding;
    
    return {
      method: 'FCFE',
      totalValue: intrinsicValue,
      valuePerShare,
      currentPrice: this.data.marketData.currentPrice,
      upside: (valuePerShare / this.data.marketData.currentPrice - 1) * 100,
      assumptions: {
        initialGrowth: initialGrowthRate,
        terminalGrowth: terminalGrowthRate,
        discountRate,
        yearsProjected: 5
      }
    };
  }

  // Discounted Cash Flow to Firm (FCFF) Model
  calculateFCFF() {
    const years = Object.keys(this.normalizedData.financialHistory).sort();
    const latestYear = years[years.length - 1];
    const latestData = this.normalizedData.financialHistory[latestYear];
    
    // Calculate FCFF = Operating Cash Flow - CapEx + Tax Shield on Interest
    const interestExpense = latestData.totalDebt * 0.04; // Estimated interest rate
    const taxShield = interestExpense * this.data.assumptions.taxRate;
    const fcff = latestData.operatingCashFlow - latestData.capex + taxShield;
    
    const wacc = this.calculateWACC();
    const terminalGrowthRate = this.data.assumptions.terminalGrowthRate;
    const initialGrowthRate = Math.min(this.data.growthMetrics.revenueGrowth5Y, 0.12);
    
    let firmValue = 0;
    let currentFCFF = fcff;
    
    // Project FCFF for 10 years
    for (let year = 1; year <= 10; year++) {
      const growthRate = year <= 5 ? initialGrowthRate : 
                        initialGrowthRate * (1 - (year - 5) / 5 * 0.7);
      currentFCFF = currentFCFF * (1 + growthRate);
      const presentValue = currentFCFF / Math.pow(1 + wacc, year);
      firmValue += presentValue;
    }
    
    // Terminal value
    const terminalFCFF = currentFCFF * (1 + terminalGrowthRate);
    const terminalValue = terminalFCFF / (wacc - terminalGrowthRate);
    const presentTerminalValue = terminalValue / Math.pow(1 + wacc, 10);
    firmValue += presentTerminalValue;
    
    // Subtract net debt to get equity value
    const netDebt = latestData.totalDebt - latestData.cashAndEquivalents;
    const equityValue = firmValue - netDebt;
    const valuePerShare = equityValue / this.data.marketData.sharesOutstanding;
    
    return {
      method: 'FCFF',
      firmValue,
      equityValue,
      valuePerShare,
      currentPrice: this.data.marketData.currentPrice,
      upside: (valuePerShare / this.data.marketData.currentPrice - 1) * 100,
      assumptions: {
        wacc,
        initialGrowth: initialGrowthRate,
        terminalGrowth: terminalGrowthRate,
        netDebt
      }
    };
  }

  // Dividend Discount Model (Gordon Growth Model)
  calculateDDM() {
    const years = Object.keys(this.normalizedData.financialHistory).sort();
    const latestYear = years[years.length - 1];
    const latestData = this.normalizedData.financialHistory[latestYear];
    
    const currentDividend = latestData.dividend;
    const dividendGrowthRate = this.data.assumptions.dividendGrowthRate;
    const requiredReturn = this.calculateCostOfEquity();
    
    // Gordon Growth Model: P = D1 / (r - g)
    const nextYearDividend = currentDividend * (1 + dividendGrowthRate);
    const valuePerShare = nextYearDividend / (requiredReturn - dividendGrowthRate);
    
    return {
      method: 'DDM (Gordon Growth)',
      valuePerShare,
      currentPrice: this.data.marketData.currentPrice,
      upside: (valuePerShare / this.data.marketData.currentPrice - 1) * 100,
      assumptions: {
        currentDividend,
        dividendGrowthRate,
        requiredReturn,
        nextYearDividend
      }
    };
  }

  // Relative Valuation Methods
  calculateRelativeValuation() {
    const currentRatios = this.data.keyRatios.valuationRatios;
    const benchmarks = this.data.industryBenchmarks;
    const latestData = this.normalizedData.financialHistory[Object.keys(this.normalizedData.financialHistory).sort().pop()];
    
    const results = {
      peValuation: {
        method: 'P/E Relative Valuation',
        fairPE: benchmarks.averagePE,
        currentPE: currentRatios.peRatio,
        valuePerShare: latestData.eps * benchmarks.averagePE,
        upside: ((latestData.eps * benchmarks.averagePE) / this.data.marketData.currentPrice - 1) * 100
      },
      
      pbValuation: {
        method: 'P/B Relative Valuation',
        fairPB: benchmarks.averagePB,
        currentPB: currentRatios.pbRatio,
        valuePerShare: latestData.bookValuePerShare * benchmarks.averagePB,
        upside: ((latestData.bookValuePerShare * benchmarks.averagePB) / this.data.marketData.currentPrice - 1) * 100
      },
      
      evEbitdaValuation: {
        method: 'EV/EBITDA Relative Valuation',
        fairMultiple: 12, // Industry average
        currentMultiple: currentRatios.evToEbitda,
        ebitda: latestData.operatingIncome + (latestData.operatingIncome * 0.15), // Estimated EBITDA
        enterpriseValue: this.calculateFairEV(latestData.operatingIncome * 1.15, 12),
        equityValue: this.calculateFairEV(latestData.operatingIncome * 1.15, 12) - (latestData.totalDebt - latestData.cashAndEquivalents),
        valuePerShare: (this.calculateFairEV(latestData.operatingIncome * 1.15, 12) - (latestData.totalDebt - latestData.cashAndEquivalents)) / this.data.marketData.sharesOutstanding
      }
    };
    
    results.evEbitdaValuation.upside = (results.evEbitdaValuation.valuePerShare / this.data.marketData.currentPrice - 1) * 100;
    
    return results;
  }

  // Asset-Based Valuation
  calculateAssetBasedValuation() {
    const latestData = this.normalizedData.financialHistory[Object.keys(this.normalizedData.financialHistory).sort().pop()];
    
    return {
      bookValue: {
        method: 'Book Value',
        valuePerShare: latestData.bookValuePerShare,
        upside: (latestData.bookValuePerShare / this.data.marketData.currentPrice - 1) * 100
      },
      
      tangibleBookValue: {
        method: 'Tangible Book Value',
        tangibleBV: latestData.shareholdersEquity - (latestData.totalAssets * 0.07), // Estimated intangibles
        valuePerShare: (latestData.shareholdersEquity - (latestData.totalAssets * 0.07)) / this.data.marketData.sharesOutstanding,
        upside: ((latestData.shareholdersEquity - (latestData.totalAssets * 0.07)) / this.data.marketData.sharesOutstanding / this.data.marketData.currentPrice - 1) * 100
      },
      
      liquidationValue: {
        method: 'Liquidation Value (Conservative)',
        // Assume 70% recovery on assets, minus all liabilities
        recoveryRate: 0.7,
        liquidationValue: latestData.totalAssets * 0.7 - (latestData.totalAssets - latestData.shareholdersEquity),
        valuePerShare: (latestData.totalAssets * 0.7 - (latestData.totalAssets - latestData.shareholdersEquity)) / this.data.marketData.sharesOutstanding,
        upside: ((latestData.totalAssets * 0.7 - (latestData.totalAssets - latestData.shareholdersEquity)) / this.data.marketData.sharesOutstanding / this.data.marketData.currentPrice - 1) * 100
      }
    };
  }

  // Earnings-Based Valuation
  calculateEarningsBasedValuation() {
    const years = Object.keys(this.normalizedData.financialHistory).sort();
    const earningsHistory = years.map(year => this.normalizedData.financialHistory[year].netIncome);
    const avgEarnings = earningsHistory.reduce((a, b) => a + b, 0) / earningsHistory.length;
    
    const costOfEquity = this.calculateCostOfEquity();
    const capitalizedEarnings = avgEarnings / costOfEquity;
    
    return {
      capitalizedEarnings: {
        method: 'Capitalized Earnings',
        avgEarnings,
        capitalizationRate: costOfEquity,
        totalValue: capitalizedEarnings,
        valuePerShare: capitalizedEarnings / this.data.marketData.sharesOutstanding,
        upside: ((capitalizedEarnings / this.data.marketData.sharesOutstanding) / this.data.marketData.currentPrice - 1) * 100
      },
      
      earningsPowerValue: {
        method: 'Earnings Power Value (No Growth)',
        normalizedEarnings: avgEarnings,
        valuePerShare: (avgEarnings / this.data.marketData.sharesOutstanding) / costOfEquity,
        upside: (((avgEarnings / this.data.marketData.sharesOutstanding) / costOfEquity) / this.data.marketData.currentPrice - 1) * 100
      }
    };
  }

  // Helper Methods
  calculateCostOfEquity() {
    const riskFreeRate = this.data.riskFactors.riskFreeRate;
    const beta = this.data.marketData.beta;
    const marketRiskPremium = this.data.riskFactors.marketRiskPremium;
    const specificRisk = this.data.riskFactors.specificRiskPremium;
    
    // CAPM: Re = Rf + β(Rm - Rf) + Specific Risk
    return riskFreeRate + beta * marketRiskPremium + specificRisk;
  }

  calculateWACC() {
    const latestData = this.normalizedData.financialHistory[Object.keys(this.normalizedData.financialHistory).sort().pop()];
    const equityValue = this.data.marketData.marketCap;
    const debtValue = latestData.totalDebt;
    const totalValue = equityValue + debtValue;
    
    const costOfEquity = this.calculateCostOfEquity();
    const costOfDebt = 0.04; // Estimated based on current rates
    const taxRate = this.data.assumptions.taxRate;
    
    // WACC = (E/V * Re) + (D/V * Rd * (1-T))
    const wacc = (equityValue / totalValue) * costOfEquity + 
                 (debtValue / totalValue) * costOfDebt * (1 - taxRate);
    
    return wacc;
  }

  calculateCAGR(values) {
    if (values.length < 2) return 0;
    const beginValue = values[0];
    const endValue = values[values.length - 1];
    const years = values.length - 1;
    return Math.pow(endValue / beginValue, 1 / years) - 1;
  }

  calculateFairEV(ebitda, multiple) {
    return ebitda * multiple;
  }

  // Dynamic Weight Calculation for Robust Valuation
  calculateDynamicWeights(fcfeResult, fcffResult, ddmResult, relativeResults, assetResults, earningsResults) {
    const industry = this.data.industry;
    const latestData = this.normalizedData.financialHistory[Object.keys(this.normalizedData.financialHistory).sort().pop()];
    const marketCap = this.data.marketData.marketCap;
    const debtToEquity = this.data.keyRatios.leverageRatios.debtToEquity;
    const beta = this.data.marketData.beta;
    
    // Base weights (conservative approach)
    let weights = {
      fcfe: 0.25,
      fcff: 0.25,
      ddm: 0.15,
      peRelative: 0.15,
      evEbitda: 0.10,
      bookValue: 0.05,
      capitalizedEarnings: 0.05
    };

    // Industry-specific adjustments
    if (industry.includes("Heavy Construction") || industry.includes("Farm") || industry.includes("Machinery")) {
      // Asset-heavy cyclical business - increase asset-based and relative methods
      weights.fcfe = 0.20; // Reduce DCF weight due to cyclicality
      weights.fcff = 0.20;
      weights.ddm = 0.10; // Lower dividend weight for cyclical
      weights.peRelative = 0.20; // Increase relative valuation
      weights.evEbitda = 0.15; // Important for industrial companies
      weights.bookValue = 0.10; // Higher asset-based weight
      weights.capitalizedEarnings = 0.05;
    }

    // Company size adjustments
    if (marketCap > 100000000000) { // Large cap (>$100B)
      // Mature large companies - emphasize earnings stability
      weights.capitalizedEarnings += 0.05;
      weights.ddm += 0.05;
      weights.fcfe -= 0.05;
      weights.fcff -= 0.05;
    }

    // Debt level adjustments
    if (debtToEquity > 2) {
      // High debt companies - FCFF more important than FCFE
      weights.fcff += 0.10;
      weights.fcfe -= 0.10;
    }

    // Cyclicality adjustments (beta-based)
    if (beta > 1.3) {
      // High-beta cyclical companies - reduce growth-dependent methods
      weights.fcfe -= 0.05;
      weights.fcff -= 0.05;
      weights.peRelative += 0.05;
      weights.evEbitda += 0.05;
    }

    // Dividend policy adjustments
    const dividendYield = this.data.dividendInfo?.currentDividendYield || 0;
    if (dividendYield > 0.03) { // >3% dividend yield
      weights.ddm += 0.05;
      weights.fcfe -= 0.025;
      weights.fcff -= 0.025;
    }

    // Quality checks - reduce weight for unreliable valuations
    const currentPrice = this.data.marketData.currentPrice;
    
    // Check for extreme valuations and reduce their weight
    if (Math.abs(fcfeResult.upside) > 100) weights.fcfe *= 0.5;
    if (Math.abs(fcffResult.upside) > 100) weights.fcff *= 0.5;
    if (Math.abs(ddmResult.upside) > 100) weights.ddm *= 0.5;
    if (Math.abs(relativeResults.peValuation.upside) > 100) weights.peRelative *= 0.5;
    if (Math.abs(relativeResults.evEbitdaValuation.upside) > 100) weights.evEbitda *= 0.5;

    // Filter out negative or unrealistic valuations
    if (fcfeResult.valuePerShare <= 0 || Math.abs(fcfeResult.upside) > 150 || fcfeResult.notApplicable) weights.fcfe = 0;
    if (fcffResult.valuePerShare <= 0 || Math.abs(fcffResult.upside) > 150) weights.fcff = 0;
    if (ddmResult.valuePerShare <= 0 || Math.abs(ddmResult.upside) > 150) weights.ddm = 0;
    if (assetResults.bookValue.valuePerShare <= 0) weights.bookValue = 0;
    if (assetResults.liquidationValue.valuePerShare <= 0) weights.bookValue = 0; // Also affects book value weight

    // For asset-heavy companies, ensure minimum asset-based representation
    if (industry.includes("Heavy Construction") || industry.includes("Farm") || industry.includes("Machinery")) {
      if (weights.bookValue === 0 && assetResults.tangibleBookValue.valuePerShare > 0) {
        weights.bookValue = 0.05; // Minimum weight for asset-based approach
      }
    }

    // Normalize weights to sum to 1
    const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
    Object.keys(weights).forEach(key => {
      weights[key] = weights[key] / totalWeight;
    });

    return weights;
  }

  // Comprehensive Dividend Analysis
  calculateDividendAnalysis() {
    if (!this.data.dividendInfo) {
      return null;
    }

    const dividendInfo = this.data.dividendInfo;
    const latestYear = Object.keys(this.normalizedData.financialHistory).sort().pop();
    const latestData = this.normalizedData.financialHistory[latestYear];
    
    return {
      currentMetrics: {
        annualDividend: this.normalizedData.dividendInfo ? this.normalizedData.dividendInfo.currentAnnualDividend : dividendInfo.currentAnnualDividend,
        dividendYield: dividendInfo.currentDividendYield,
        payoutRatio: dividendInfo.payoutRatio,
        payoutFrequency: dividendInfo.payoutFrequency,
        nextExDate: dividendInfo.nextExDividendDate,
        nextPayDate: dividendInfo.nextPaymentDate
      },
      
      growthAnalysis: {
        consecutiveYears: dividendInfo.consecutiveYearsOfGrowth,
        growthRate5Y: dividendInfo.dividendGrowthAnalysis.growthRate5Y,
        growthRate10Y: dividendInfo.dividendGrowthAnalysis.growthRate10Y,
        cagr: dividendInfo.dividendGrowthAnalysis.compoundAnnualGrowthRate,
        averageIncrease: dividendInfo.dividendGrowthAnalysis.averageAnnualIncrease,
        lastCut: dividendInfo.dividendGrowthAnalysis.lastCut
      },
      
      sustainability: {
        earningsCoverage: dividendInfo.dividendMetrics.earningsCoverage,
        fcfCoverage: dividendInfo.dividendMetrics.freeCashFlowCoverage,
        payoutRatio: dividendInfo.payoutRatio,
        retentionRatio: dividendInfo.dividendMetrics.retentionRatio,
        sustainabilityScore: dividendInfo.dividendGrowthAnalysis.sustainabilityScore,
        impliedGrowthRate: dividendInfo.dividendMetrics.impliedGrowthRate
      },
      
      aristocratStatus: {
        isDividendAristocrat: dividendInfo.aristocratStatus,
        aristocratSince: dividendInfo.aristocratSince,
        yearsOfConsecutiveGrowth: dividendInfo.consecutiveYearsOfGrowth,
        status: dividendInfo.consecutiveYearsOfGrowth >= 25 ? 'Dividend Aristocrat' : 
                dividendInfo.consecutiveYearsOfGrowth >= 10 ? 'Dividend Achiever' : 
                'Regular Dividend Payer'
      },
      
      peerComparison: dividendInfo.peerComparison,
      
      projectedDividends: this.projectFutureDividends(),
      
      dividendInvestmentMetrics: {
        yieldOnCost10Y: this.calculateYieldOnCost(10),
        yieldOnCost20Y: this.calculateYieldOnCost(20),
        totalReturnContribution: this.calculateDividendTotalReturn(),
        reinvestmentValue: this.calculateDividendReinvestmentValue()
      },
      
      riskFactors: {
        cyclicalRisk: 'Medium - Heavy machinery industry is cyclical',
        payoutStability: dividendInfo.payoutRatio < 0.6 ? 'High' : dividendInfo.payoutRatio < 0.8 ? 'Medium' : 'Low',
        fcfStability: dividendInfo.dividendMetrics.freeCashFlowCoverage > 2 ? 'High' : 'Medium',
        debtConcern: latestData.totalDebt / latestData.shareholdersEquity > 3 ? 'High' : 'Low'
      }
    };
  }

  projectFutureDividends() {
    if (!this.data.dividendInfo) return [];
    
    const currentDividend = this.data.dividendInfo.currentAnnualDividend;
    const growthRate = this.data.dividendInfo.dividendGrowthRate;
    const conservativeRate = this.data.assumptions.dividendAssumptions?.conservativeDividendGrowth || 0.05;
    
    const projections = [];
    for (let year = 1; year <= 10; year++) {
      // Use declining growth rate over time
      const adjustedGrowthRate = year <= 5 ? growthRate : growthRate * (1 - (year - 5) * 0.1);
      const finalGrowthRate = Math.max(adjustedGrowthRate, conservativeRate);
      
      const projectedDividend = currentDividend * Math.pow(1 + finalGrowthRate, year);
      const currentPrice = this.data.marketData.currentPrice;
      const yieldOnCost = projectedDividend / currentPrice;
      
      projections.push({
        year: new Date().getFullYear() + year,
        projectedDividend: projectedDividend.toFixed(2),
        yieldOnCost: (yieldOnCost * 100).toFixed(1) + '%',
        growthRateUsed: (finalGrowthRate * 100).toFixed(1) + '%'
      });
    }
    
    return projections;
  }

  calculateYieldOnCost(years) {
    if (!this.data.dividendInfo) return 0;
    
    const currentDividend = this.data.dividendInfo.currentAnnualDividend;
    const growthRate = this.data.dividendInfo.dividendGrowthRate;
    const currentPrice = this.data.marketData.currentPrice;
    
    const futureDividend = currentDividend * Math.pow(1 + growthRate, years);
    return (futureDividend / currentPrice) * 100;
  }

  calculateDividendTotalReturn() {
    if (!this.data.dividendInfo) return 0;
    
    const dividendYield = this.data.dividendInfo.currentDividendYield;
    const priceAppreciation = 0.06; // Assumed long-term price appreciation
    const totalReturn = dividendYield + priceAppreciation;
    
    return {
      dividendComponent: (dividendYield * 100).toFixed(1) + '%',
      priceAppreciationComponent: (priceAppreciation * 100).toFixed(1) + '%',
      totalExpectedReturn: (totalReturn * 100).toFixed(1) + '%'
    };
  }

  calculateDividendReinvestmentValue() {
    if (!this.data.dividendInfo) return {};
    
    const initialInvestment = 10000; // $10,000 initial investment
    const currentDividend = this.data.dividendInfo.currentAnnualDividend;
    const currentPrice = this.data.marketData.currentPrice;
    const dividendYield = this.data.dividendInfo.currentDividendYield;
    const growthRate = this.data.dividendInfo.dividendGrowthRate;
    
    const scenarios = [10, 20, 30];
    const results = {};
    
    scenarios.forEach(years => {
      // Calculate DRIP value assuming 3% annual price appreciation
      const priceGrowthRate = 0.03;
      const finalPrice = currentPrice * Math.pow(1 + priceGrowthRate, years);
      const finalDividend = currentDividend * Math.pow(1 + growthRate, years);
      
      // Simplified DRIP calculation
      const totalShares = initialInvestment / currentPrice;
      const additionalShares = totalShares * dividendYield * years * 0.7; // Rough estimate
      const finalShares = totalShares + additionalShares;
      const finalValue = finalShares * finalPrice;
      
      results[`${years}Years`] = {
        finalValue: Math.round(finalValue),
        totalReturn: ((finalValue / initialInvestment - 1) * 100).toFixed(1) + '%',
        annualizedReturn: ((Math.pow(finalValue / initialInvestment, 1/years) - 1) * 100).toFixed(1) + '%',
        shares: finalShares.toFixed(1),
        yieldOnCost: ((finalDividend / currentPrice) * 100).toFixed(1) + '%'
      };
    });
    
    return results;
  }

  // Comprehensive Valuation Summary with Robust Weighting
  calculateIntrinsicValue() {
    const fcfeResult = this.calculateFCFE();
    const fcffResult = this.calculateFCFF();
    const ddmResult = this.calculateDDM();
    const relativeResults = this.calculateRelativeValuation();
    const assetResults = this.calculateAssetBasedValuation();
    const earningsResults = this.calculateEarningsBasedValuation();

    // Dynamic weight calculation based on company/industry characteristics
    const weights = this.calculateDynamicWeights(fcfeResult, fcffResult, ddmResult, relativeResults, assetResults, earningsResults);

    // Collect all value per share estimates with dynamic weights
    const valuations = [
      { method: fcfeResult.method, value: fcfeResult.valuePerShare, weight: weights.fcfe },
      { method: fcffResult.method, value: fcffResult.valuePerShare, weight: weights.fcff },
      { method: ddmResult.method, value: ddmResult.valuePerShare, weight: weights.ddm },
      { method: relativeResults.peValuation.method, value: relativeResults.peValuation.valuePerShare, weight: weights.peRelative },
      { method: relativeResults.evEbitdaValuation.method, value: relativeResults.evEbitdaValuation.valuePerShare, weight: weights.evEbitda },
      { method: assetResults.bookValue.method, value: assetResults.bookValue.valuePerShare, weight: weights.bookValue },
      { method: earningsResults.capitalizedEarnings.method, value: earningsResults.capitalizedEarnings.valuePerShare, weight: weights.capitalizedEarnings }
    ];

    // Calculate weighted average intrinsic value
    const weightedIntrinsicValue = valuations.reduce((sum, val) => sum + (val.value * val.weight), 0);
    const currentPrice = this.data.marketData.currentPrice;
    const upside = (weightedIntrinsicValue / currentPrice - 1) * 100;
    
    // Risk assessment
    const marginOfSafety = Math.max(0, (weightedIntrinsicValue - currentPrice) / weightedIntrinsicValue * 100);
    const recommendation = this.getRecommendation(upside, marginOfSafety);

    return {
      ticker: this.data.ticker,
      companyName: this.data.companyName,
      currentPrice,
      intrinsicValue: weightedIntrinsicValue,
      upside: upside,
      marginOfSafety,
      recommendation,
      confidence: this.calculateConfidence(valuations),
      valuationBreakdown: {
        fcfe: fcfeResult,
        fcff: fcffResult,
        ddm: ddmResult,
        relative: relativeResults,
        assetBased: assetResults,
        earningsBased: earningsResults
      },
      weightedValuations: valuations,
      weightingRationale: this.getWeightingRationale(weights),
      riskMetrics: this.calculateRiskMetrics(),
      dividendAnalysis: this.calculateDividendAnalysis(),
      summary: this.generateSummary(weightedIntrinsicValue, upside, marginOfSafety, recommendation)
    };
  }

  calculateConfidence(valuations) {
    const values = valuations.map(v => v.value);
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    const coefficientOfVariation = stdDev / mean;
    
    // Lower CV = higher confidence
    if (coefficientOfVariation < 0.2) return 'High';
    if (coefficientOfVariation < 0.4) return 'Medium';
    return 'Low';
  }

  calculateRiskMetrics() {
    const ratios = this.data.keyRatios;
    return {
      financial: {
        debtToEquity: ratios.leverageRatios.debtToEquity,
        currentRatio: ratios.liquidityRatios.currentRatio,
        interestCoverage: ratios.leverageRatios.interestCoverage,
        riskLevel: this.assessFinancialRisk(ratios)
      },
      business: {
        beta: this.data.marketData.beta,
        volatilityRisk: this.data.marketData.beta > 1.5 ? 'High' : this.data.marketData.beta > 1 ? 'Medium' : 'Low',
        industryRisk: 'Medium' // Cyclical industry
      },
      valuation: {
        peRatio: ratios.valuationRatios.peRatio,
        pbRatio: ratios.valuationRatios.pbRatio,
        valuationRisk: ratios.valuationRatios.peRatio > 25 ? 'High' : 'Medium'
      }
    };
  }

  assessFinancialRisk(ratios) {
    let score = 0;
    if (ratios.leverageRatios.debtToEquity > 3) score += 2;
    else if (ratios.leverageRatios.debtToEquity > 2) score += 1;
    
    if (ratios.liquidityRatios.currentRatio < 1) score += 2;
    else if (ratios.liquidityRatios.currentRatio < 1.2) score += 1;
    
    if (ratios.leverageRatios.interestCoverage < 5) score += 2;
    else if (ratios.leverageRatios.interestCoverage < 10) score += 1;
    
    if (score >= 4) return 'High';
    if (score >= 2) return 'Medium';
    return 'Low';
  }

  getRecommendation(upside, marginOfSafety) {
    if (upside > 20 && marginOfSafety > 15) return 'Strong Buy';
    if (upside > 10 && marginOfSafety > 10) return 'Buy';
    if (upside > 0 && marginOfSafety > 5) return 'Hold';
    if (upside > -10) return 'Hold';
    return 'Sell';
  }

  generateSummary(intrinsicValue, upside, marginOfSafety, recommendation) {
    return {
      valuation: `Based on comprehensive analysis using multiple valuation methods, ${this.data.companyName} has an estimated intrinsic value of $${intrinsicValue.toFixed(2)} per share.`,
      opportunity: upside > 0 ? 
        `The stock appears ${upside > 20 ? 'significantly ' : ''}undervalued with ${upside.toFixed(1)}% potential upside.` :
        `The stock appears overvalued with ${Math.abs(upside).toFixed(1)}% potential downside.`,
      risk: `Margin of safety: ${marginOfSafety.toFixed(1)}%. ${marginOfSafety > 15 ? 'Excellent' : marginOfSafety > 10 ? 'Good' : marginOfSafety > 5 ? 'Adequate' : 'Poor'} downside protection.`,
      recommendation: `Investment recommendation: ${recommendation}`
    };
  }

  getWeightingRationale(weights) {
    const rationale = [];
    const industry = this.data.industry;
    const marketCap = this.data.marketData.marketCap;
    const debtToEquity = this.data.keyRatios.leverageRatios.debtToEquity;
    const beta = this.data.marketData.beta;

    if (industry.includes("Heavy Construction") || industry.includes("Farm") || industry.includes("Machinery")) {
      rationale.push("Cyclical industrial company: Increased weight on relative and asset-based methods");
    }
    
    if (marketCap > 100000000000) {
      rationale.push("Large-cap mature company: Enhanced weight on earnings stability methods");
    }
    
    if (debtToEquity > 2) {
      rationale.push("High debt levels: FCFF weighted higher than FCFE");
    }
    
    if (beta > 1.3) {
      rationale.push("High-beta cyclical: Reduced growth-dependent DCF weights");
    }

    if (weights.fcfe === 0) {
      rationale.push("FCFE excluded due to extreme valuation result");
    }

    return rationale;
  }
}

module.exports = ValuationCalculator;

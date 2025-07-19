const ValuationCalculator = require('../src/ValuationCalculator');

describe('ValuationCalculator', () => {
  let calculator;
  let mockData;

  beforeEach(() => {
    mockData = {
      ticker: 'TEST',
      companyName: 'Test Company',
      marketData: {
        currentPrice: 100,
        marketCap: 10000000000,
        sharesOutstanding: 100000000,
        beta: 1.2
      },
      riskFactors: {
        riskFreeRate: 0.03,
        marketRiskPremium: 0.06,
        specificRiskPremium: 0.01
      },
      financialHistory: {
        '2024': {
          revenue: 1000000000,
          netIncome: 100000000,
          freeCashFlow: 80000000,
          operatingCashFlow: 120000000,
          capex: 40000000,
          totalDebt: 500000000,
          cashAndEquivalents: 50000000,
          shareholdersEquity: 800000000,
          bookValuePerShare: 8,
          eps: 1,
          dividend: 0.5,
          totalAssets: 1500000000,
          operatingIncome: 150000000
        }
      },
      keyRatios: {
        valuationRatios: {
          peRatio: 20,
          pbRatio: 12.5,
          evToEbitda: 15
        },
        leverageRatios: {
          debtToEquity: 0.625,
          interestCoverage: 15
        },
        liquidityRatios: {
          currentRatio: 1.5
        }
      },
      assumptions: {
        terminalGrowthRate: 0.025,
        taxRate: 0.25,
        dividendGrowthRate: 0.05
      },
      growthMetrics: {
        fcfGrowth5Y: 0.08,
        revenueGrowth5Y: 0.06
      },
      industryBenchmarks: {
        averagePE: 18,
        averagePB: 3
      }
    };

    calculator = new ValuationCalculator(mockData);
  });

  describe('Cost of Equity Calculation', () => {
    test('should calculate cost of equity using CAPM', () => {
      const costOfEquity = calculator.calculateCostOfEquity();
      // Expected: 0.03 + 1.2 * 0.06 + 0.01 = 0.112 (11.2%)
      expect(costOfEquity).toBeCloseTo(0.112, 3);
    });
  });

  describe('FCFE Valuation', () => {
    test('should calculate FCFE valuation', () => {
      const result = calculator.calculateFCFE();
      
      expect(result).toHaveProperty('method', 'FCFE');
      expect(result).toHaveProperty('valuePerShare');
      expect(result).toHaveProperty('upside');
      expect(result.valuePerShare).toBeGreaterThan(0);
      expect(typeof result.upside).toBe('number');
    });
  });

  describe('FCFF Valuation', () => {
    test('should calculate FCFF valuation', () => {
      const result = calculator.calculateFCFF();
      
      expect(result).toHaveProperty('method', 'FCFF');
      expect(result).toHaveProperty('valuePerShare');
      expect(result).toHaveProperty('firmValue');
      expect(result).toHaveProperty('equityValue');
      expect(result.valuePerShare).toBeGreaterThan(0);
    });
  });

  describe('DDM Valuation', () => {
    test('should calculate dividend discount model value', () => {
      const result = calculator.calculateDDM();
      
      expect(result).toHaveProperty('method', 'DDM (Gordon Growth)');
      expect(result).toHaveProperty('valuePerShare');
      expect(result.valuePerShare).toBeGreaterThan(0);
    });
  });

  describe('Relative Valuation', () => {
    test('should calculate relative valuation metrics', () => {
      const result = calculator.calculateRelativeValuation();
      
      expect(result).toHaveProperty('peValuation');
      expect(result).toHaveProperty('pbValuation');
      expect(result).toHaveProperty('evEbitdaValuation');
      
      expect(result.peValuation.valuePerShare).toBeGreaterThan(0);
      expect(result.pbValuation.valuePerShare).toBeGreaterThan(0);
    });
  });

  describe('Comprehensive Intrinsic Value', () => {
    test('should calculate comprehensive intrinsic value', () => {
      const result = calculator.calculateIntrinsicValue();
      
      expect(result).toHaveProperty('ticker', 'TEST');
      expect(result).toHaveProperty('intrinsicValue');
      expect(result).toHaveProperty('upside');
      expect(result).toHaveProperty('recommendation');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('valuationBreakdown');
      
      expect(result.intrinsicValue).toBeGreaterThan(0);
      expect(['Strong Buy', 'Buy', 'Hold', 'Sell']).toContain(result.recommendation);
      expect(['High', 'Medium', 'Low']).toContain(result.confidence);
    });
  });

  describe('Risk Assessment', () => {
    test('should assess financial risk correctly', () => {
      const riskMetrics = calculator.calculateRiskMetrics();
      
      expect(riskMetrics).toHaveProperty('financial');
      expect(riskMetrics).toHaveProperty('business');
      expect(riskMetrics).toHaveProperty('valuation');
      
      expect(['High', 'Medium', 'Low']).toContain(riskMetrics.financial.riskLevel);
      expect(['High', 'Medium', 'Low']).toContain(riskMetrics.business.volatilityRisk);
    });
  });

  describe('WACC Calculation', () => {
    test('should calculate WACC correctly', () => {
      const wacc = calculator.calculateWACC();
      
      expect(wacc).toBeGreaterThan(0);
      expect(wacc).toBeLessThan(1); // Should be less than 100%
    });
  });

  describe('CAGR Calculation', () => {
    test('should calculate CAGR correctly', () => {
      const values = [100, 110, 121, 133.1];
      const cagr = calculator.calculateCAGR(values);
      
      expect(cagr).toBeCloseTo(0.1, 2); // ~10% CAGR
    });

    test('should handle single value', () => {
      const values = [100];
      const cagr = calculator.calculateCAGR(values);
      
      expect(cagr).toBe(0);
    });
  });
});

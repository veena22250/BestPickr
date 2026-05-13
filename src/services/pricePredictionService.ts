export interface PricePrediction {
  currentPrice: number;
  predictedPrice: number;
  priceChange: number;
  priceChangePercent: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  confidence: number;
  recommendation: string;
  nextBestTime: string;
  factors: string[];
}

export const predictPrice = async (product: any): Promise<PricePrediction> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const currentPrice = product.cost_inr || product.price || 1000;
  const basePrice = product.original_price || currentPrice;
  const discount = product.discount || 0;
  
  // Generate realistic price prediction based on product data
  const priceVolatility = Math.random() * 0.3; // 0-30% volatility
  const trendDirection = Math.random();
  const daysAhead = Math.floor(Math.random() * 30) + 7; // 7-37 days
  
  let predictedPrice: number;
  let trend: 'increasing' | 'decreasing' | 'stable';
  let recommendation: string;
  let nextBestTime: string;
  
  if (trendDirection < 0.4) {
    // Decreasing trend (40% chance)
    const decreasePercent = (Math.random() * 0.15) + 0.05; // 5-20% decrease
    predictedPrice = currentPrice * (1 - decreasePercent);
    trend = 'decreasing';
    recommendation = 'Wait for better deals. Price expected to drop further.';
    nextBestTime = `in ${daysAhead} days`;
  } else if (trendDirection < 0.7) {
    // Stable trend (30% chance)
    predictedPrice = currentPrice * (1 + (Math.random() - 0.5) * 0.1); // ±5% variation
    trend = 'stable';
    recommendation = 'Good time to buy. Price is stable and unlikely to change significantly.';
    nextBestTime = 'now';
  } else {
    // Increasing trend (30% chance)
    const increasePercent = (Math.random() * 0.2) + 0.05; // 5-25% increase
    predictedPrice = currentPrice * (1 + increasePercent);
    trend = 'increasing';
    recommendation = 'Buy now before price increases. Limited time offer available.';
    nextBestTime = 'immediately';
  }
  
  const priceChange = predictedPrice - currentPrice;
  const priceChangePercent = (priceChange / currentPrice) * 100;
  const confidence = 70 + (Math.random() * 25); // 70-95% confidence
  
  const factors = [
    'Seasonal demand patterns',
    'Competitor pricing analysis',
    'Historical price trends',
    'Supply chain factors',
    'Market demand fluctuations'
  ];
  
  return {
    currentPrice,
    predictedPrice: Math.round(predictedPrice),
    priceChange: Math.round(priceChange),
    priceChangePercent: Math.round(priceChangePercent * 100) / 100,
    trend,
    confidence: Math.round(confidence),
    recommendation,
    nextBestTime,
    factors
  };
}; 
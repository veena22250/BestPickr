export interface SentimentAnalysis {
  overallSentiment: 'positive' | 'neutral' | 'negative';
  overallScore: number;
  summary: string;
  pros: string[];
  cons: string[];
  bestFor: string;
  alternatives: Array<{ name: string; reason: string }>;
  healthConcerns?: string[];
  detailedAnalysis: string;
}

export const analyzeSentiment = async (product: any): Promise<SentimentAnalysis> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  const rating = product.rating || 4.0 + (Math.random() * 1.0);
  const price = product.cost_inr || product.price || 1000;
  const discount = product.discount || 0;
  const reviews = product.reviews || Math.floor(Math.random() * 1000) + 50;
  
  // Determine overall sentiment based on multiple factors
  let overallScore = 0;
  let factors = 0;
  
  // Price factor (30% weight)
  const priceScore = discount > 20 ? 90 : discount > 10 ? 75 : 60;
  overallScore += priceScore * 0.3;
  factors += 0.3;
  
  // Rating factor (40% weight)
  const ratingScore = (rating / 5) * 100;
  overallScore += ratingScore * 0.4;
  factors += 0.4;
  
  // Reviews factor (20% weight)
  const reviewScore = reviews > 500 ? 90 : reviews > 100 ? 75 : 60;
  overallScore += reviewScore * 0.2;
  factors += 0.2;
  
  // Availability factor (10% weight)
  const availabilityScore = product.in_stock ? 95 : 30;
  overallScore += availabilityScore * 0.1;
  factors += 0.1;
  
  const finalScore = Math.round(overallScore / factors);
  
  let overallSentiment: 'positive' | 'neutral' | 'negative';
  if (finalScore >= 75) {
    overallSentiment = 'positive';
  } else if (finalScore >= 50) {
    overallSentiment = 'neutral';
  } else {
    overallSentiment = 'negative';
  }
  
  // Generate pros and cons
  const pros: string[] = [];
  const cons: string[] = [];
  
  if (discount > 15) {
    pros.push(`Great discount of ${discount}% off`);
  }
  if (rating >= 4.5) {
    pros.push('Excellent customer ratings');
  } else if (rating >= 4.0) {
    pros.push('Good customer feedback');
  }
  if (reviews > 500) {
    pros.push('Well-reviewed by many customers');
  }
  if (product.in_stock) {
    pros.push('Available for immediate purchase');
  }
  
  if (discount < 10) {
    cons.push('Limited discount available');
  }
  if (rating < 3.5) {
    cons.push('Mixed customer reviews');
  }
  if (reviews < 100) {
    cons.push('Limited customer feedback');
  }
  if (!product.in_stock) {
    cons.push('Currently out of stock');
  }
  
  // Generate detailed analysis
  const detailedAnalysis = `${product.product_name || 'This product'} shows ${overallSentiment} sentiment with a score of ${finalScore}/100. `;
  const analysisDetails = overallSentiment === 'positive' 
    ? 'The product offers good value with competitive pricing and positive customer feedback. It\'s recommended for most users looking for this type of product.'
    : overallSentiment === 'neutral'
    ? 'The product has average ratings and pricing. Consider comparing with alternatives before making a purchase decision.'
    : 'The product has some concerns with pricing or customer satisfaction. We recommend exploring alternatives or waiting for better deals.';
  
  // Generate best for section
  const bestFor = overallSentiment === 'positive'
    ? 'Shoppers looking for a reliable product with good value and positive reviews'
    : overallSentiment === 'neutral'
    ? 'Budget-conscious buyers who want to compare options before deciding'
    : 'Users who need this specific product and are willing to compromise on price or quality';
  
  // Generate alternatives
  const alternatives = [
    {
      name: 'Similar Products',
      reason: 'Compare with similar items for better value or features'
    },
    {
      name: 'Wait for Deals',
      reason: 'Monitor for better discounts or promotions'
    }
  ];
  
  // Add health concerns for certain product categories
  const healthConcerns: string[] = [];
  const productName = (product.product_name || '').toLowerCase();
  if (productName.includes('supplement') || productName.includes('vitamin')) {
    healthConcerns.push('Consult healthcare provider before use');
    healthConcerns.push('Check for potential drug interactions');
  }
  if (productName.includes('skincare') || productName.includes('cosmetic')) {
    healthConcerns.push('Patch test recommended for sensitive skin');
    healthConcerns.push('Check ingredient list for allergies');
  }
  
  return {
    overallSentiment,
    overallScore: finalScore,
    summary: detailedAnalysis + analysisDetails,
    pros,
    cons,
    bestFor,
    alternatives,
    healthConcerns: healthConcerns.length > 0 ? healthConcerns : undefined,
    detailedAnalysis: detailedAnalysis + analysisDetails
  };
}; 
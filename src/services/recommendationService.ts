export interface ProductRecommendation {
  id: string;
  name: string;
  price: number;
  rating: number;
  image?: string;
  reason: string;
  url?: string;
}

export const getRelatedProducts = async (product: any, isDelivery: boolean = false): Promise<ProductRecommendation[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  if (isDelivery) {
    // For delivery services, recommend alternative delivery options
    const deliveryServices = [
      {
        id: 'swiggy',
        name: 'Swiggy Instamart',
        price: 40,
        rating: 4.2,
        reason: 'Fast grocery delivery',
        url: 'https://www.swiggy.com/instamart'
      },
      {
        id: 'blinkit',
        name: 'Blinkit',
        price: 35,
        rating: 4.1,
        reason: '10-minute grocery delivery',
        url: 'https://blinkit.com'
      },
      {
        id: 'zepto',
        name: 'Zepto',
        price: 30,
        rating: 4.3,
        reason: 'Ultra-fast delivery',
        url: 'https://zepto.in'
      },
      {
        id: 'bigbasket',
        name: 'BigBasket',
        price: 50,
        rating: 4.0,
        reason: 'Wide product selection',
        url: 'https://www.bigbasket.com'
      }
    ];
    
    return deliveryServices.slice(0, 3);
  } else {
    // For e-commerce products, recommend similar products
    const basePrice = product.cost_inr || 1000;
    const category = product.category || 'electronics';
    
    const similarProducts = [
      {
        id: 'similar1',
        name: `Similar ${product.product_name || 'Product'} - Premium`,
        price: Math.round(basePrice * 1.2),
        rating: 4.5,
        reason: 'Higher quality alternative',
        url: `https://www.amazon.in/s?k=${encodeURIComponent(product.product_name || 'product')}`
      },
      {
        id: 'similar2',
        name: `Similar ${product.product_name || 'Product'} - Budget`,
        price: Math.round(basePrice * 0.8),
        rating: 3.8,
        reason: 'More affordable option',
        url: `https://www.flipkart.com/search?q=${encodeURIComponent(product.product_name || 'product')}`
      },
      {
        id: 'similar3',
        name: `Similar ${product.product_name || 'Product'} - Best Value`,
        price: Math.round(basePrice * 0.9),
        rating: 4.2,
        reason: 'Best price-performance ratio',
        url: `https://www.myntra.com/search?q=${encodeURIComponent(product.product_name || 'product')}`
      }
    ];
    
    return similarProducts;
  }
};

export const getBuyingRecommendation = (product: any, pricePrediction?: any): string => {
  const currentPrice = product.cost_inr || product.price || 1000;
  const discount = product.discount || 0;
  const rating = product.rating || 4.0;
  
  if (pricePrediction) {
    if (pricePrediction.trend === 'decreasing') {
      return `Wait ${pricePrediction.nextBestTime} - Price expected to drop by ₹${Math.abs(pricePrediction.priceChange)}`;
    } else if (pricePrediction.trend === 'increasing') {
      return `Buy now - Price expected to increase by ₹${pricePrediction.priceChange}`;
    } else {
      return 'Good time to buy - Price is stable';
    }
  }
  
  // Fallback recommendation based on product data
  if (discount > 25) {
    return 'Excellent deal - Buy now before discount ends';
  } else if (discount > 15) {
    return 'Good discount available - Consider buying';
  } else if (rating >= 4.5) {
    return 'Highly rated product - Good choice';
  } else {
    return 'Compare with alternatives before buying';
  }
}; 
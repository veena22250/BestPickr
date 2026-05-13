import React, { useEffect, useState, useCallback } from 'react';
import { X, Loader2, TrendingUp, TrendingDown, Minus, Star, Clock, AlertTriangle } from 'lucide-react';
import { predictPrice, PricePrediction } from '../services/pricePredictionService';
import { analyzeSentiment, SentimentAnalysis } from '../services/sentimentService';
import { getRelatedProducts, getBuyingRecommendation, ProductRecommendation } from '../services/recommendationService';
import { NotifyButton } from './NotifyButton';


interface ProductAnalysisSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  product: any;
  isDelivery?: boolean;
}

const ProductAnalysisSidebar: React.FC<ProductAnalysisSidebarProps> = ({
  isOpen,
  onClose,
  product,
  isDelivery = false,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pricePrediction, setPricePrediction] = useState<PricePrediction | null>(null);
  const [sentimentAnalysis, setSentimentAnalysis] = useState<SentimentAnalysis | null>(null);
  const [relatedProducts, setRelatedProducts] = useState<ProductRecommendation[]>([]);
  const [buyingRecommendation, setBuyingRecommendation] = useState<string>('');

  const getSentimentColor = (sentiment: 'positive' | 'neutral' | 'negative') => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-400';
      case 'negative':
        return 'text-red-400';
      case 'neutral':
      default:
        return 'text-yellow-400';
    }
  };

  const getSentimentBgColor = (sentiment: 'positive' | 'neutral' | 'negative') => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-500';
      case 'negative':
        return 'bg-red-500';
      case 'neutral':
      default:
        return 'bg-yellow-500';
    }
  };

  const getTrendIcon = (trend: 'increasing' | 'decreasing' | 'stable') => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="h-4 w-4 text-red-400" />;
      case 'decreasing':
        return <TrendingDown className="h-4 w-4 text-green-400" />;
      case 'stable':
        return <Minus className="h-4 w-4 text-yellow-400" />;
    }
  };

  const fetchAnalysis = useCallback(async () => {
    if (!product) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch all analysis data in parallel
      const [priceData, sentimentData, relatedData] = await Promise.all([
        predictPrice(product),
        analyzeSentiment(product),
        getRelatedProducts(product, isDelivery)
      ]);
      
      setPricePrediction(priceData);
      setSentimentAnalysis(sentimentData);
      setRelatedProducts(relatedData);
      setBuyingRecommendation(getBuyingRecommendation(product, priceData));
    } catch (err) {
      console.error('Error fetching analysis:', err);
      setError('Failed to analyze the product. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  }, [product, isDelivery]);

  useEffect(() => {
    if (isOpen && product) {
      fetchAnalysis();
    }
  }, [isOpen, product, fetchAnalysis]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
          <div className="pointer-events-auto w-screen max-w-md">
            <div className="flex h-full flex-col overflow-y-scroll bg-gray-800 shadow-xl">
              <div className="px-4 py-6 sm:px-6 bg-gray-900">
                <div className="flex items-start justify-between">
                  <h2 className="text-lg font-medium text-white">
                    {isLoading ? 'Analyzing...' : 'Product Analysis'}
                  </h2>
                  <div className="ml-3 flex h-7 items-center">
                    <button
                      type="button"
                      className="rounded-md bg-gray-900 text-gray-400 hover:text-gray-500 focus:outline-none"
                      onClick={onClose}
                    >
                      <span className="sr-only">Close panel</span>
                      <X className="h-6 w-6" aria-hidden="true" />
                    </button>
                  </div>
                </div>
              </div>
              
              {isLoading ? (
                <div className="flex flex-1 flex-col items-center justify-center p-6">
                  <Loader2 className="h-12 w-12 animate-spin text-blue-500" />
                  <p className="mt-4 text-gray-300">Analyzing product data...</p>
                </div>
              ) : error ? (
                <div className="flex flex-1 flex-col items-center justify-center p-6 text-red-400">
                  <p className="text-center">{error}</p>
                  <button
                    onClick={fetchAnalysis}
                    className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                  >
                    Retry Analysis
                  </button>
                </div>
              ) : (
                <div className="flex-1 overflow-y-auto p-6">
                  {/* Price Prediction Section */}
                  {pricePrediction && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-white mb-4">Price Prediction</h3>
                      <div className="bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            {getTrendIcon(pricePrediction.trend)}
                            <span className="text-white font-medium">
                              {pricePrediction.trend.charAt(0).toUpperCase() + pricePrediction.trend.slice(1)} Trend
                            </span>
                          </div>
                          <span className={`text-sm font-medium ${
                            pricePrediction.trend === 'decreasing' ? 'text-green-400' : 
                            pricePrediction.trend === 'increasing' ? 'text-red-400' : 'text-yellow-400'
                          }`}>
                            {pricePrediction.confidence}% confidence
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 mb-3">
                          <div>
                            <p className="text-sm text-gray-400">Current Price</p>
                            <p className="text-white font-medium">₹{pricePrediction.currentPrice.toLocaleString()}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-400">Predicted Price</p>
                            <p className="text-white font-medium">₹{pricePrediction.predictedPrice.toLocaleString()}</p>
                          </div>
                        </div>
                        
                        <div className="mb-3">
                          <p className="text-sm text-gray-400">Expected Change</p>
                          <p className={`font-medium ${
                            pricePrediction.priceChange >= 0 ? 'text-red-400' : 'text-green-400'
                          }`}>
                            {pricePrediction.priceChange >= 0 ? '+' : ''}₹{pricePrediction.priceChange} 
                            ({pricePrediction.priceChangePercent >= 0 ? '+' : ''}{pricePrediction.priceChangePercent}%)
                          </p>
                        </div>
                        
                        <div className="bg-blue-900 bg-opacity-30 rounded p-3">
                          <div className="flex items-start space-x-2">
                            <Clock className="h-4 w-4 text-blue-400 mt-0.5" />
                            <div>
                              <p className="text-sm text-blue-300 font-medium">Recommendation</p>
                              <p className="text-sm text-gray-300">{pricePrediction.recommendation}</p>
                            </div>
                          </div>
                        </div>

                            <NotifyButton
                              productId={product.model_number}
                              productName={product.product_name}
                            />
                      </div>
                    </div>
                  )}

                  {/* Sentiment Analysis Section */}
                  {sentimentAnalysis && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-white mb-4">Sentiment Analysis</h3>
                      <div className="bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <span className={`text-sm font-medium ${getSentimentColor(sentimentAnalysis.overallSentiment)}`}>
                            {sentimentAnalysis.overallSentiment.charAt(0).toUpperCase() + sentimentAnalysis.overallSentiment.slice(1)} Sentiment
                          </span>
                          <span className="text-white font-medium">
                            Score: {sentimentAnalysis.overallScore}/100
                          </span>
                        </div>
                        
                        <div className="mb-4">
                          <div className="h-2 w-full bg-gray-600 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${getSentimentBgColor(sentimentAnalysis.overallSentiment)}`}
                              style={{ width: `${sentimentAnalysis.overallScore}%` }}
                            />
                          </div>
                        </div>
                        
                        <p className="text-sm text-gray-300 mb-4">{sentimentAnalysis.detailedAnalysis}</p>
                        
                        {/* Pros & Cons */}
                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                          {sentimentAnalysis.pros.length > 0 && (
                            <div>
                              <h4 className="font-medium text-green-400 mb-2">Pros</h4>
                              <ul className="text-sm text-gray-300 space-y-1">
                                {sentimentAnalysis.pros.map((pro, index) => (
                                  <li key={index} className="flex items-start">
                                    <span className="text-green-400 mr-2">•</span>
                                    {pro}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {sentimentAnalysis.cons.length > 0 && (
                            <div>
                              <h4 className="font-medium text-red-400 mb-2">Cons</h4>
                              <ul className="text-sm text-gray-300 space-y-1">
                                {sentimentAnalysis.cons.map((con, index) => (
                                  <li key={index} className="flex items-start">
                                    <span className="text-red-400 mr-2">•</span>
                                    {con}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                        
                        {/* Health Concerns */}
                        {sentimentAnalysis.healthConcerns && sentimentAnalysis.healthConcerns.length > 0 && (
                          <div className="mt-4 bg-yellow-900 bg-opacity-30 rounded p-3">
                            <div className="flex items-start space-x-2">
                              <AlertTriangle className="h-4 w-4 text-yellow-400 mt-0.5" />
                              <div>
                                <p className="text-sm text-yellow-300 font-medium">Health Considerations</p>
                                <ul className="text-sm text-gray-300 mt-1 space-y-1">
                                  {sentimentAnalysis.healthConcerns.map((concern, index) => (
                                    <li key={index} className="flex items-start">
                                      <span className="text-yellow-400 mr-2">•</span>
                                      {concern}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Best For Section */}
                  {sentimentAnalysis?.bestFor && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-white mb-4">Best For</h3>
                      <div className="bg-blue-900 bg-opacity-30 rounded-lg p-4">
                        <p className="text-sm text-gray-300">{sentimentAnalysis.bestFor}</p>
                      </div>
                    </div>
                  )}

                  {/* Buying Recommendation */}
                  {buyingRecommendation && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-white mb-4">Buying Recommendation</h3>
                      <div className="bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center space-x-2">
                          <Star className="h-4 w-4 text-yellow-400" />
                          <p className="text-sm text-gray-300">{buyingRecommendation}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Related Products */}
                  {relatedProducts.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-white mb-4">People Also Bought</h3>
                      <div className="space-y-3">
                        {relatedProducts.map((relatedProduct) => (
                          <div key={relatedProduct.id} className="bg-gray-700 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-medium text-white text-sm">{relatedProduct.name}</h4>
                              <span className="text-sm text-gray-400">₹{relatedProduct.price}</span>
                            </div>
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center space-x-1">
                                <Star className="h-3 w-3 text-yellow-400 fill-current" />
                                <span className="text-sm text-gray-300">{relatedProduct.rating}</span>
                              </div>
                              <span className="text-xs text-gray-400">{relatedProduct.reason}</span>
                            </div>
                            {relatedProduct.url && (
                              <a
                                href={relatedProduct.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-block bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1 rounded transition-colors"
                              >
                                View Product
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Alternatives */}
                  {sentimentAnalysis?.alternatives && sentimentAnalysis.alternatives.length > 0 && (
                    <div>
                      <h3 className="text-lg font-medium text-white mb-4">Alternatives</h3>
                      <div className="space-y-3">
                        {sentimentAnalysis.alternatives.map((alt, i) => (
                          <div key={i} className="bg-gray-700 rounded-lg p-4">
                            <h4 className="font-medium text-white text-sm">{alt.name}</h4>
                            <p className="text-sm text-gray-300 mt-1">{alt.reason}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductAnalysisSidebar;

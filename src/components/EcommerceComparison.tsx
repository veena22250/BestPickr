import React, { useState, useRef, useCallback, useMemo } from 'react';
import { Search, ShoppingBag, Sparkles,Check,X,ShoppingCart } from 'lucide-react';
import ProductAnalysisSidebar from './ProductAnalysisSidebar';
import ecommerceDataRaw from '../data/ecomdata.json';
import { Product } from '../types/product';
import VoiceInputButton from './VoiceInputButton';
import {
  ResponsiveContainer,
  BarChart,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar,
  CartesianGrid,
} from 'recharts';

import { getPlatformLogo } from './_PlatformLogos';

// Brand logo mapping for common brands
const brandLogoMap: { [key: string]: string } = {
  'nike': 'https://upload.wikimedia.org/wikipedia/commons/a/a6/Nike_Logo.svg',
  'adidas': 'https://upload.wikimedia.org/wikipedia/commons/2/20/Adidas_Logo.svg',
  'puma': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Puma_logo.svg',
  'reebok': 'https://upload.wikimedia.org/wikipedia/commons/0/0b/Reebok_logo.svg',
  'under armour': 'https://upload.wikimedia.org/wikipedia/commons/7/72/Under_armour_logo.svg',
  'new balance': 'https://upload.wikimedia.org/wikipedia/commons/1/1a/New_Balance_logo.svg',
  'converse': 'https://upload.wikimedia.org/wikipedia/commons/3/3c/Converse_logo.svg',
  'vans': 'https://upload.wikimedia.org/wikipedia/commons/0/00/Vans_logo.svg',
  'skechers': 'https://upload.wikimedia.org/wikipedia/commons/2/2a/Skechers_logo.svg',
  'asics': 'https://upload.wikimedia.org/wikipedia/commons/2/24/ASICS_logo.svg',
  'brooks': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Brooks_logo.svg',
  'saucony': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Saucony_logo.svg',
  'mizuno': 'https://upload.wikimedia.org/wikipedia/commons/9/9a/Mizuno_logo.svg',
  'wilson': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Wilson_logo.svg',
  'head': 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Head_logo.svg',
  'babolat': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Babolat_logo.svg',
  'yonex': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Yonex_logo.svg',
  'prince': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Prince_logo.svg',
  'dunlop': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Dunlop_logo.svg',
  'volkl': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Volkl_logo.svg',
};

// Function to get brand logo URL
const getBrandLogo = (brandName: string): string | null => {
  const normalizedBrand = brandName.toLowerCase().trim();
  return brandLogoMap[normalizedBrand] || null;
};

// Platform links for e-commerce redirection
const platformLinks: { [key: string]: string } = {
  'amazon': 'https://www.amazon.in/s?k=',
  'flipkart': 'https://www.flipkart.com/search?q=',
  'myntra': 'https://www.myntra.com/search?q=',
  'ajio': 'https://www.ajio.com/search/?query=',
  'meesho': 'https://www.meesho.com/search?q=',
  'snapdeal': 'https://www.snapdeal.com/search?keyword=',
  'paytmmall': 'https://paytmmall.com/search?q=',
  'jiomart': 'https://www.jiomart.com/search/',
  'bigbasket': 'https://www.bigbasket.com/search/?q=',
  'grofers': 'https://grofers.com/search?q=',
  'swiggy': 'https://www.swiggy.com/instamart/search?query=',
  'zomato': 'https://www.zomato.com/order-food-online?q=',
  'blinkit': 'https://blinkit.com/s/?q=',
  'zepto': 'https://www.zeptonow.com/search?query=',
  'dunzo': 'https://www.dunzo.com/search?q=',
  'more': 'https://www.more.retail/search?q=',
  'ola': 'https://www.olacabs.com/',
  'uber': 'https://www.uber.com/in/en/',
  'rapido': 'https://www.rapido.bike/',
  'nammayanthri': 'https://www.nammayathri.com/'
};

// Function to get platform search URL
const getPlatformSearchUrl = (platform: string, productName: string): string => {
  const normalizedPlatform = platform.toLowerCase().trim();
  const baseUrl = platformLinks[normalizedPlatform];
  if (baseUrl) {
    return baseUrl + encodeURIComponent(productName);
  }
  // Fallback to a generic search
  return `https://www.google.com/search?q=${encodeURIComponent(productName + ' ' + platform)}`;
};

// Define the structure of our raw data
interface RawProduct {
  product_name: string;
  platform: string;
  cost_inr: number;
  in_stock: boolean;
  description: string;
  brand_name: string;
  model_number: string;
  sizes_available?: string[];
  color_options?: string[];
  material: string;
  estimated_delivery: string;
  category: string;
  sub_category: string;
  image_url?: string;
  rating?: number;
  review_count?: number;
  discount?: number;
  original_price?: number;
  url: string;
}

// Convert raw product data to our Product type
const products: Product[] = (ecommerceDataRaw.products as unknown as RawProduct[]).map(item => ({
  ...item,
  in_stock: item.in_stock ?? true,
  sizes_available: item.sizes_available ?? [],
  color_options: item.color_options ?? [],
}));

interface GroupedProduct {
  productName: string;
  platforms: Product[];
}

function groupProductsByName(products: Product[]): GroupedProduct[] {
  const map = new Map<string, Product[]>();
  products.forEach((item) => {
    const key = item.product_name.toLowerCase();
    if (!map.has(key)) map.set(key, []);
    map.get(key)?.push(item);
  });
  return Array.from(map.entries()).map(([productName, platforms]) => ({
    productName,
    platforms,
  }));
}

const EcommerceComparison: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [selectedForAnalysis, setSelectedForAnalysis] = useState<Product | null>(null);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  // Per-cart search state (keyed by productName)
 const [cart, setCart] = useState<{item: RawProduct, quantity: number}[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [orderPlaced, setOrderPlaced] = useState(false);

  //const [cartSearches, setCartSearches] = useState<{ [key: string]: string }>({});

  const handleProductClick = useCallback((product: Product) => {
    setSelectedForAnalysis(product);
    setShowAnalysis(true);
  }, []);

  const closeAnalysis = useCallback(() => {
    setShowAnalysis(false);
    // Small delay to allow the sidebar to close before clearing the product
    setTimeout(() => setSelectedForAnalysis(null), 300);
  }, []);

  const uniqueProductNames = useMemo(() => 
    Array.from(new Set(products.map((p) => p.product_name))),
    []
  );


   // Add item to cart
  const addToCart = (product: RawProduct) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.item.product_name === product.product_name);
      if (existingItem) {
        return prevCart.map(item =>
          item.item.product_name === product.product_name
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prevCart, { item: product, quantity: 1 }];
    });
    setIsCartOpen(true);
  };


   // Remove item from cart
  const removeFromCart = (productName: string) => {
    setCart(prevCart => prevCart.filter(item => item.item.product_name !== productName));
  };

  // Update item quantity in cart
  const updateQuantity = (productName: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    setCart(prevCart =>
      prevCart.map(item =>
        item.item.product_name === productName ? { ...item, quantity: newQuantity } : item
      )
    );
  };

  // Calculate cart total
  const cartTotal = cart.reduce(
    (total, { item, quantity }) => total + item.cost_inr * quantity,
    0
  );

  // Place order
  const placeOrder = () => {
    setOrderPlaced(true);
    setTimeout(() => {
      setCart([]);
      setIsCartOpen(false);
      setOrderPlaced(false);
    }, 3000);
  };

  const filteredNames = useMemo(() => 
    searchQuery && showDropdown
      ? uniqueProductNames.filter((name) =>
          name.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : [],
    [searchQuery, showDropdown, uniqueProductNames]
  );

  const filteredProducts = useMemo(() => 
    searched && selectedProduct
      ? groupProductsByName(
          products.filter((item) =>
            item.product_name.toLowerCase().includes(selectedProduct.toLowerCase())
          )
        )
      : [],
    [searched, selectedProduct]
  );

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setSearched(false);
    setShowDropdown(true);
  }, []);

  const handleDropdownSelect = useCallback((name: string) => {
    setSearchQuery(name);
    setSelectedProduct(name);
    setSearched(false);
    setShowDropdown(false);
    inputRef.current?.focus();
  }, []);

  const handleSearch = useCallback((e?: React.FormEvent) => {
    e?.preventDefault();
    if (!searchQuery.trim()) return;
    
    setSelectedProduct(searchQuery);
    setShowDropdown(false);
    setLoading(true);
    
    // Simulate API call with timeout
    setTimeout(() => {
      setLoading(false);
      setSearched(true);
    }, 500);
  }, [searchQuery]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  }, [handleSearch]);

  // Prepare chart data
  type ChartDataPoint = { name: string; price: number };
  const chartData = useMemo<ChartDataPoint[]>(() => {
    if (!searched || filteredProducts.length === 0) return [];
    
    return filteredProducts.flatMap(group =>
      group.platforms.map(p => ({
        name: p.platform,
        price: p.cost_inr,
      }))
    );
  }, [searched, filteredProducts]);
  
  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">E-commerce Price Comparison</h1>
          <p className="text-gray-300">Compare prices across multiple platforms</p>
        </div>

        {/* Search Bar */}
        <div className="relative mb-8 max-w-2xl mx-auto">
          <form onSubmit={handleSearch} className="relative">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                ref={inputRef}
                type="text"
                className="block w-full pl-10 pr-16 py-3 border border-gray-600 rounded-lg bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Search for products..."
                value={searchQuery}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                onFocus={() => setShowDropdown(true)}
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-2">
                <VoiceInputButton
                  onResult={(text) => {
                    setSearchQuery(text);
                    handleSearch();
                  }}
                  onError={(error) => console.error('Voice input error:', error)}
                  size="sm"
                  className="mr-2"
                />
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <Search className="h-5 w-5" />
                </button>
              </div>
            </div>
          </form>

          {/* Search Suggestions Dropdown */}
          {showDropdown && filteredNames.length > 0 && (
            <div className="absolute z-10 mt-1 w-full bg-gray-800 border border-gray-700 rounded-md shadow-lg max-h-60 overflow-auto">
              {filteredNames.map((name) => (
                <div
                  key={name}
                  className="px-4 py-2 text-white hover:bg-gray-700 cursor-pointer"
                  onClick={() => handleDropdownSelect(name)}
                >
                  {name}
                </div>
              ))}
            </div>
          )}
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : searched && filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <ShoppingBag className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-lg font-medium text-white">No products found</h3>
            <p className="mt-1 text-gray-400">Try a different search term</p>
          </div>
        ) : (
          <>
            {searched && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-white mb-4">Price Comparison</h2>
                <div className="bg-gray-800 rounded-lg p-4 h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#4B5563" />
                      <XAxis dataKey="name" tick={{ fill: 'white' }} />
                      <YAxis tick={{ fill: 'white' }} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="price" fill="#8884d8" name="Price (INR)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Product Grid Display */}
            {searched && filteredProducts.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-white mb-4">Available Products</h2>
                <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 auto-rows-max">
                  {filteredProducts.flatMap(group => 
                    group.platforms.map((product, index) => (
                      <div 
                        key={`${product.platform}-${index}`}
                        className="bg-gray-800/50 backdrop-blur-md rounded-xl p-4 border border-gray-700/50 hover:border-lavender-400/50 transition-all group cursor-pointer hover:bg-gray-700/30"
                        onClick={() => handleProductClick(product)}
                      >
                        <div className="flex items-center space-x-3 mb-3">
                          <div className="h-20 w-20 flex items-center justify-center overflow-hidden">
                            {(() => {
                              // First try to get brand logo
                              const brandLogoSrc = getBrandLogo(product.brand_name);
                              if (brandLogoSrc) {
                                return (
                                  <img 
                                    src={brandLogoSrc} 
                                    alt={product.brand_name} 
                                    className="h-20 w-20 object-contain"
                                    onError={(e) => {
                                      // Fallback to platform logo if brand logo fails
                                      const target = e.target as HTMLImageElement;
                                      const platformLogoSrc = getPlatformLogo(product.platform);
                                      if (platformLogoSrc) {
                                        target.src = platformLogoSrc;
                                      } else {
                                        // Final fallback to brand name initial
                                        target.style.display = 'none';
                                        const parent = target.parentElement;
                                        if (parent) {
                                          parent.innerHTML = `<div class="h-20 w-20 flex items-center justify-center bg-gray-700 rounded-lg">
                                            <span class="text-lg font-medium text-white">${product.brand_name.charAt(0).toUpperCase()}</span>
                                          </div>`;
                                        }
                                      }
                                    }}
                                  />
                                );
                              }
                              
                              // If no brand logo, try platform logo
                              const platformLogoSrc = getPlatformLogo(product.platform);
                              if (platformLogoSrc) {
                                return (
                                  <img 
                                    src={platformLogoSrc} 
                                    alt={product.platform} 
                                    className="h-20 w-20 object-contain"
                                    onError={(e) => {
                                      // Fallback to brand name initial
                                      const target = e.target as HTMLImageElement;
                                      target.style.display = 'none';
                                      const parent = target.parentElement;
                                      if (parent) {
                                        parent.innerHTML = `<div class="h-20 w-20 flex items-center justify-center bg-gray-700 rounded-lg">
                                          <span class="text-lg font-medium text-white">${product.brand_name.charAt(0).toUpperCase()}</span>
                                        </div>`;
                                      }
                                    }}
                                  />
                                );
                              }
                              
                              // Final fallback to brand name initial
                              return (
                                <div className="h-20 w-20 flex items-center justify-center bg-gray-700 rounded-lg">
                                  <span className="text-lg font-medium text-white">{product.brand_name.charAt(0).toUpperCase()}</span>
                                </div>
                              );
                            })()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-medium text-white truncate">{product.product_name}</h3>
                            <p className="text-sm text-gray-400">{product.brand_name}</p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleProductClick(product);
                            }}
                            className="p-1.5 rounded-full bg-gray-700/50 text-gray-300 hover:bg-lavender-600 hover:text-white transition-colors opacity-0 group-hover:opacity-100"
                            title="AI Analysis"
                          >
                           
                          </button>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-lg font-bold text-white">₹{product.cost_inr}</span>
                            {product.rating && (
                              <div className="flex items-center text-yellow-400 text-sm">
                                <span>⭐ {product.rating}</span>
                              </div>
                            )}
                          </div>
                          
                          {product.discount && (
                            <div className="text-green-400 text-sm">
                              {product.discount}% OFF
                            </div>
                          )}
                          
                          <p className="text-sm text-gray-300 italic">{product.platform}</p>
                          
                          <div className="mt-3 space-y-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                addToCart(product);
                              }}
                              className="w-full px-4 py-2 bg-lavender-500 rounded text-white hover:bg-lavender-600 text-center"
                            >
                              Add to Cart
                            </button>
                            <a
                              href={getPlatformSearchUrl(product.platform, product.product_name)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center justify-center gap-1 text-sm text-white hover:text-lavender-300 transition-colors"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <span>View on {product.platform}</span>
                            </a>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}


          </>
        )}
      </div>

      {/* Cart Sidebar */}
      <div className={`fixed inset-y-0 right-0 w-full sm:w-96 bg-gray-800 shadow-xl transform ${isCartOpen ? 'translate-x-0' : 'translate-x-full'} transition-transform duration-300 ease-in-out z-50`}>
        <div className="h-full flex flex-col">
          <div className="p-4 border-b border-gray-700 flex justify-between items-center">
            <h2 className="text-xl font-semibold text-white">Your Cart</h2>
            <button 
              onClick={() => setIsCartOpen(false)}
              className="text-gray-400 hover:text-white"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          
          {cart.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
              <ShoppingCart className="h-16 w-16 text-gray-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-300 mb-2">Your cart is empty</h3>
              <p className="text-gray-500 mb-6">Add some items to get started</p>
              <button
                onClick={() => setIsCartOpen(false)}
                className="px-4 py-2 bg-lavender-500 text-white rounded-md hover:bg-lavender-600"
              >
                Continue Shopping
              </button>
            </div>
          ) : (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {cart.map(({ item, quantity }) => (
                  <div key={item.product_name} className="flex items-center p-3 bg-gray-700/50 rounded-lg">
                    <div className="h-12 w-12 rounded-full bg-gray-700 flex items-center justify-center mr-3">
                      <span className="text-lg font-medium text-white">{item.product_name.charAt(0)}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-white">{item.product_name}</h3>
                      <p className="text-sm text-gray-300">
                        {item.estimated_delivery}  • ₹{item.cost_inr}
                      </p>
                    </div>
                    <div className="flex items-center">
                      <button
                        onClick={() => updateQuantity(item.product_name, quantity - 1)}
                        className="px-2 py-1 bg-gray-600 rounded-l-md text-white hover:bg-gray-500"
                      >
                        -
                      </button>
                      <span className="px-3 py-1 bg-gray-700 text-white">
                        {quantity}
                      </span>
                      <button
                        onClick={() => updateQuantity(item.product_name, quantity + 1)}
                        className="px-2 py-1 bg-gray-600 rounded-r-md text-white hover:bg-gray-500"
                      >
                        +
                      </button>
                      <button
                        onClick={() => removeFromCart(item.product_name)}
                        className="ml-2 text-gray-400 hover:text-red-400"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="p-4 border-t border-gray-700">
                <div className="flex justify-between mb-4 text-lg font-medium">
                  <span>Total:</span>
                  <span>₹{cartTotal.toFixed(2)}</span>
                </div>
                <button
                  onClick={placeOrder}
                  disabled={orderPlaced}
                  className={`w-full py-3 px-4 rounded-md text-white font-medium ${
                    orderPlaced
                      ? 'bg-green-500 cursor-not-allowed'
                      : 'bg-lavender-500 hover:bg-lavender-600'
                  }`}
                >
                  {orderPlaced ? (
                    <span className="flex items-center justify-center">
                      <Check className="h-5 w-5 mr-2" />
                      Order Placed!
                    </span>
                  ) : (
                    'Proceed to Checkout'
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>


      {/* AI Analysis Sidebar */}
      <ProductAnalysisSidebar
        isOpen={showAnalysis && selectedForAnalysis !== null}
        onClose={closeAnalysis}
        product={selectedForAnalysis}
      />
    </div>
  );
};

export default EcommerceComparison;

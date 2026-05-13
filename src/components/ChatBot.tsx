import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, X, Mic, MicOff } from 'lucide-react';
import { generateChatbotResponse } from '../services/groqService';

// Import JSON data
import ecomData from '../data/ecomdata.json';
import quickDeliveryData from '../data/quickdelivery.json';
import rideData from '../data/ridedata.json';

interface Message {
  role: 'user' | 'model';
  parts: string;
}

const ChatBot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'model',
      parts: 'Hello! I\'m your BestPickr AI assistant. I can help you find products, compare prices, check delivery options, and compare ride services using our real data and AI-powered insights. What would you like to know?'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechRecognition, setSpeechRecognition] = useState<SpeechRecognition | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setIsListening(true);
      };
      
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };
      
      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      setSpeechRecognition(recognition);
    }
  }, []);

  // Handle voice input
  const handleVoiceInput = () => {
    if (!speechRecognition) {
      alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    
    if (isListening) {
      speechRecognition.stop();
    } else {
      speechRecognition.start();
    }
  };

  // Function to search through e-commerce data
  const searchEcomData = (query: string) => {
    const searchTerm = query.toLowerCase();
    const results = ecomData.products.filter(product => 
      product.product_name.toLowerCase().includes(searchTerm) ||
      product.brand_name.toLowerCase().includes(searchTerm) ||
      product.category.toLowerCase().includes(searchTerm) ||
      product.sub_category.toLowerCase().includes(searchTerm)
    );
    return results;
  };

  // Function to search through quick delivery data
  const searchDeliveryData = (query: string) => {
    const searchTerm = query.toLowerCase();
    const results: any[] = [];
    
    quickDeliveryData.platforms.forEach(platform => {
      platform.categories.forEach(category => {
        category.products.forEach(product => {
          if (product.product_name.toLowerCase().includes(searchTerm) ||
              category.category_name.toLowerCase().includes(searchTerm)) {
            results.push({
              ...product,
              platform: platform.platform_name,
              category: category.category_name
            });
          }
        });
      });
    });
    return results;
  };

  // Function to search through ride data
  const searchRideData = (query: string) => {
    const searchTerm = query.toLowerCase();
    const results = rideData.rides.filter(ride => 
      ride.pickup_location.toLowerCase().includes(searchTerm) ||
      ride.destination.toLowerCase().includes(searchTerm) ||
      ride.platform.toLowerCase().includes(searchTerm)
    );
    return results;
  };

  // Function to get platform statistics
  const getPlatformStats = () => {
    const platforms = [...new Set(ecomData.products.map(p => p.platform))];
    const categories = [...new Set(ecomData.products.map(p => p.category))];
    const brands = [...new Set(ecomData.products.map(p => p.brand_name))];
    
    return {
      totalProducts: ecomData.products.length,
      platforms: platforms.length,
      categories: categories.length,
      brands: brands.length
    };
  };

  // Function to generate data-driven response (fallback when Groq is not available)
  const generateDataResponse = (query: string) => {
    const lowerQuery = query.toLowerCase();

    // 1. Check for product matches in e-commerce data
    const ecomResults = searchEcomData(query);
    
    // 2. Check for delivery matches
    const deliveryResults = searchDeliveryData(query);
    
    // 3. If we have both types of results, prioritize based on query context
    if (ecomResults.length > 0 && deliveryResults.length > 0) {
      // If query seems more delivery-focused, show delivery results first
      if (lowerQuery.includes('delivery') || lowerQuery.includes('grocery') || lowerQuery.includes('food') || lowerQuery.includes('snack')) {
        const topResults = deliveryResults.slice(0, 3);
        let response = `🚚 **Quick Delivery Options:**\n\n`;
        topResults.forEach(product => {
          response += `**${product.product_name}**\n`;
          response += `💰 Cost: ${product.cost}\n`;
          response += `⚖️ Weight: ${product.weight}\n`;
          response += `🚚 Delivery: ${product.delivery_time}\n`;
          response += `🏪 Platform: ${product.platform}\n`;
          response += `📂 Category: ${product.category}\n\n`;
        });
        if (deliveryResults.length > 3) {
          response += `... and ${deliveryResults.length - 3} more items.\n\n`;
        }
        response += `🏷️ **Also found ${ecomResults.length} e-commerce products.** Try searching for a specific brand or product name.`;
        return response;
      } else {
        // Show e-commerce results first
        const topResults = ecomResults.slice(0, 3);
        let response = `🏷️ **Found ${ecomResults.length} products matching your query:**\n\n`;
        topResults.forEach(product => {
          response += `**${product.product_name}** (${product.brand_name})\n`;
          response += `💰 Price: ₹${product.cost_inr}\n`;
          response += `🏪 Platform: ${product.platform}\n`;
          response += `📦 Delivery: ${product.estimated_delivery}\n`;
          response += `📋 Category: ${product.category} > ${product.sub_category}\n`;
          response += `✅ In Stock: ${product.in_stock ? 'Yes' : 'No'}\n\n`;
        });
        if (ecomResults.length > 3) {
          response += `... and ${ecomResults.length - 3} more products.\n\n`;
        }
        response += `🚚 **Also found ${deliveryResults.length} delivery items.** Try asking about delivery or grocery for quick delivery options.`;
        return response;
      }
    }
    
    // 4. If only e-commerce results found
    if (ecomResults.length > 0) {
      const topResults = ecomResults.slice(0, 3);
      let response = `🏷️ **Found ${ecomResults.length} products matching your query:**\n\n`;
      topResults.forEach(product => {
        response += `**${product.product_name}** (${product.brand_name})\n`;
        response += `💰 Price: ₹${product.cost_inr}\n`;
        response += `🏪 Platform: ${product.platform}\n`;
        response += `📦 Delivery: ${product.estimated_delivery}\n`;
        response += `📋 Category: ${product.category} > ${product.sub_category}\n`;
        response += `✅ In Stock: ${product.in_stock ? 'Yes' : 'No'}\n\n`;
      });
      if (ecomResults.length > 3) {
        response += `... and ${ecomResults.length - 3} more products. Try a more specific search!`;
      }
      return response;
    }
    
    // 5. If only delivery results found
    if (deliveryResults.length > 0) {
      const topResults = deliveryResults.slice(0, 3);
      let response = `🚚 **Quick Delivery Options:**\n\n`;
      topResults.forEach(product => {
        response += `**${product.product_name}**\n`;
        response += `💰 Cost: ${product.cost}\n`;
        response += `⚖️ Weight: ${product.weight}\n`;
        response += `🚚 Delivery: ${product.delivery_time}\n`;
        response += `🏪 Platform: ${product.platform}\n`;
        response += `📂 Category: ${product.category}\n\n`;
      });
      if (deliveryResults.length > 3) {
        response += `... and ${deliveryResults.length - 3} more items. Try a more specific search!`;
      }
      return response;
    }

    // 6. Platform info
    if (lowerQuery.includes('bestpickr') || lowerQuery.includes('platform') || lowerQuery.includes('features') || lowerQuery.includes('help')) {
      const stats = getPlatformStats();
      return `🏪 BestPickr Platform Overview\n\n` +
             `📊 Data Statistics:\n` +
             `• Total Products: ${stats.totalProducts}\n` +
             `• E-commerce Platforms: ${stats.platforms} (Amazon, Flipkart, Myntra)\n` +
             `• Product Categories: ${stats.categories}\n` +
             `• Brands Available: ${stats.brands}\n` +
             `• Quick Delivery Platforms: ${quickDeliveryData.platforms.length}\n` +
             `• Ride Routes: ${rideData.rides.length}\n\n` +
             `🔍 **What I can help you with:**\n` +
             `• Search for specific products and prices\n` +
             `• Compare delivery options and timing\n` +
             `• Find ride-sharing options and costs\n` +
             `• Browse products by category or brand\n\n` +
             `Try asking: Show me Nike shoes, Grocery delivery options, or Ride from MG Road`;
    }

    // 7. Category/brand browsing
    if (lowerQuery.includes('category') || lowerQuery.includes('categories') || lowerQuery.includes('brands')) {
      const categories = [...new Set(ecomData.products.map(p => p.category))];
      const brands = [...new Set(ecomData.products.map(p => p.brand_name))];
      
      return `📂 **Available Categories:**\n${categories.join(', ')}\n\n` +
             `🏷️ **Popular Brands:**\n${brands.slice(0, 10).join(', ')}...\n\n` +
             `Ask me about any specific category or brand!`;
    }

    // 8. Ride
    if (lowerQuery.includes('ride') || lowerQuery.includes('uber') || lowerQuery.includes('ola') || lowerQuery.includes('rapido') || lowerQuery.includes('taxi')) {
      const rideResults = searchRideData(query);
      if (rideResults.length > 0) {
        const topResults = rideResults.slice(0, 3);
        let response = `🚗 **Ride Options:**\n\n`;
        topResults.forEach(ride => {
          response += `**${ride.platform}**\n`;
          response += `📍 From: ${ride.pickup_location}\n`;
          response += `🎯 To: ${ride.destination}\n`;
          response += `📏 Distance: ${ride.distance_km} km\n\n`;
          ride.vehicles.forEach(vehicle => {
            response += `  🛵 ${vehicle.vehicle_type}: ₹${vehicle.cost_inr} (${vehicle.travel_time_minutes} min)\n`;
          });
          response += `\n`;
        });
        if (rideResults.length > 3) {
          response += `... and ${rideResults.length - 3} more routes. Try a more specific location!`;
        }
        return response;
      } else {
        return `❌ No ride routes found for ${query}.\n\n` +
               `💡 Try searching for:\n` +
               `• Popular locations: MG Road, Whitefield, Electronic City\n` +
               `• Platforms: Uber, Ola, Rapido\n` +
               `• Or ask about ride options in general`;
      }
    }

    // 9. Default - no results found
    return `🔍 **I couldn't find specific data for ${query}.**\n\n` +
           `**Here's what I can help you discover:**\n` +
           `🛍️ **Products & Shopping**\n` +
           `• Search for brands: Nike, Adidas, Boat, Puma\n` +
           `• Browse categories: Electronics, Fashion, Footwear\n` +
           `• Find specific items: headphones, shoes, clothing\n` +
           `🚚 **Quick Delivery**\n` +
           `• Grocery items: vegetables, fruits, snacks\n` +
           `• Popular snacks: Kurkure, Lays, Cheetos\n` +
           `• Fresh produce: tomato, potato, onion\n` +
           `🚗 **Ride Services**\n` +
           `• Platforms: Uber, Ola, Rapido\n` +
           `• Popular routes: MG Road, Whitefield, Electronic City\n` +
           `ℹ️ **Platform Info**\n` +
           `• Ask about: BestPickr features, categories, brands\n\n` +
           `**Try a more specific search or ask about any of the above!**`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Add user message to chat
    const userMessage: Message = { role: 'user', parts: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Try to use Groq AI first, fallback to data-driven response if it fails
      let response: string;
      
      try {
        // Prepare context data for Groq
        const contextData = {
          ecomData,
          deliveryData: quickDeliveryData,
          rideData
        };
        
        response = await generateChatbotResponse(input, contextData);
      } catch (groqError) {
        console.warn('Groq AI failed, falling back to data-driven response:', groqError);
        // Fallback to the original data-driven response
        response = generateDataResponse(input);
      }
      
      setMessages(prev => [...prev, { role: 'model', parts: response }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'model', 
        parts: 'Sorry, I encountered an error while processing your request. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-lavender-600 hover:bg-lavender-700 text-white p-4 rounded-full shadow-lg transition-all duration-300 flex items-center justify-center"
        aria-label="Open chat"
      >
        <Bot size={24} />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 bg-gray-800 rounded-xl shadow-xl flex flex-col" style={{ height: '600px' }}>
      <div className="bg-lavender-600 text-white p-4 rounded-t-xl flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Bot size={20} />
          <h3 className="font-semibold">BestPickrBot</h3>
        </div>
        <button 
          onClick={() => setIsOpen(false)}
          className="text-white hover:text-gray-200"
          aria-label="Close chat"
        >
          <X size={20} />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`max-w-[80%] p-3 rounded-lg whitespace-pre-line break-words ${
                message.role === 'user' 
                  ? 'bg-lavender-600 text-white rounded-br-none' 
                  : 'bg-gray-700 text-gray-100 rounded-bl-none'
              }`}
              style={{ fontFamily: 'inherit', fontSize: '1rem', lineHeight: '1.6' }}
            >
              {message.parts.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line.trim().startsWith('**') && line.trim().endsWith('**') ? (
                    <span className="font-bold text-lavender-300">{line.replace(/\*\*/g, '')}</span>
                  ) : line.trim().startsWith('🏷️') || line.trim().startsWith('🚚') || line.trim().startsWith('🚗') || line.trim().startsWith('📂') || line.trim().startsWith('📊') || line.trim().startsWith('🔍') || line.trim().startsWith('📋') ? (
                    <span className="block mt-2 mb-1 font-semibold text-lavender-400">{line}</span>
                  ) : line.trim().startsWith('•') ? (
                    <span className="block pl-4">{line}</span>
                  ) : line.trim().startsWith('❌') || line.trim().startsWith('🤔') ? (
                    <span className="block text-red-400 font-semibold mt-2">{line}</span>
                  ) : line.trim().startsWith('💡') ? (
                    <span className="block text-yellow-300 font-semibold mt-2">{line}</span>
                  ) : line.trim().startsWith('...') ? (
                    <span className="block text-gray-400 italic">{line}</span>
                  ) : line.trim() === '' ? (
                    <br />
                  ) : (
                    <span>{line}</span>
                  )}
                  <br />
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-gray-100 p-3 rounded-lg rounded-bl-none max-w-[80%]">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Listening..." : "Type or speak your message..."}
            className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-lavender-500"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={handleVoiceInput}
            disabled={isLoading}
            className={`p-2 rounded-lg transition-all duration-200 ${
              isListening 
                ? 'bg-red-600 hover:bg-red-700 animate-pulse' 
                : 'bg-green-600 hover:bg-green-700'
            } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
            title={isListening ? "Stop listening" : "Start voice input"}
          >
            {isListening ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-lavender-600 hover:bg-lavender-700 text-white p-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatBot;

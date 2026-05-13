import re
from typing import Dict, List, Optional, Any, Union
import random
from datetime import datetime
import json

class ThrifCartChatbot:
    """
    A rule-based chatbot for BestPickr that can answer questions about products, 
    compare prices, and provide recommendations.
    """
    
    def __init__(self, product_catalog: List[Dict] = None, user_preferences: Dict = None):
        """
        Initialize the BestPickr chatbot.
        
        Args:
            product_catalog: List of product dictionaries
            user_preferences: Dictionary containing user preferences
        """
        self.product_catalog = product_catalog or []
        self.user_preferences = user_preferences or {}
        self.context = {}
        self.greetings = [
            "Hi there! I'm your BestPickr AI assistant. How can I help you today?",
            "Hello! Ready to find some great deals? What can I help you with?",
            "Hey! I'm here to help you compare prices and find the best products. What do you need?"
        ]
        
        # Define response templates
        self.templates = {
            'greeting': random.choice([
                "Hi there! I'm your BestPickr AI assistant. How can I help you today?",
                "Hello! Ready to find some great deals? What can I help you with?",
                "Hey! I'm here to help you compare prices and find the best products. What do you need?"
            ]),
            'product_info': "I found {count} {product_name} products. {details}",
            'price_comparison': "Here's how {product_name} compares across platforms:\n{comparison}",
            'recommendation': "Based on your preferences, I recommend: {recommendations}",
            'help': "I can help you with:\n- Finding products\n- Comparing prices\n- Getting recommendations\n- Answering questions about BestPickr",
            'fallback': "I'm not sure I understand. Could you rephrase that?"
        }
        
        # Define patterns for intent recognition
        self.patterns = {
            'greeting': [
                r'hi|hello|hey|greetings',
                r'good\s*(morning|afternoon|evening)'
            ],
            'product_search': [
                r'(find|search|show)\s+(me\s+)?(products?\s+)?(called|named|like)?\s*([\w\s]+)',
                r'(do\s+you\s+have|is\s+there)\s+([\w\s]+)'
            ],
            'price_comparison': [
                r'(compare|price\s+of|cost\s+of|how much is|price for)\s+([\w\s]+)',
                r'(which\s+is\s+cheaper|best\s+price|cheapest)\s+(for|on)?\s*([\w\s]+)'
            ],
            'recommendation': [
                r'(recommend|suggest|what should i buy|what do you suggest)',
                r'(best|top|popular)\s+(products?|items?)'
            ],
            'help': [
                r'help|what can you do|how does this work',
                r'show\s+(me\s+)?(commands|options|menu)'
            ],
            'thanks': [
                r'thanks|thank you|appreciate it|cheers',
                r'that\'s\s+helpful|great, thanks'
            ]
        }
        
        # Initialize product categories
        self.categories = {
            'grocery': ['food', 'grocery', 'vegetables', 'fruits', 'snacks', 'beverages'],
            'electronics': ['phone', 'laptop', 'tv', 'camera', 'headphones', 'tablet'],
            'fashion': ['shirt', 'pants', 'dress', 'shoes', 'accessories', 'watch'],
            'home': ['furniture', 'appliances', 'decor', 'kitchen', 'bedding']
        }
        
    def _match_pattern(self, text: str, intent: str) -> Optional[re.Match]:
        """
        Check if the input text matches any pattern for the given intent.
        
        Args:
            text: Input text from user
            intent: Intent to match against
            
        Returns:
            re.Match object if a match is found, None otherwise
        """
        for pattern in self.patterns.get(intent, []):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match
        return None
    
    def _extract_product_name(self, text: str) -> Optional[str]:
        """
        Extract product name from user input.
        
        Args:
            text: User input text
            
        Returns:
            Extracted product name or None if not found
        ""
        # Try to match product search patterns
        for pattern in self.patterns['product_search'] + self.patterns['price_comparison']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the last group which should contain the product name
                for group in reversed(match.groups()):
                    if group and len(group.strip()) > 1:  # Ensure it's not a single character
                        return group.strip()
        return None
    """
    def _find_products(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """
        
        Find products matching the query.
        
        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of results to return
            
        Returns:
            List of matching products
        """
        if not self.product_catalog:
            return []
            
        query = query.lower()
        results = []
        
        for product in self.product_catalog:
            # Skip if category filter is provided and doesn't match
            if category and product.get('category', '').lower() != category.lower():
                continue
                
            # Check if query matches product name, description, or category
            if (query in product.get('name', '').lower() or 
                query in product.get('description', '').lower() or
                query in product.get('category', '').lower()):
                results.append(product)
                
                # Stop if we've reached the limit
                if len(results) >= limit:
                    break
        
        return results
    
    def _compare_prices(self, product_name: str) -> str:


        """
        Compare prices for a product across platforms.
        
        Args:
            product_name: Name of the product to compare
            
        Returns:
            Formatted comparison string
        ""
        # In a real implementation, this would query the database or API
        # For now, we'll use mock data
        mock_comparison = [
            {"platform": "Amazon", "price": 499, "rating": 4.5, "delivery": "2 days"},
            {"platform": "Flipkart", "price": 489, "rating": 4.3, "delivery": "3 days"},
            {"platform": "Myntra", "price": 525, "rating": 4.2, "delivery": "1 day"},
            {"platform": "Ajio", "price": 510, "rating": 4.0, "delivery": "2 days"}
        ]
        
        # Sort by price (cheapest first)
        mock_comparison.sort(key=lambda x: x['price'])
        
        # Format the comparison
        comparison_lines = []
        for item in mock_comparison:
            comparison_lines.append(
                f"- {item['platform']}: ₹{item['price']} (Rating: {item['rating']}★, Delivery: {item['delivery']})"
            )
        
        return "\n".join(comparison_lines)
    
    def _get_recommendations(self, user_id: str = None, limit: int = 3) -> List[Dict]:
        """
        """"
        Get product recommendations for a user.
        
        Args:
            user_id: ID of the user (optional)
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended products
        
            """
        # In a real implementation, this would use a recommendation model
        # For now, return some popular products
        if not self.product_catalog:
            return []
            
        # Sort by rating and return top N
        sorted_products = sorted(
            self.product_catalog,
            key=lambda x: x.get('rating', 0),
            reverse=True
        )
        
        return sorted_products[:limit]
    
    def process_message(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            message: User's message
            user_id: Optional user ID for personalized responses
            
        Returns:
            Dictionary containing the response and metadata
        """
        message = message.lower().strip()
        response = {
            'text': '',
            'intent': None,
            'entities': {},
            'context': self.context,
            'suggestions': []
        }
        
        # Check for greetings
        if self._match_pattern(message, 'greeting'):
            response['text'] = random.choice(self.greetings)
            response['intent'] = 'greeting'
            return response
            
        # Check for help request
        if self._match_pattern(message, 'help'):
            response['text'] = self.templates['help']
            response['intent'] = 'help'
            return response
            
        # Check for thanks
        if self._match_pattern(message, 'thanks'):
            response['text'] = "You're welcome! Is there anything else I can help you with?"
            response['intent'] = 'thanks'
            return response
        
        # Check for product search
        product_search = self._match_pattern(message, 'product_search')
        if product_search:
            product_name = self._extract_product_name(message)
            if product_name:
                products = self._find_products(product_name)
                if products:
                    product_list = "\n".join([f"- {p['name']} (₹{p.get('price', 'N/A')})" for p in products[:3]])
                    response['text'] = f"I found these {product_name} products:\n{product_list}"
                    if len(products) > 3:
                        response['text'] += f"\n...and {len(products) - 3} more."
                    
                    # Add suggestions for price comparison
                    response['suggestions'].extend([
                        f"Compare prices for {product_name}",
                        f"Show me more {product_name} products"
                    ])
                else:
                    response['text'] = f"I couldn't find any products matching '{product_name}'. Could you try a different search term?"
                
                response['intent'] = 'product_search'
                response['entities']['product'] = product_name
                return response
        
        # Check for price comparison
        price_compare = self._match_pattern(message, 'price_comparison')
        if price_compare or 'compare' in message.lower():
            product_name = self._extract_product_name(message)
            if product_name:
                comparison = self._compare_prices(product_name)
                if comparison:
                    response['text'] = f"Here's how {product_name} compares across platforms:\n{comparison}"
                    
                    # Add suggestions
                    response['suggestions'].extend([
                        f"Show me reviews for {product_name}",
                        f"Where can I get the best deal on {product_name}?"
                    ])
                else:
                    response['text'] = f"I couldn't find price comparison data for '{product_name}'."
                
                response['intent'] = 'price_comparison'
                response['entities']['product'] = product_name
                return response
        
        # Check for recommendations
        if self._match_pattern(message, 'recommendation'):
            recommendations = self._get_recommendations(user_id=user_id)
            if recommendations:
                rec_list = "\n".join([f"- {r['name']} (Rating: {r.get('rating', 'N/A')}★, Price: ₹{r.get('price', 'N/A')})" 
                                     for r in recommendations])
                response['text'] = f"Here are some recommendations for you:\n{rec_list}"
                
                # Add suggestions
                response['suggestions'].extend([
                    "Show me more recommendations",
                    "Filter by category"
                ])
            else:
                response['text'] = "I couldn't find any recommendations at the moment. Please try again later."
            
            response['intent'] = 'recommendation'
            return response
        
        # Fallback response
        response['text'] = self.templates['fallback']
        response['intent'] = 'unknown'
        response['suggestions'] = [
            "How do I compare prices?",
            "Can you recommend products?",
            "What can you help me with?"
        ]
        
        return response
    
    def get_suggested_responses(self) -> List[str]:
        """
        Get a list of suggested responses to help the user.
        
        Returns:
            List of suggested response strings
        """
        return [
            "Show me the best deals",
            "Compare prices for smartphones",
            "What's on sale today?",
            "Help me find a gift"
        ]
    
    def update_context(self, context: Dict) -> None:
        """
        Update the chatbot's context.
        
        Args:
            context: Dictionary containing context information
        """
        self.context.update(context)
    
    def set_user_preferences(self, preferences: Dict) -> None:
        """
        Set or update user preferences.
        
        Args:
            preferences: Dictionary containing user preferences
        """
        self.user_preferences.update(preferences)
    
    def set_product_catalog(self, catalog: List[Dict]) -> None:
        """
        Set the product catalog for the chatbot to use.
        
        Args:
            catalog: List of product dictionaries
        """
        self.product_catalog = catalog

# Example usage
if __name__ == "__main__":
    # Example product catalog
    example_products = [
        {"id": 1, "name": "iPhone 13", "category": "Electronics", "price": 69900, "rating": 4.7},
        {"id": 2, "name": "Samsung Galaxy S21", "category": "Electronics", "price": 64999, "rating": 4.5},
        {"id": 3, "name": "OnePlus 9 Pro", "category": "Electronics", "price": 66999, "rating": 4.6},
        {"id": 4, "name": "Nike Air Max", "category": "Fashion", "price": 12999, "rating": 4.4},
        {"id": 5, "name": "Adidas Ultraboost", "category": "Fashion", "price": 15999, "rating": 4.5},
    ]
    
    # Initialize chatbot
    chatbot = ThrifCartChatbot(product_catalog=example_products)
    
    # Example conversation
    print("Chatbot: " + chatbot.templates['greeting'])
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Chatbot: Goodbye! Have a great day!")
            break
            
        response = chatbot.process_message(user_input)
        print("\nChatbot:", response['text'])
        
        if response['suggestions']:
            print("\nSuggestions:")
            for i, suggestion in enumerate(response['suggestions'], 1):
                print(f"{i}. {suggestion}")

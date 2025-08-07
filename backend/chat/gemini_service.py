import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in settings")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Customer support context and instructions
        self.system_prompt = """
        You are a helpful customer support assistant. Your role is to:
        
        1. Provide friendly, professional, and helpful responses
        2. Help customers with their questions and issues
        3. Escalate complex issues when necessary
        4. Maintain a positive and empathetic tone
        5. Ask clarifying questions when needed
        6. Provide step-by-step solutions when appropriate
        
        Guidelines:
        - Always be polite and professional
        - If you don't know something, admit it and offer to escalate
        - Keep responses concise but comprehensive
        - Use markdown formatting for better readability
        - If a customer seems frustrated, acknowledge their feelings
        - Offer multiple solutions when possible
        
        Common topics you can help with:
        - Account issues
        - Billing questions
        - Technical support
        - Product information
        - Order status
        - Returns and refunds
        - Mental health
        
        If a customer needs human assistance, let them know you can create a support ticket for them.
        """
    
    def generate_response(self, user_message: str, conversation_history: list = None) -> str:
        try:
            # Build the conversation context
            context = self.system_prompt + "\n\nConversation:\n"
            
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    role = "Customer" if msg['sender'] == 'user' else "Assistant"
                    context += f"{role}: {msg['content']}\n"
            
            context += f"Customer: {user_message}\nAssistant:"
            
            # Generate response using Gemini
            response = self.model.generate_content(context)
            
            if response.text:
                return response.text.strip()
            else:
                return "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team for assistance."
                
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            return "I'm experiencing technical difficulties at the moment. Please try again later or contact our support team for immediate assistance."
    
    def analyze_intent(self, message: str) -> dict:
        """Analyze user message to determine intent and extract key information"""
        try:
            analysis_prompt = f"""
            Analyze this customer support message and return a JSON response with:
            1. intent: (greeting, question, complaint, compliment, request_human, technical_issue, billing_issue, account_issue, other)
            2. urgency: (low, medium, high, urgent)
            3. sentiment: (positive, neutral, negative)
            4. requires_human: (true/false)
            5. key_topics: (array of main topics mentioned)
            
            Message: "{message}"
            
            Respond only with valid JSON.
            """
            
            response = self.model.generate_content(analysis_prompt)
            
            if response.text:
                import json
                try:
                    return json.loads(response.text.strip())
                except json.JSONDecodeError:
                    pass
            
            # Fallback response
            return {
                "intent": "other",
                "urgency": "medium",
                "sentiment": "neutral",
                "requires_human": False,
                "key_topics": []
            }
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {str(e)}")
            return {
                "intent": "other",
                "urgency": "medium",
                "sentiment": "neutral",
                "requires_human": False,
                "key_topics": []
            }
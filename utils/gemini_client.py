import google.generativeai as genai
from config import Config
import logging

class GeminiClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Check if API key is configured
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == 'your_actual_gemini_api_key_here':
            self.gemini_available = False
            self.logger.error("❌ Gemini API key is not configured!")
            return
        
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            self.gemini_available = True
            self.logger.info("✅ Gemini AI client initialized successfully")
        except Exception as e:
            self.gemini_available = False
            self.logger.error(f"❌ Gemini AI initialization failed: {str(e)}")
    
    def generate_response(self, prompt, context=None, max_tokens=500):
        """
        Generate AI response using Gemini
        
        Args:
            prompt (str): User's message
            context (str, optional): Context from browsing history
            max_tokens (int): Maximum tokens in response
            
        Returns:
            str: AI generated response
        """
        # Check if Gemini is available
        if not self.gemini_available:
            return "Hello! I'm your browser assistant. To enable AI chat features, please configure the Gemini API key in the backend settings. You can get a free API key from https://ai.google.dev/"
        
        try:
            # Add context if provided
            if context:
                enhanced_prompt = f"""
                Context from user's browsing activity: {context}
                
                User question: {prompt}
                
                Please provide a helpful response considering the user's browsing context.
                """
            else:
                enhanced_prompt = f"""
                User question: {prompt}
                
                Please provide a helpful and friendly response.
                """
            
            # Generate response
            response = self.model.generate_content(
                enhanced_prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            )
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
    
    def get_chat_context(self, user_id, session_id):
        """
        Retrieve recent browsing context for AI response
        """
        # For now, return a simple context
        # You can enhance this to fetch actual browsing history
        return "User is using a browser extension with AI chat capabilities."
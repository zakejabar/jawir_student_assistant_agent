"""
OpenRouter LLM configuration and client setup
"""
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMConfig:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-3.1-8b-instruct"  # Free tier model
        
    def get_llm(self):
        """Get configured LLM instance"""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
            
        return ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            openai_api_base=self.base_url,
            temperature=0.1,  # Lower temperature for consistent extraction
            max_tokens=2000
        )
        
    def test_connection(self):
        """Test LLM connection"""
        try:
            llm = self.get_llm()
            response = llm.invoke("Hello, test message.")
            return True, response.content
        except Exception as e:
            return False, str(e)

# Global config instance
llm_config = LLMConfig()

import logging
import time
import requests
import json
import subprocess
import sys
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handler for local LLaMA2 model via Ollama"""
    
    def __init__(self):
        self.model_name = "llama2:7b"  # Using 7B for better speed
        self.base_url = "http://localhost:11434"
        self.api_url = f"{self.base_url}/api/generate"
        self.model_loaded = False
        
        # Model configuration
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "num_predict": 2000,
            "stop": ["Human:", "Assistant:", "\n\n---"]
        }
    
    def initialize(self):
        """Initialize the LLM handler"""
        try:
            logger.info("Initializing LLM handler...")
            
            # Check if Ollama is running
            if not self._check_ollama_running():
                logger.info("Starting Ollama service...")
                self._start_ollama()
            
            # Pull model if not available
            if not self._check_model_available():
                logger.info(f"Pulling {self.model_name} model...")
                self._pull_model()
            
            # Test model
            self._test_model()
            
            self.model_loaded = True
            logger.info("LLM handler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM handler: {str(e)}")
            raise
    
    def _check_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _start_ollama(self):
        """Start Ollama service"""
        try:
            # Try to start Ollama in the background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait a bit for service to start
            time.sleep(5)
            
            # Check if it's running now
            if not self._check_ollama_running():
                raise Exception("Failed to start Ollama service")
                
        except FileNotFoundError:
            raise Exception("Ollama is not installed. Please run the setup script first.")
        except Exception as e:
            raise Exception(f"Failed to start Ollama: {str(e)}")
    
    def _check_model_available(self) -> bool:
        """Check if the model is available locally"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model["name"].startswith(self.model_name):
                        return True
            return False
        except:
            return False
    
    def _pull_model(self):
        """Pull the LLaMA2 model"""
        try:
            pull_data = {"name": self.model_name}
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=pull_data,
                stream=True,
                timeout=1800  # 30 minutes timeout for model download
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to pull model: {response.status_code}")
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    if data.get("status"):
                        logger.info(f"Model pull: {data['status']}")
                    if data.get("error"):
                        raise Exception(f"Model pull error: {data['error']}")
                        
        except requests.exceptions.Timeout:
            raise Exception("Model download timeout. Please check your internet connection.")
        except Exception as e:
            raise Exception(f"Failed to pull model: {str(e)}")
    
    def _test_model(self):
        """Test the model with a simple query"""
        try:
            test_response = self.generate_response(
                question="What is law?",
                context="",
                max_tokens=50
            )
            
            if not test_response or len(test_response.strip()) == 0:
                raise Exception("Model test failed - empty response")
                
            logger.info("Model test successful")
            
        except Exception as e:
            raise Exception(f"Model test failed: {str(e)}")
    
    def generate_response(self, question: str, context: str = "", max_tokens: int = 1000) -> str:
        """Generate response using local LLaMA2 model"""
        if not self.model_loaded:
            return "Model not loaded. Please check the system status."
        
        try:
            # Create prompt
            prompt = self._create_prompt(question, context)
            
            # Prepare request data
            request_data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    **self.generation_config,
                    "num_predict": min(max_tokens, 2000)
                }
            }
            
            # Make API call
            start_time = time.time()
            response = requests.post(
                self.api_url,
                json=request_data,
                timeout=120  # 2 minutes timeout
            )
            
            if response.status_code != 200:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return "I apologize, but I'm experiencing technical difficulties. Please try again."
            
            # Parse response
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            generation_time = time.time() - start_time
            logger.info(f"Generated response in {generation_time:.2f} seconds")
            
            # Post-process response
            generated_text = self._post_process_response(generated_text)
            
            return generated_text if generated_text else "I couldn't generate a response. Please rephrase your question."
            
        except requests.exceptions.Timeout:
            logger.error("LLM request timeout")
            return "The request is taking longer than expected. Please try with a simpler question."
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            return "I encountered an error while processing your request. Please try again."
    
    def _create_prompt(self, question: str, context: str = "") -> str:
        """Create a structured prompt for legal question answering"""
        
        if context.strip():
            prompt = f"""You are a knowledgeable legal assistant. Answer the question based on the provided context. Be accurate, concise, and cite relevant sections when possible.

Context:
{context}

Question: {question}

Answer: Provide a clear, accurate response based on the context above. If the context doesn't contain enough information, say so clearly."""
        else:
            prompt = f"""You are a knowledgeable legal assistant with expertise in Indian law. Provide accurate, helpful information about legal matters.

Question: {question}

Answer: Provide a clear, accurate legal response. If you're not certain about specific details, mention that and suggest consulting with a qualified legal professional."""
        
        return prompt
    
    def _post_process_response(self, response: str) -> str:
        """Clean and format the model response"""
        # Remove common artifacts
        response = response.replace("Answer:", "").strip()
        response = response.replace("Response:", "").strip()
        
        # Remove repetitive patterns
        lines = response.split('\n')
        cleaned_lines = []
        prev_line = ""
        
        for line in lines:
            line = line.strip()
            if line and line != prev_line:
                cleaned_lines.append(line)
                prev_line = line
        
        response = '\n\n'.join(cleaned_lines)
        
        # Limit response length
        max_length = 2000
        if len(response) > max_length:
            response = response[:max_length] + "..."
        
        return response.strip()
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status"""
        try:
            if not self._check_ollama_running():
                return {"status": "offline", "message": "Ollama service not running"}
            
            if not self._check_model_available():
                return {"status": "model_missing", "message": f"Model {self.model_name} not available"}
            
            return {
                "status": "ready",
                "message": "Model ready for inference",
                "model_name": self.model_name,
                "loaded": self.model_loaded
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def reload_model(self):
        """Reload the model"""
        try:
            self.model_loaded = False
            self.initialize()
            return True
        except Exception as e:
            logger.error(f"Failed to reload model: {str(e)}")
            return False
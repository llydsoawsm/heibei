from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import json
import logging
import requests

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'chatbot/index.html')

def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            
            if not settings.OPENAI_API_KEY:
                logger.error("OpenRouter API key not found in settings")
                return JsonResponse(
                    {"response": "AI Assistant is not configured. Please add your OpenRouter API key to the .env file."},
                    status=200
                )
            
            # OpenRouter API endpoint
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            # Request headers for OpenRouter
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "HeiBei AI Assistant",
                "Content-Type": "application/json"
            }
            
            # Request body - using Mistral's free model
            payload = {
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "system", "content": "You are HeiBei, a friendly and knowledgeable AI assistant."},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                logger.info(f"Chat response status: {response.status_code}")
                logger.info(f"Chat response body: {response.text}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    ai_response = response_data['choices'][0]['message']['content']
                    return JsonResponse({"response": ai_response})
                else:
                    error_message = "Unknown error"
                    try:
                        error_data = response.json()
                        error_message = error_data.get('error', {}).get('message', error_message)
                        
                        # Check for rate limit and quota errors
                        if any(keyword in error_message.lower() for keyword in ["rate limit", "quota", "insufficient_quota"]) or response.status_code in [402, 429]:
                            return JsonResponse({
                                "response": "🔄 Free tier limit reached! Here's how to continue:\n\n"
                                           "1. Get a new API key:\n"
                                           "   - Go to https://openrouter.ai/\n"
                                           "   - Create a new account\n"
                                           "   - Get your API key from https://openrouter.ai/keys\n\n"
                                           "2. Update your settings:\n"
                                           "   - Open settings.py\n"
                                           "   - Replace the current OPENAI_API_KEY with your new key\n\n"
                                           "3. Restart the Django server\n\n"
                                           "Tip: You might want to keep a few backup API keys ready for next time! 😊"
                            }, status=200)
                        
                    except:
                        error_message = f"Error {response.status_code}"
                    
                    logger.error(f"OpenRouter error: {error_message}")
                    return JsonResponse({
                        "response": "I apologize, but I'm having trouble connecting to my AI service right now. Please try again in a moment."
                    }, status=200)
                    
            except Exception as e:
                logger.error(f"Request error: {str(e)}")
                return JsonResponse({
                    "response": "I encountered an error while processing your request. Please try again."
                }, status=200)
                
        except json.JSONDecodeError:
            return JsonResponse({"response": "Invalid request format"}, status=200)
        except Exception as e:
            logger.error(f"Unexpected error in chat view: {str(e)}")
            return JsonResponse({"response": "An unexpected error occurred. Please try again."}, status=200)
    return JsonResponse({"response": "Invalid request method"}, status=200)

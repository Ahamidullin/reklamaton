import google.generativeai as genai
from config import GOOGLE_API_KEY, DEEPINFRA_API_KEY
from pydub import AudioSegment
import io
from google.cloud import speech
import requests
from io import BytesIO
from urllib.parse import quote_plus
import httpx
import json

genai.configure(api_key=GOOGLE_API_KEY)

async def get_deepinfra_response(character: "Character", history: list[dict]) -> str:
    """Get response from DeepInfra Mistral model"""
    if not DEEPINFRA_API_KEY:
        raise ValueError("DEEPINFRA_API_KEY is not set")
    
    # Build system prompt
    if character.description:
        system_prompt = f"Ты — {character.name}. {character.description}. Отвечай на русском языке."
    else:
        # Construct a detailed prompt for constructor-based characters
        prompt_parts = [
            f"Ты — {character.name}, AI-персонаж.",
            f"Твой архетип по MBTI: {character.archetype}.",
            f"Стиль твоего общения: {character.communication_style}.",
            f"Уровень твоего сарказма: {character.sarcasm_level} из 5.",
            f"Уровень твоего юмора: {character.humor_level} из 5.",
            f"Уровень твоего флирта: {character.flirt_level} из 5.",
            f"Уровень твоей непредсказуемости: {character.unpredictability_level} из 5.",
            f"Наличие черного юмора: {'да' if character.has_black_humor else 'нет'}.",
            "Веди диалог строго в соответствии с этими чертами.",
            "Отвечай на русском языке."
        ]
        system_prompt = " ".join(prompt_parts)
    
    # If no history, return greeting
    if not history:
        return f"Привет! Я {character.name}. Рад с тобой пообщаться. Что скажешь?"
    
    # Prepare messages for DeepInfra API
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Make API request
    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}"
    }
    
    payload = {
        "model": "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("choices") and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "К сожалению, не удалось получить ответ от AI. Попробуйте еще раз."
                
    except httpx.HTTPStatusError as e:
        print(f"Error calling DeepInfra API: {e.response.status_code} {e.response.text}")
        return "К сожалению, произошла ошибка при общении с AI. Попробуйте еще раз."
    except Exception as e:
        print(f"Error calling DeepInfra API: {e}")
        return "К сожалению, произошла ошибка при общении с AI. Попробуйте еще раз."

async def get_gemini_response(character: "Character", history: list[dict]) -> str:
    """Get response from Gemini or DeepInfra based on available API keys"""
    
    # Check which API to use - if Google API key is available, use Gemini; otherwise use DeepInfra
    if GOOGLE_API_KEY:
        # Use Gemini (existing code)
        if character.description:
            system_prompt = f"Ты — {character.name}. {character.description}. Отвечай на русском языке."
        else:
            # Construct a detailed prompt for constructor-based characters
            prompt_parts = [
                f"Ты — {character.name}, AI-персонаж.",
                f"Твой архетип по MBTI: {character.archetype}.",
                f"Стиль твоего общения: {character.communication_style}.",
                f"Уровень твоего сарказма: {character.sarcasm_level} из 5.",
                f"Уровень твоего юмора: {character.humor_level} из 5.",
                f"Уровень твоего флирта: {character.flirt_level} из 5.",
                f"Уровень твоей непредсказуемости: {character.unpredictability_level} из 5.",
                f"Наличие черного юмора: {'да' if character.has_black_humor else 'нет'}.",
                "Веди диалог строго в соответствии с этими чертами.",
                "Отвечай на русском языке."
            ]
            system_prompt = " ".join(prompt_parts)

        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=system_prompt
        )
        
        if not history:
            return f"Привет! Я {character.name}. Рад с тобой пообщаться. Что скажешь?"

        # The entire history is sent to the model now, let's format it all.
        api_history = [
            {"role": msg["role"], "parts": [{"text": msg["content"]}]}
            for msg in history
        ]

        chat = model.start_chat(history=api_history[:-1]) # History is everything EXCEPT the last message
        
        user_prompt = api_history[-1]['parts'][0]['text'] # The last message is the prompt

        try:
            response = await chat.send_message_async(user_prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return "К сожалению, произошла ошибка при общении с AI. Попробуйте еще раз."
    
    elif DEEPINFRA_API_KEY:
        # Use DeepInfra as fallback
        try:
            return await get_deepinfra_response(character, history)
        except Exception as e:
            print(f"Error calling DeepInfra API: {e}")
            return "К сожалению, произошла ошибка при общении с AI. Попробуйте еще раз."
    
    else:
        # No API keys available
        return "К сожалению, нет доступных API ключей для генерации ответов. Пожалуйста, настройте GOOGLE_API_KEY или DEEPINFRA_API_KEY."

async def convert_voice_to_opus(voice_file: io.BytesIO) -> io.BytesIO:
    """Converts a voice file (likely in OGG format from Telegram) to OGG with OPUS codec."""
    voice_file.seek(0)
    audio = AudioSegment.from_ogg(voice_file)
    
    # Export to OGG with OPUS codec
    output_buffer = io.BytesIO()
    audio.export(output_buffer, format="ogg", codec="libopus")
    output_buffer.seek(0)
    return output_buffer 

async def get_text_from_speech(voice_file: io.BytesIO) -> str:
    """Transcribes a voice file using Google Speech-to-Text."""
    try:
        client = speech.SpeechAsyncClient()
        
        # The content of the file
        content = voice_file.read()

        audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000, # Telegram voice messages are typically 48kHz
            language_code="ru-RU",
        )

        response = await client.recognize(config=config, audio=audio)

        if response.results and response.results[0].alternatives:
            return response.results[0].alternatives[0].transcript
        else:
            return ""
            
    except Exception as e:
        print(f"Error calling Speech-to-Text API: {e}")
        return "" 

async def generate_image_with_deepinfra(prompt: str) -> BytesIO | None:
    """Generates an image using the Deep Infra FLUX.1-schnell model."""
    if not DEEPINFRA_API_KEY:
        print("Error: DEEPINFRA_API_KEY is not set.")
        return None

    url = "https://api.deepinfra.com/v1/inference/black-forest-labs/FLUX-1-schnell"
    headers = {"Authorization": f"bearer {DEEPINFRA_API_KEY}"}
    # The API for this model expects a flat JSON structure.
    payload = {
        "prompt": prompt,
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 25
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            # The API returns a direct link to the generated image.
            image_url = result['output'][0]
            
            async with httpx.AsyncClient() as img_client:
                img_response = await img_client.get(image_url)
                img_response.raise_for_status()
                return BytesIO(img_response.content)

    except httpx.HTTPStatusError as e:
        print(f"Error calling Deep Infra API: {e.response.status_code} {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return None

async def upload_to_telegraph(image_bytes: BytesIO) -> str | None:
    """Uploads image bytes to Telegraph and returns the URL."""
    try:
        image_bytes.seek(0)
        files = {'file': ('image.png', image_bytes, 'image/png')}
        response = requests.post('https://telegra.ph/upload', files=files)
        response.raise_for_status()
        result = response.json()
        if result and isinstance(result, list) and result[0].get('src'):
            return "https://telegra.ph" + result[0]['src']
    except Exception as e:
        print(f"Error uploading to Telegraph: {e}")
    return None 
import google.generativeai as genai
from config import get_settings
import asyncio
import random

settings = get_settings()
genai.configure(api_key=settings.google_api_key)

def get_weather(city: str):
    temp = random.randint(20, 35)
    conditions = random.choice(["Sunny", "Cloudy", "Rainy", "Humid"])
    return {"city": city, "temperature": f"{temp}°C", "condition": conditions}

def get_stock_price(symbol: str):
    price = random.randint(100, 2000)
    change = random.choice(["+1.2%", "-0.5%", "+0.8%", "-2.1%"])
    return {"symbol": symbol.upper(), "price": f"${price}", "change": change}

available_functions = {
    'get_weather': get_weather,
    'get_stock_price': get_stock_price
}

tools = [get_weather, get_stock_price]
model = genai.GenerativeModel(settings.gemini_model, tools=tools)

async def get_streaming_response(history_context, user_message):
    chat = model.start_chat(enable_automatic_function_calling=False)
    
    system_prompt = "You are a helpful AI assistant. Use tools for weather/stocks. Otherwise answer normally."
    full_prompt = f"{system_prompt}\n\nContext:\n{history_context}\n\nUser: {user_message}"
    
    response = await chat.send_message_async(full_prompt)
    part = response.parts[0]
    
    if hasattr(part, 'function_call') and part.function_call:
        fc = part.function_call
        fn_name = fc.name
        fn_args = dict(fc.args)
        
        if fn_name in available_functions:
            tool_result = available_functions[fn_name](**fn_args)
            
            response = await chat.send_message_async(
                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                    name=fn_name,
                    response=tool_result
                )),
                stream=True
            )
            
            async for chunk in response:
                if chunk.parts and hasattr(chunk.parts[0], 'text'):
                    yield chunk.text
        else:
            yield "Error: Unknown tool."
    else:
        if response.parts and hasattr(response.parts[0], 'text'):
            yield response.text
        else:
            yield "I couldn't generate a response."

async def generate_summary(events):
    if not events: return "No conversation."
    
    text = ""
    for e in events:
        if e['event_type'] == 'user_message': text += f"User: {e['content']}\n"
        elif e['event_type'] == 'ai_response': text += f"AI: {e['content']}\n"
            
    summary_model = genai.GenerativeModel(settings.gemini_model)
    res = await summary_model.generate_content_async(f"Summarize in 2 sentences:\n{text}")
    return res.text

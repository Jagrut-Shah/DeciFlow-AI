import sys
import os

sys.path.append(os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

import asyncio
from app.infrastructure.ai.models import LLMConfig
from app.infrastructure.ai.templates import PromptTemplate
from app.infrastructure.ai.vertex_ai import GeminiService

import logging
logging.basicConfig(level=logging.INFO)

async def main():
    print("--- Running Prompt Templating ---")
    template = PromptTemplate("Extract insights for {segment} over {timeframe}.")
    formatted = template.format(segment="B2B Retail", timeframe="Q3")
    print(f"Formatted Prompt: {formatted}")
    
    print("\n--- Running AI Integration with Retry ---")
    llm = GeminiService()
    config = LLMConfig(temperature=0.4)
    
    try:
        response = await llm.generate_response(formatted, config)
        print("\n--- NORMALIZED AI RESPONSE ---")
        print(response.model_dump_json(indent=2))
    except Exception as e:
        print(f"Engine Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

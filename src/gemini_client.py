import asyncio
import json
from google import genai
from google.genai.types import GenerateContentConfig, Part
from typing import List, Dict, Any
import logging
from config import Config

class GeminiClient:
    def __init__(self, config: Config):
        self.config = config
        try:
            self.client = genai.Client(
                vertexai=True,
                project=config.project_id,
                location=config.location
            )
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {str(e)}")
            raise RuntimeError(f"Gemini 客户端初始化失败: {str(e)}")
        

    async def process_single_prompt(self, prompt: Any, retry_count: int = 3) -> Dict[str, Any]:  # 改为 Any
        """处理单个提示"""
        for attempt in range(retry_count):
            try:
                config = GenerateContentConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=8192,
                    response_mime_type=self.config.response_mime_type,
                    response_schema=self.config.response_schema
                    )
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.config.model,
                    contents=prompt,
                    config=config
                )
                return json.loads(response.text)
            except Exception as e:
                if attempt == retry_count - 1:
                    logging.error(f"Failed after {retry_count} attempts: {str(e)}")
                    # return {"error": str(e), "description": "处理失败"}
                    raise
                await asyncio.sleep(1)

    async def process_batch(self, prompts: Any) -> List[Dict[str, Any]]:  # 改为 Any
        """批量处理提示"""
        tasks = [asyncio.create_task(self.process_single_prompt(prompt)) for prompt in prompts]
        return await asyncio.gather(*tasks)
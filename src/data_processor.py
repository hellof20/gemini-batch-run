import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import json
import logging

from config import Config
from gemini_client import GeminiClient
from prompt_processor import PromptProcessor

class DataProcessor:
    def __init__(self, config: Config, gemini_client: GeminiClient, prompt_processor: PromptProcessor):
        self.config = config
        self.gemini_client = gemini_client
        self.prompt_processor = prompt_processor
        self.results_file = Path("results.jsonl")

    async def process_chunk(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """处理数据块"""
        try:
            prompts = self.prompt_processor.fill_prompts(df)  # 移除类型注解
            return await self.gemini_client.process_batch(prompts)
        except Exception as e:
            logging.error(f"Error processing chunk: {str(e)}")
            # return [{"error": str(e)} for _ in range(len(df))]
            raise

    async def process_file(self) -> pd.DataFrame:
        """处理整个文件并返回结果DataFrame"""
        total_chunks = sum(1 for _ in pd.read_csv(self.config.filepath, chunksize=self.config.chunk_size))
        all_results = []
        
        # 读取原始数据
        original_df = pd.read_csv(self.config.filepath)
        
        for chunk_idx, df in enumerate(pd.read_csv(self.config.filepath, chunksize=self.config.chunk_size), 1):
            # logging.info(f"Processing chunk {chunk_idx}/{total_chunks}")
            results = await self.process_chunk(df)
            all_results.extend(results)
            
            progress = (chunk_idx / total_chunks) * 100
            logging.info(f"Progress: {progress:.2f}%")
        
        # 将结果转换为DataFrame并与原始数据合并
        results_df = pd.DataFrame(all_results)
        final_df = pd.concat([original_df, results_df], axis=1)
        
        return final_df
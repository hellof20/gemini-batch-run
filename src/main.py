# main.py
import asyncio
from dotenv import load_dotenv
import logging
import time,os
from config import Config
from gemini_client import GeminiClient
from prompt_processor import PromptProcessor
from data_processor import DataProcessor
from pathlib import Path


class CustomFilter(logging.Filter):
    def filter(self, record):
        # 返回 False 表示过滤掉该日志
        return "AFC is enabled with max remote calls" not in record.msg

async def main():
    try:
        # 初始化配置
        config = Config.from_env()
        config.validate()
        
        # 设置日志文件路径
        log_path = Path(config.data_folder) / "app.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        # 添加自定义过滤器到根日志记录器
        logging.getLogger().addFilter(CustomFilter())
        
        # 初始化各个组件
        gemini_client = GeminiClient(config)
        prompt_processor = PromptProcessor(config.prompts_template_file)
        data_processor = DataProcessor(config, gemini_client, prompt_processor)
        
        # 处理数据
        start_time = time.time()
        result_df = await data_processor.process_file()
        
        # 保存处理结果
        result_path = Path(config.data_folder) / "result.csv"
        result_df.to_csv(result_path, index=False)
        
        end_time = time.time()
        logging.info(f"Processing completed in {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
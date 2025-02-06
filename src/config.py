from pathlib import Path
import json
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Config:
    project_id: str
    location: str
    model: str
    temperature: float
    filepath: Path
    chunk_size: int
    data_folder: Path
    prompts_template_file: Path
    response_mime_type: str = "text/plain"
    response_schema: Dict[str, Any] = None # set default is None


    @classmethod
    def from_env(cls):
        """从环境变量创建配置"""
        response_mime_type_env = os.getenv("RESPONSE_MIME_TYPE")
        response_schema_file = os.getenv("RESPONSE_SCHEMA_FILE")
        
        # 从文件加载 schema
        schema = None
        if response_schema_file:
            schema_path = Path(response_schema_file)
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
        
        return cls(
            project_id=os.getenv("PROJECT_ID"),
            location=os.getenv("LOCATION"),
            model=os.getenv("MODEL"),
            data_folder=Path(os.getenv("DATA_FOLDER")),
            temperature=float(os.getenv("TEMPERATURE")),
            filepath=Path(os.getenv("DATA_FILEPATH")),
            chunk_size=int(os.getenv("ChunkSize")),
            prompts_template_file=Path(os.getenv("PROMPTS_TEMPLATE_FILE")),
            response_mime_type = response_mime_type_env if response_mime_type_env else "text/plain",
            response_schema=schema
        )

    def validate(self):
        """验证配置"""
        if not self.filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {self.filepath}")
        if not self.prompts_template_file.exists():
            raise FileNotFoundError(f"Template file not found: {self.prompts_template_file}")
        
        # 添加 schema 文件检查
        schema_file = os.getenv("RESPONSE_SCHEMA_FILE")
        if schema_file and not Path(schema_file).exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
            
        if self.chunk_size <= 0:
            raise ValueError("ChunkSize must be positive")
        if not 0 <= self.temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1")
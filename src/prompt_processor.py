# prompt_processor.py
from pathlib import Path
import re
import pandas as pd
from google.genai.types import Part
from typing import List, Union
import logging

class PromptProcessor:
    def __init__(self, template_file: Path):
        self.template = self.load_template(template_file)

    @staticmethod
    def load_template(template: Union[str,Path]) -> List[Part]:
        """加载提示词模板，支持多行文本或文件"""
        parts = []
        with open(template, 'r', encoding='utf-8') as f:
            template_string = f.read()
        
        lines = template_string.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue  # 跳过空行

            match_file = re.match(r'^FILE: (.*?),(.*?)$', line)
            if match_file:
                file_uri, mime_type = match_file.groups()
                parts.append(Part.from_uri(file_uri=file_uri.strip(), mime_type=mime_type.strip()))
            else:
                parts.append(Part.from_text(text=line))
        return parts

    def fill_prompts(self, df: pd.DataFrame) -> List[List[Part]]:
        """填充提示词"""
        try:
            all_prompts = []
            for _, row in df.iterrows():
                filled_prompts = []
                for p in self.template:
                    if hasattr(p, 'text') and p.text is not None:
                        filled_text = p.text.format(**row)
                        filled_prompts.append(Part.from_text(text=filled_text))
                    elif hasattr(p, 'file_data') and p.file_data is not None:
                        filled_uri = str(p.file_data.file_uri).format(**row)
                        filled_mime = str(p.file_data.mime_type).format(**row)
                        filled_prompts.append(Part.from_uri(
                            file_uri=filled_uri,
                            mime_type=filled_mime
                        ))
                all_prompts.append(filled_prompts)
            return all_prompts
        except Exception as e:
            logging.error(f"Error filling prompts: {str(e)}")
            raise
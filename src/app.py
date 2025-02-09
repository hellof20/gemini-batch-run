import streamlit as st
import os,time
from pathlib import Path
import json
from dotenv import load_dotenv
import pandas as pd
import subprocess
import uuid
from datetime import datetime


def save_env_file(env_data):
    """保存.env文件"""
    folder_path = Path(env_data.get('DATA_FOLDER', ''))
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)
    
    env_path = folder_path / ".env"
    with open(env_path, 'w') as f:
        for key, value in env_data.items():
            f.write(f"{key}={value}\n")
    load_dotenv(env_path, override=True)

def read_log_file(log_path):
    """读取日志文件内容"""
    try:
        with open(log_path, 'r') as f:
            return f.read()
    except Exception:
        return ""

def main():
    st.title("LLM应用测试")
    
    with st.expander("环境配置", expanded=True):
        # Google Cloud 配置
        st.subheader("Google Cloud 配置")
        project_id = st.text_input("Project ID", "")
        location = st.text_input("Location", "")
        
        # 模型参数配置
        st.subheader("模型参数")
        model = st.selectbox(
            "Model",
            [
                "gemini-2.0-flash-001",
                "gemini-2.0-flash-lite-preview-02-05",
                "gemini-2.0-pro-exp-02-05",
                "gemini-1.5-pro-002",
                "gemini-1.5-flash-002"
            ]
        )
        temperature = st.slider("Temperature", 0.0, 1.0,0.8)
        chunk_size = st.number_input("Chunk Size", 1, 100,10)

    # 显示文件内容
    with st.expander("数据配置", expanded=True):
        st.subheader("测试数据文件")
        uploaded_data = st.file_uploader("上传数据文件", type=['csv'])
        if uploaded_data:
            df = pd.read_csv(uploaded_data)
            st.dataframe(df)
        
        st.subheader("提示词模板")
        uploaded_prompt = st.file_uploader("上传提示词模板", type=['txt'])
        if uploaded_prompt:
            prompt_content = uploaded_prompt.getvalue().decode('utf-8')
            edited_prompt = st.text_area("提示词内容", prompt_content, height=300)
        
        st.subheader("响应模式")
        uploaded_schema = st.file_uploader("上传响应模式", type=['json'])
        if uploaded_schema:
            schema_content = uploaded_schema.getvalue().decode('utf-8')
            edited_schema = st.text_area("响应模式内容", schema_content, height=300)

    # 提交按钮
    if st.button("提交并处理"):
        if not (project_id and location and model and uploaded_data):
            st.error("请填写必要的配置信息并上传数据文件！")
            return

        try:
            # 创建新的数据文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_path = Path(f"data_{timestamp}_{str(uuid.uuid4())[:8]}")
            folder_path.mkdir(parents=True, exist_ok=True)

            # 保存数据文件
            data_path = folder_path / "data.csv"
            data_path.write_bytes(uploaded_data.getvalue())

            # 保存提示词模板
            prompt_path = folder_path / "prompt.txt"
            prompt_path.write_text(edited_prompt, encoding='utf-8')

            # 保存响应模式
            schema_path = folder_path / "schema.json"
            schema_path.write_text(edited_schema, encoding='utf-8')

            # 保存环境变量
            new_env_data = {
                "PROJECT_ID": project_id,
                "LOCATION": location,
                "MODEL": model,
                "TEMPERATURE": str(temperature),
                "ChunkSize": str(chunk_size),
                "DATA_FOLDER": folder_path,
                "DATA_FILEPATH": data_path,
                "PROMPTS_TEMPLATE_FILE": prompt_path,
                "RESPONSE_MIME_TYPE": "application/json",
                "RESPONSE_SCHEMA_FILE": schema_path
            }
            save_env_file(new_env_data)
    
            # 运行处理脚本
            st.info("开始处理数据...")
            
            # 创建进度条
            progress_placeholder = st.empty()
            log_placeholder = st.empty()
            
            # 运行处理脚本
            process = subprocess.Popen(
                ["python", "src/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 监控日志文件
            log_path = folder_path / "app.log"
            
            while True:
                # 检查进程是否结束
                return_code = process.poll()
                
                # 读取并显示日志
                log_content = read_log_file(log_path)
                if log_content:
                    log_placeholder.code(log_content)
                
                if return_code is not None:
                    stdout, stderr = process.communicate()
                    if return_code != 0:
                        st.error(f"处理失败：{stderr}")
                        return
                    break
                    
                time.sleep(1)
            
            # 处理成功的情况
            st.success("数据处理完成！")
            
            # 读取并显示结果
            result_path = folder_path / "result.csv"
            if result_path.exists():
                result_df = pd.read_csv(result_path)
                st.subheader("处理结果预览")
                st.dataframe(result_df)
        
                # 提供清空按钮
                if st.button("清空处理结果"):
                    try:
                        import shutil
                        shutil.rmtree(folder_path)
                        st.success("处理结果已清空！")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"清空失败：{str(e)}")
            else:
                st.error(f"处理失败：{stderr}")
    
        except Exception as e:
            st.error(f"发生错误：{str(e)}")

if __name__ == "__main__":
    main()
# Gemini Batch Processing Application

这是一个基于 Google Gemini API 的批量处理应用程序，提供了一个 Streamlit Web 界面来并行处理大规模数据。

## 功能特点

- 支持批量处理大规模数据
- 提供友好的 Web 界面进行配置和操作
- 支持自定义提示词模板
- 支持自定义响应模式（Schema）
- 实时显示处理进度和日志
- 异步处理提高性能

## 环境要求

- Python 3.10+
- Google Cloud 项目访问权限

## 使用方法
1. 启动应用：
```bash
streamlit run src/app.py
 ```

2. 在 Web 界面配置以下内容：
- Google Cloud 项目配置
- 模型参数设置
- 上传数据文件（CSV 格式）
- 配置提示词模板
- 设置响应模式（Schema）
3. 点击"提交并处理"开始处理

## 配置说明
### 参数配置
- PROJECT_ID : Google Cloud 项目 ID
- LOCATION : API 调用位置
- MODEL : Gemini 模型名称
- TEMPERATURE : 生成温度（0-1）
- ChunkSize : 批处理大小

### 提示词模板
提示词模板支持文本和文件混合格式，使用特定语法：

```plaintext
<Role>
你是图片内容安全审核专家
</Role>

<Task>
审核图片是否涉及哪个类别，并给出归属到该类别的原因

候选类别:
色情
性暗示
血腥
爆炸
政治
武器
恐怖
广告logo
辱骂
</Task>

<requirement>
输出为中文
不包含上述类别则为安全
</requirement>

<output>
1. 输出格式为json
2. 输出category和reason
</output>

FILE: {image_url},image/jpeg
 ```

### 输出Schema
定义你希望输出结果的json格式：

```json
{
    "type": "object",
    "properties": {
        "category": {
            "type": "string"
        },
        "reason": {
            "type": "string"
        }
    }
}
```
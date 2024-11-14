# SRT LLM Translator

## Overview
The SRT LLM Translator is a Python-based tool that translates subtitles from one language to another using large language models. It preserves the original timestamps of the subtitles, making it easy to integrate translated subtitles back into video files.

## Features
- Translates SRT subtitle files to a specified target language.
- Maintains original timestamps for seamless integration.
- Utilizes OpenAI's API for translation.

## Requirements
- Python 3.x
- OpenAI API key
- Required Python packages:
  - `openai`
  - `srt`

## Installation
1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your OpenAI API key and optionally change the default model:
    ```bash
    export OPENAI_API_KEY='your_OpenAI_api_key'
    export OPENAI_MODEL='gpt-4o-mini'
    ```

## Usage
To translate an SRT file, run the following command:

``` bash
python srt_llm_translator.py --target-lang <target_language> --file <source_file.srt>
```

To translate multiple SRT files, run the following command:

``` bash
python srt_llm_translator.py --target-lang <target_language> --folder <path/to/dir>
```

### Parameters
- `--target-lang`: The language code for the target language (e.g., `en` for English, `es` for Spanish).
- `--file`: The path to the source SRT file.
- `--folder`: The path to a directory where your source SRT files are.

## Example

``` bash
python srt_llm_translator.py --target-lang es --file subtitles.srt
```

## Other models

You can use other models by overwritting the following environment variables:

### OpenRouter

``` bash
export OPENAI_API_KEY='your_OpenRouter_api_key'
export OPENAI_MODEL=anthropic/claude-3.5-sonnet
export OPENAI_API_URL=https://openrouter.ai/api/v1
```

### xAI Grok

```bash
export OPENAI_API_KEY='your_xAI_api_key'
export OPENAI_MODEL=grok-beta
export OPENAI_API_URL=https://api.x.ai/v1
```

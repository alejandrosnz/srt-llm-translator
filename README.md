# SRT LLM Translator

## Overview
The SRT LLM Translator translates subtitles from one language to another using large language models. It preserves the original timestamps of the subtitles, making it easy to integrate translated subtitles back into video files.

**Two ways to use this translator:**
1. **[Python Script](#method-1-python-script)** - Command-line tool for local execution
2. **[n8n Workflow](#method-2-n8n-workflow)** - Visual automation workflow for integration pipelines

## Features
- Translates SRT subtitle files to a specified target language.
- Maintains original timestamps for seamless integration.
- Utilizes OpenAI's API for translation.
- Support for multiple LLM providers (OpenAI, Gemini, Grok, OpenRouter)

---

# Method 1: Python Script

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
- `--source-lang`: Optional source language code, defaults to auto-detection if not specified.
- `--file`: The path to the source SRT file.
- `--folder`: The path to a directory where your source SRT files are.
- `--batch-size`: (optional) Number of SRT lines to translate per LLM request (defaults to 50)
- `--debug`: (optional) Enable debug mode

## Example

``` bash
python srt_llm_translator.py --target-lang es --file sample/sample.srt
```

---

# Method 2: n8n Workflow

For those who prefer a visual workflow automation approach, I've migrated this translator to n8n. The n8n workflow provides a user-friendly interface and can be easily integrated into automation pipelines [(more info here)](./n8n_workflow.json).

![n8n SRT Translator Workflow](./n8n/n8n_workflow.png)

### Features of the n8n Workflow:
- Web-based form interface for easy file upload
- Direct file download of translated SRT
- Visual workflow management
- No command-line required

### Getting the n8n Workflow:
You can download and import the complete n8n workflow:

📁 **[Download n8n Workflow](./n8n/n8n_workflow.json)**

### Setup Instructions for n8n:
1. Download the workflow JSON file
2. Import it into your n8n instance
3. Configure your LLM API credentials in the 'Model' node
4. Execute the workflow

The n8n version maintains the functionality of the Python script while providing better visualization and easier integration with other automation tools.

But at the moment, it doesn't not work with multiple files.

---

# Script Configuration Options

## Other models

You can use other models by overwritting the following environment variables:

### OpenRouter

``` bash
export OPENAI_API_URL=https://openrouter.ai/api/v1
export OPENAI_API_KEY='your_OpenRouter_api_key'
export OPENAI_MODEL=meta-llama/llama-3.2-3b-instruct
```

### Google Gemini

```bash
export OPENAI_API_URL=https://generativelanguage.googleapis.com/v1beta/openai
export OPENAI_API_KEY='your_gemini_api_key'
export OPENAI_MODEL=gemini-1.5-flash
```

### xAI Grok

```bash
export OPENAI_API_URL=https://api.x.ai/v1
export OPENAI_API_KEY='your_xAI_api_key'
export OPENAI_MODEL=grok-beta
```

## Cost and Performance

The cost and performance of the translator were tested with xAI's grok-beta model (priced at $5/M token input and $15/M output). With this model, a 1-hour SRT file (approximately 500 phrases) cost around $0.25 and took 6 minutes to process. In contrast, using OpenAI's GPT 4o-mini model (priced at $0.15/M token input and $0.60/M output), the same 1-hour SRT file cost less than $0.01, but took nearly 8 minutes to process.

Due to the poor time performance observed with the initial implementation, I decided to introduce parallelism in the translation process. The results were significant, as shown in the table below:

| Thread count | xAI Grok-beta | OpenAI GPT 4o-mini |
| ------------ | ------------- | ------------------ |
| 1            | 6 min         | 8 min              |
| 10           | 50 sec        | 45 sec             |
| 20           | 30 sec        | 25 sec             |
| 50           | 75 sec        | 12 sec             |

The translation time has been significantly reduced, but Grok was unable to handle the 50 parallel requests. The thread count can be defined using the MAX_CONCURRENT_CALLS environment variable, which I have set to 5 as the default, just to be safe. However, GPT 4o-mini can handle 50 threads without any issues.

NOTE: These tests were conducted prior to batch optimizations. Previously, one language model request was made per SRT line; now, 50 lines are sent per request. This will speed up the translation process and avoid request-per-minute limits.

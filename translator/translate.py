import os
import time

import srt
from openai import OpenAI
from .file_handler import load_srt_file, save_str_file

def translate_subtitles(source_srt_file: str, target_srt_file: str, target_language: str) -> str:
    """
    Translates subtitles in an SRT file to the target language, preserving timestamps.

    Parameters:
    source_srt_file (str): Path to the input SRT file.
    target_srt_file (str): Path to the output SRT file.
    target_language (str): Target language code (e.g., 'es', 'de', 'zh').

    """
    # Configure OpenAI API
    openai = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
    )
    
    # Load subtitle file
    subtitles = load_srt_file(source_srt_file)

    translated_subtitles = []
    for entry in subtitles:
        try:
            response = openai.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": f"Translate the following text to {target_language}. Maintain the same tone and style."
                    },
                    {
                        "role": "user",
                        "content": entry.content
                    }
                ]
            )
            translated_text = response.choices[0].message.content.strip()
            
            translated_subtitles.append(srt.Subtitle(
                index=entry.index,
                start=entry.start,
                end=entry.end,
                content=translated_text
            ))
            
            time.sleep(0.1)  # avoid request limit
        except Exception as e:
            print(f"Error translating entry {entry.index}: {str(e)}")
            translated_subtitles.append(entry)

    # Save translated file
    if translated_subtitles:
        save_str_file(target_srt_file, translated_subtitles)
    else:
        raise Exception("No subtitles to save")

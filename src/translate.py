import os
import asyncio
import json
import re
import time
from typing import List
import srt
from openai import AsyncOpenAI
from .file_handler import load_srt_file, save_str_file


class SubtitleTranslator:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.semaphore = asyncio.Semaphore(int(os.getenv("MAX_CONCURRENT_CALLS", 5)))
        self.llm_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.max_retries = 3
        self.retry_delay = 2

    def chunk_subtitles(self, subtitles: List[srt.Subtitle], batch_size: int):
        for i in range(0, len(subtitles), batch_size):
            yield subtitles[i:i + batch_size]

    def clean_json_text(self, text: str) -> str:
        text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
        match = re.search(r"(\{|\[)", text)
        if match:
            text = text[match.start():]
        return text.strip()

    async def translate_batch(self, batch: List[srt.Subtitle], source_language: str, target_language: str) -> List[srt.Subtitle]:
        async with self.semaphore:
            # Prepare the data to send to the LLM
            batch_data = [
                {
                    "index": sub.index,
                    "text": sub.content
                }
                for sub in batch
            ]

            system_prompt = f"""
                You are a professional subtitle translator.

                Context:
                - You receive a list of subtitle entries with an index and a text.
                - Translate the 'text' from {source_language} to {target_language} accurately.
                - Preserve the tone, meaning, and style.
                - If a line is already in the target language, return it unchanged.
                - If a line is not in {source_language}, but you can infer the language, translate it to {target_language}.
                - Return ONLY a valid JSON array of objects with this structure:

                [
                    {{
                        "index": int,
                        "text": string
                    }},
                    ...
                ]

                Guidelines:
                - Do NOT add or remove entries.
                - Do NOT include anything outside the JSON array.
                # Professional Subtitle Translation System

                ## Role and Objective
                You are an expert subtitle translator specializing in audiovisual content. Your primary task is to translate subtitle entries
                 from the source language '{source_language}' to the target '{target_language}', while maintaining narrative consistency 
                 and resolving linguistic ambiguities through contextual analysis.

                ## Input Format
                You will receive a JSON array containing subtitle entries with:
                - `index`: Sequential identifier for each subtitle line
                - `text`: The subtitle text to be translated

                ## Core Translation Instructions

                ### 1. Contextual Translation Strategy
                - **Use previous lines as context**: Before translating each line, analyze the preceding subtitle entries to understand:
                - Character gender and relationships
                - Narrative context and emotional tone
                - Technical terminology or proper nouns
                - Conversational flow and speaker identity
                - **Resolve ambiguities**: When the source language contains ambiguous elements (gender, formality level, implied subjects),
                 use the established context from previous lines to make consistent choices

                ### 2. Language Detection and Handling
                - If a line is already in {target_language}, return it unchanged
                - If a line is not in the defined source language ({source_language}), but you can infer the language, translate it to {target_language}.
                - If text is empty, whitespace-only, or contains only symbols/numbers, preserve as-is

                ### 3. Translation Quality Standards
                - **Preserve**: Tone, meaning, style, punctuation, and capitalization
                - **Maintain**: Subtitle timing constraints (keep similar length when possible)
                - **Ensure**: Natural flow in the target language
                - **Consider**: Cultural adaptation where necessary for comprehension

                ## Output Requirements

                ### Format
                Return ONLY a valid JSON array with this exact structure:
                ```json
                [
                    {{
                        "index": int,
                        "text": string
                    }},
                ]
                ```

                ### Constraints
                - Do NOT add, remove, or reorder entries
                - Do NOT include explanations, comments, or text outside the JSON
                - Do NOT ask for clarification or additional context
                - Maintain the exact same number of entries as the input

                ## Examples

                ### Input:
                ```json
                [
                    {{"index": 47, "text": "Maria walked into the room."}},
                    {{"index": 48, "text": "She looked tired."}},
                    {{"index": 49, "text": "Good morning, doctor."}}
                ]
                ```

                ### Output (English to Spanish):
                ```json
                [
                    {{"index": 47, "text": "María entró en la habitación."}},
                    {{"index": 48, "text": "Se veía cansada."}},
                    {{"index": 49, "text": "Buenos días, doctora."}}
                ]
                ```

                *Note: In line 49, "doctora" (feminine) is used because the context from previous lines established that Maria is the doctor being addressed.*

                ## Processing Instructions
                1. Read all entries in the batch first
                2. Analyze the contextual flow and character information
                3. Translate each line considering the established context
                4. Ensure consistency across all translations in the batch
                5. Output the complete JSON array
                """

            for attempt in range(1, self.max_retries + 1):
                try:
                    if self.debug:
                        print(f"\n[DEBUG] Sending batch starting at index {batch[0].index}")
                        print(json.dumps(batch_data, ensure_ascii=False, indent=2))

                    response = await self.llm_client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": json.dumps(batch_data, ensure_ascii=False)},
                        ],
                        temperature=0,
                        response_format={"type": "json_object"}
                    )

                    raw_content = response.choices[0].message.content
                    if self.debug:
                        print(f"\n[DEBUG] Raw LLM response:\n{raw_content}")

                    if not raw_content:
                        raise ValueError("Empty response from LLM")

                    translated_batch = json.loads(self.clean_json_text(raw_content))

                    # Combine the translated batch with the original batch
                    result = []
                    index_to_sub = {sub.index: sub for sub in batch}
                    for item in translated_batch:
                        orig_sub = index_to_sub.get(item["index"])
                        if orig_sub is None:
                            # Ignore if the index is not found
                            continue
                        result.append(
                            srt.Subtitle(
                                index=item["index"],
                                start=orig_sub.start,
                                end=orig_sub.end,
                                content=item["text"]
                            )
                        )
                    return result

                except Exception as e:
                    print(f"[Attempt {attempt}] Error translating batch starting at {batch[0].index}: {e}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay * attempt)
                        continue
                    else:
                        print("Max retries reached, returning original batch.")
                        return batch


    async def translate_all(self, subtitles: List[srt.Subtitle], source_language: str, target_language: str, batch_size: int = 50) -> List[srt.Subtitle]:
        translated_subtitles = []
        for batch in self.chunk_subtitles(subtitles, batch_size):
            translated_batch = await self.translate_batch(batch, source_language, target_language)
            translated_subtitles.extend(translated_batch)
        return translated_subtitles


async def translate_subtitles(source_srt_file: str, source_language: str, target_language: str, batch_size: int = 50, debug: bool = False) -> str:
    """
    Translates subtitles in an SRT file to the target language, preserving timestamps.
    Processes multiple translations concurrently while maintaining subtitle order.

    Parameters:
    source_srt_file (str): Path to the input SRT file.
    source_language (str): Source language
    target_language (str): Target language
    batch_size (int): Number of subtitles to translate concurrently
    debug (bool): Enable debug mode
    """
    print(f"Translating the SRT file '{source_srt_file}'")

    # Load the subtitles from the source SRT file
    subtitles = load_srt_file(source_srt_file)

    # Initialize translator and process all subtitles
    translator = SubtitleTranslator(debug=debug)
    translated_subtitles = await translator.translate_all(subtitles, source_language, target_language, batch_size=batch_size)

    # Save the translated subtitles to a new SRT file
    target_srt_file = source_srt_file.replace('.srt', f'.{target_language}.srt')
    if translated_subtitles:
        save_str_file(target_srt_file, translated_subtitles)
    else:
        raise Exception("No subtitles to save")

    # Return the path to the translated SRT file
    print(f"Translated subtitles saved to '{target_srt_file}'")
    return target_srt_file

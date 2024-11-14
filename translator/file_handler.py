import srt
from typing import List

def load_srt_file(file_path: str) -> List[srt.Subtitle]:
    """
    Loads and parses the SRT file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    return list(srt.parse(srt_content))

def save_str_file(output_path: str, subtitles: List[srt.Subtitle]):
    """
    Saves the translated subtitles to an SRT file.
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(srt.compose(subtitles))

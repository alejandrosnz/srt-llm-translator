import argparse

from translator.translate import translate_subtitles

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SRT file translator using LLM.")
    parser.add_argument("--target-lang", type=str, required=True, help="Target language (e.g.: en).")
    parser.add_argument("--file", type=str, required=True, help="Source SRT file path.")
    parser.add_argument("--output", type=str, default="translated.srt", help="Output SRT file path.")
    args = parser.parse_args()

    translate_subtitles(args.file, args.output, args.target_lang)

    print(f"Translated subtitles saved to {args.output}")


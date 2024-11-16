import argparse
import os
import asyncio

from src.translate import translate_subtitles

async def main():
    parser = argparse.ArgumentParser(description="SRT file translator using LLM.")
    parser.add_argument("--target-lang", type=str, required=True, help="Target language (e.g.: en).")
    parser.add_argument("--file", type=str, help="Source SRT file path.")
    parser.add_argument("--folder", type=str, help="Source folder of SRT files.")
    args = parser.parse_args()

    if args.file and args.folder:
        raise ValueError("Please specify either --file or --folder, not both.")

    if args.folder:
        for filename in os.listdir(args.folder):
            if filename.endswith(".srt"):
                file_path = os.path.join(args.folder, filename)
                await translate_subtitles(file_path, args.target_lang)
    elif args.file:
        await translate_subtitles(args.file, args.target_lang)
    else:
        raise ValueError("The following arguments are required: --file or --folder")

if __name__ == "__main__":
    asyncio.run(main())

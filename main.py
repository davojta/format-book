import os
import click
from pathlib import Path
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from lib.helpers import split_text_into_sections, generate_filename, split_content_by_length, format_text, save_formatted_section, calculate_text_stats

@click.group()
def cli():
    """
    A command-line interface to format text files in a folder and perform statistics analysis.
    """
    pass

def format_chapter_number(number):
    return f"{number:02}"

@cli.command()
@click.argument('input_folder', type=click.Path(exists=True, file_okay=False))
@click.argument('output_folder', type=click.Path())
@click.option('--max-length', default=2000, help='Maximum length for each split section.')
@click.option('--use-chatgpt/--no-chatgpt', default=True, help='Use ChatGPT for formatting text.')
@click.option('--max-workers', default=5, help='Maximum number of parallel workers.')
def format_folder(input_folder, output_folder, max_length, use_chatgpt, max_workers):
    """
    Format all text files in INPUT_FOLDER and save formatted versions to OUTPUT_FOLDER.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Formatting text files in {input_folder} with workers={max_workers} ...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for file_path in input_path.glob('*.txt'):
            sections = split_text_into_sections(file_path)
            for section in sections:
                split_parts = split_content_by_length(section['content'], max_length)
                for part in split_parts:
                    futures.append(
                        executor.submit(format_text, part['content'], use_chatgpt=use_chatgpt)
                    )

        formatted_contents = []
        for future in as_completed(futures):
            formatted_contents.append(future.result())

        index = 0
        for file_path in input_path.glob('*.txt'):
            sections = split_text_into_sections(file_path)
            print(f"Processing {file_path.name}...")
            for section in sections:
                filename = generate_filename(f"{format_chapter_number(section['chapter_number'])} {section['title']}") + ".txt"
                formatted_content = ""
                split_parts = split_content_by_length(section['content'], max_length)
                for _ in split_parts:
                    formatted_content += formatted_contents[index] + "\n"
                    index += 1
                save_formatted_section(output_path / filename, section['chapter_number'], section['title'], formatted_content)
            print(f"End processing {file_path.name}...")

    print(f"Formatted files have been saved to {output_folder}.")

@cli.command()
@click.argument('input_folder', type=click.Path(exists=True, file_okay=False))
@click.argument('output_folder', type=click.Path(exists=True, file_okay=False))
def generate_stats(input_folder, output_folder):
    """
    Generate statistics for text files in INPUT_FOLDER and OUTPUT_FOLDER.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    stats_columns = ["tag", "title", "chars", "words", "sents"]
    dfs = []

    for tag, directory in {"input": input_path, "output": output_path}.items():
        data = []
        for filename in directory.glob('*.txt'):
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read()
                num_chars, num_words, num_sentences = calculate_text_stats(text)
                data.append([tag, filename.name, num_chars, num_words, num_sentences])
        df = pd.DataFrame(data, columns=stats_columns)
        dfs.append(df)

    merged_df = pd.merge(dfs[0], dfs[1], on="title", suffixes=("_input", "_output"))
    merged_df["diff_chars"] = merged_df["chars_input"] - merged_df["chars_output"]
    merged_df["diff_words"] = merged_df["words_input"] - merged_df["words_output"]
    merged_df["diff_sents"] = merged_df["sents_input"] - merged_df["sents_output"]

    print(merged_df.head()[["title", "diff_words", "diff_sents"]])


@cli.command()
@click.argument('input_folder', type=click.Path(exists=True, file_okay=False))
@click.option('--max-words', default=2000, help='Maximum number of words per combined file.')
def combine_chapters(input_folder, max_words):
    """
    Combine chapter files from INPUT_FOLDER into single text files based on the maximum number of words.
    """
    input_path = Path(input_folder)
    combined_content = ""
    current_word_count = 0
    file_count = 1

    output_folder = input_path / "combined"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_path in sorted(input_path.glob('*.txt')):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            word_count = len(content.split())
            if current_word_count + word_count > max_words and combined_content:
                output_filename = f"combined_{file_count}_words_{current_word_count}.txt"
                output_path = output_folder / output_filename
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(combined_content)
                print(f"Combined chapters saved to {output_filename}")
                combined_content = ""
                current_word_count = 0
                file_count += 1

            combined_content += content + "\n"
            current_word_count += word_count

    if combined_content:
        output_filename = f"combined_{file_count}_words_{current_word_count}.txt"
        output_path = output_folder / output_filename
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(combined_content)
        print(f"Combined chapters saved to {output_filename}")

if __name__ == "__main__":
    cli()
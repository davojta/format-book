from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.helpers import (
    split_text_into_sections,
    generate_filename,
    split_content_by_length,
    format_text,
    save_formatted_section,
    calculate_text_stats,
)
from pathlib import Path


def format_chapter_number(number):
    return f"{number:02}"


def format_texts_in_folder(
    input_folder, output_folder, max_length, use_chatgpt, max_workers
):
    """
    Format all text files in INPUT_FOLDER and save formatted versions to OUTPUT_FOLDER.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Formatting text files in {input_folder} with workers={max_workers} ...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for file_path in input_path.glob("*.txt"):
            sections = split_text_into_sections(file_path)
            for section in sections:
                split_parts = split_content_by_length(section["content"], max_length)

                for index, part in enumerate(split_parts):
                    print(
                        f"Submitting tasks for formatting {file_path.name}/p_{index}/{section['title']}..."
                    )
                    futures.append(
                        executor.submit(
                            format_text, part["content"], use_chatgpt=use_chatgpt
                        )
                    )

        formatted_contents = []

        results_in_submit_order = [f.result() for f in futures]
        for result in results_in_submit_order:
            formatted_contents.append(result)

        index = 0
        for file_path in input_path.glob("*.txt"):
            sections = split_text_into_sections(file_path)
            print(f"Processing {file_path.name}...")
            for section in sections:
                filename = (
                    generate_filename(
                        f"{format_chapter_number(section['chapter_number'])} {section['title']}"
                    )
                    + ".txt"
                )
                formatted_content = ""
                split_parts = split_content_by_length(section["content"], max_length)
                for _ in split_parts:
                    formatted_content += formatted_contents[index] + "\n"
                    index += 1
                save_formatted_section(
                    output_path / filename,
                    section["chapter_number"],
                    section["title"],
                    formatted_content,
                )
            print(f"End processing {file_path.name}...")

    print(f"Formatted files have been saved to {output_folder}.")

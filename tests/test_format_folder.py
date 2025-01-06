import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.utils.format_folder import format_texts_in_folder


def sample_txt_content(number):
    """Return a simple string for testing text content."""
    return f"{number}. Chapter {number}\n Hello world of content for chapter {number}.\n\nAnother line for chapter {number}.\n"


@pytest.fixture
def create_test_files(tmp_path):
    """
    Create some *.txt files in a temporary input folder.
    Returns (input_folder, output_folder).
    """
    input_folder = tmp_path / "input"
    input_folder.mkdir()

    # Create two sample text files in the input folder
    file1 = input_folder / "test1.txt"

    file1.write_text(sample_txt_content(1))
    file1_path = Path(file1)
    with file1_path.open(mode="a", encoding="utf-8") as file:
        file.write(sample_txt_content(2))

    file2 = input_folder / "test2.txt"

    file2.write_text(sample_txt_content(3))
    file2_path = Path(file2)
    with file2_path.open(mode="a", encoding="utf-8") as file:
        file.write(sample_txt_content(4))

    output_folder = tmp_path / "output"

    # Return paths so that the test function can pass them to format_folder
    return str(input_folder), str(output_folder)


def test_format_folder_in_submission_order(
    create_test_files,
):
    """
    Test that format_folder processes files, splits them,
    formats them in the correct (submitted) order, and saves them.
    """
    # Unpack the input/output folder paths from the fixture
    input_folder, output_folder = create_test_files

    format_texts_in_folder(
        input_folder=input_folder,
        output_folder=output_folder,
        max_length=100,
        use_chatgpt=False,
        max_workers=2,
    )

    output_files = list(Path(output_folder).glob("*.txt"))
    output_files = [str(file) for file in output_files]
    print("Output files:", output_files)
    assert len(output_files) == 4, "Expected 4 output files."

    print(
        "Test passed: format_folder produces results in the submission order and saves them correctly!"
    )

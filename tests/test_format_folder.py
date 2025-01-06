import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


# Example helper function imports:
# from your_module import format_folder, split_text_into_sections, ...
# For demonstration, we'll assume they are all in a module named `your_module`.
# Adapt as necessary.

# We'll assume the function we want to test looks like:
# def format_folder(input_folder, output_folder, max_length, use_chatgpt, max_workers):
#     ...

@pytest.fixture
def sample_txt_content():
    """Return a simple string for testing text content."""
    return "Chapter 1\nHello World\n\nChapter 2\nAnother line."

@pytest.fixture
def create_test_files(tmp_path, sample_txt_content):
    """
    Create some *.txt files in a temporary input folder.
    Returns (input_folder, output_folder).
    """
    input_folder = tmp_path / "input"
    input_folder.mkdir()

    # Create two sample text files in the input folder
    file1 = input_folder / "test1.txt"
    file1.write_text(sample_txt_content)

    file2 = input_folder / "test2.txt"
    file2.write_text(sample_txt_content)

    output_folder = tmp_path / "output"

    # Return paths so that the test function can pass them to format_folder
    return str(input_folder), str(output_folder)


@patch("src.helpers.split_text_into_sections")
@patch("src.helpers.split_content_by_length")
@patch("src.helpers.format_text")
@patch("src.helpers.generate_filename")
@patch("src.helpers.format_chapter_number")
@patch("src.helpers.save_formatted_section")
def test_format_folder_in_submission_order(
    mock_save_section,
    mock_format_chapter_number,
    mock_generate_filename,
    mock_format_text,
    mock_split_content_by_length,
    mock_split_sections,
    create_test_files
):
    """
    Test that format_folder processes files, splits them,
    formats them in the correct (submitted) order, and saves them.
    """
    # Unpack the input/output folder paths from the fixture
    input_folder, output_folder = create_test_files

    # Configure our mocks to return predictable data.

    # split_text_into_sections returns a list of "sections":
    # Each "section" here is a dict with 'content', 'chapter_number', and 'title'.
    # We'll pretend each file has exactly 2 sections for simplicity.
    mock_split_sections.side_effect = [
        [  # For test1.txt
            {"content": "Section 1 content", "chapter_number": 1, "title": "Intro"},
            {"content": "Section 2 content", "chapter_number": 2, "title": "Main"},
        ],
        [  # For test2.txt
            {"content": "Section A content", "chapter_number": 1, "title": "Alpha"},
            {"content": "Section B content", "chapter_number": 2, "title": "Beta"},
        ],
    ]

    # split_content_by_length might further split each section into parts.
    # Suppose each section is split into 2 parts for demonstration.
    mock_split_content_by_length.side_effect = lambda content, max_len: [
        {"content": content + " - part1"},
        {"content": content + " - part2"},
    ]

    # format_text returns some "formatted" text (we'll just append "-formatted").
    # We'll keep track of call order with a side effect:
    # The side_effect list length should match the total # of parts we produce.
    format_text_calls = []
    def format_text_side_effect(text, use_chatgpt):
        format_text_calls.append(text)   # record the text that’s formatted
        return text + "-formatted"

    mock_format_text.side_effect = format_text_side_effect

    # generate_filename just returns something like "01 Intro".
    # We'll keep it simple here:
    mock_generate_filename.side_effect = lambda base: base.replace(" ", "_")

    # format_chapter_number just returns a string with zero padding. 
    # E.g., chapter_number=1 -> "01"
    mock_format_chapter_number.side_effect = lambda num: f"{num:02d}"

    # Now we call the actual function we want to test
    from main import format_folder  # Import inside the test to avoid circular import
    format_folder(
        input_folder=input_folder,
        output_folder=output_folder,
        max_length=100,
        use_chatgpt=True,
        max_workers=2
    )

    # --- Assertions ---
    # 1) The order of calls to format_text should match submission order:
    #    The sections were returned in a certain order above.
    #    Each section was split into 2 parts, so we expect 2 calls per section.
    # Combined:
    #  - For test1.txt: "Section 1 content - part1", "Section 1 content - part2",
    #                   "Section 2 content - part1", "Section 2 content - part2"
    #  - For test2.txt: "Section A content - part1", ...
    expected_call_order = [
        "Section 1 content - part1",
        "Section 1 content - part2",
        "Section 2 content - part1",
        "Section 2 content - part2",
        "Section A content - part1",
        "Section A content - part2",
        "Section B content - part1",
        "Section B content - part2",
    ]
    assert format_text_calls == expected_call_order, (
        "Expected format_text to be called in the submitted order for each section."
    )

    # 2) Check that save_formatted_section was called the correct number of times.
    # Each file has 2 sections, so total sections = 4.
    assert mock_save_section.call_count == 4, (
        f"Expected save_formatted_section to be called 4 times, got {mock_save_section.call_count}"
    )

    # 3) Optionally verify the arguments with which save_formatted_section was called.
    # Each call should have a path, a chapter_number, a title, and the combined formatted content.
    # This combined content should be the two "formatted" parts with a newline in between.
    calls = mock_save_section.call_args_list
    # For test1.txt, section 1 (chapter_number=1, title='Intro'):
    # For test1.txt, section 2 (chapter_number=2, title='Main'):
    # For test2.txt, section 1 (chapter_number=1, title='Alpha'):
    # For test2.txt, section 2 (chapter_number=2, title='Beta'):

    # Example check on the first call:
    first_call_args, first_call_kwargs = calls[0]  # positional args, keyword args
    # Ensure path contains the expected file name:
    # For example, we expect something like "01_Intro.txt"
    assert "01_Intro.txt" in str(first_call_args[0]), "Unexpected filename for the first section."
    # Check the chapter_number, title, and formatted content
    assert first_call_args[1] == 1, "Unexpected chapter number for the first section."
    assert first_call_args[2] == "Intro", "Unexpected title for the first section."
    # The content should be the two parts appended, with "-formatted" and a newline between them.
    # i.e., "Section 1 content - part1-formatted\nSection 1 content - part2-formatted\n"
    expected_content = (
        "Section 1 content - part1-formatted\n"
        "Section 1 content - part2-formatted\n"
    )
    assert first_call_args[3] == expected_content, "Unexpected combined content for the first section."

    # More checks can be added as needed.

    # If you want to verify the actual files, you could check what was written
    # to the output directory. However, since we’ve mocked `save_formatted_section`,
    # we’d only see that data in the mock, not in the file system.

    print("Test passed: format_folder produces results in the submission order and saves them correctly!")

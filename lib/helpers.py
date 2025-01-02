import re
import json
from openai import OpenAI

import os
import pandas as pd
import re

API_KEY = "sk-proj-"
client = OpenAI(api_key=API_KEY)

formatted_directory = "/Users/dzianissheka/projects/dev/study/nlp_tools/format-book/_temp/formatted_chapters_mini/"

if not os.path.exists(formatted_directory):
    os.makedirs(formatted_directory)



def get_stat_for_text(text):
    num_characters = len(text)
    num_words = len(text.split())
    num_sentences = len(re.split(r'[.!?]', text)) - 1

    return {
        'characters': num_characters,
        'words': num_words,
        'sentences': num_sentences,
    }


def split_text_into_sections(file_path):
    # Read the text from the file
    with open(file_path, 'r') as file:
        text = file.read()
    
    # Regular expression to match sections
    pattern = r"(\d+)\.\s*([^\n]+)\n(.*?)(?=\n\d+\.|$)"
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Create a dictionary to store the sections
    sections = []
    for match in matches:
        chapter_number = match[0].strip()
        title = match[1].strip()
        content = match[2].strip()

        num_characters = len(content)
        num_words = len(content.split())
        num_sentences = len(re.split(r'[.!?]', content)) - 1

        sections.append({
            "chapter_number": int(chapter_number),
            "title": title,
            "content": content,
            'characters': num_characters,
            'words': num_words,
            'sentences': num_sentences,
        })
    
    return sections


# Function to split a section by length, ensuring splits occur at sentence boundaries
def split_content_by_length(content, max_length):
    # Split content into sentences
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    parts = []
    current_section = ""
    for sentence in sentences:
        if len(current_section) + len(sentence) <= max_length:
            if current_section:
                current_section += " "
            current_section += sentence
        else:
            # Add the current section as a new part
            parts.append({
                "content": current_section.strip(),
                "characters": len(current_section.strip()),
                "words": len(current_section.strip().split()),
                "sentences": len(re.split(r'[.!?]', current_section.strip())) - 1
            })
            # Start a new section with the current sentence
            current_section = sentence
    
    if current_section:
        content = current_section.strip()
        parts.append({
            "content": content,
            "characters": len(current_section),
            "words": len(current_section.split()),
            "sentences": len(re.split(r'[.!?]', content)) - 1
        })
    
    return parts


def format_text(text_content, use_chatgpt=True):
    if not use_chatgpt:
        return text_content

    prompt = (
        f"Format the following piece of text separating paragraphs with new line, removing excessing new lines without changing the words of the text"
        f"Return a JSON object with a single field named 'result'. The value of 'result' should contain the formatted text. "
        f"\n\nText: {text_content}"
    )
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant which response always in json format."},
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={ "type": "json_object" }
    )

        # Parse the JSON response and extract the value of "result"
    try:
        # print(f"\n\nText: {completion.choices[0].message.content}")
        response_json = json.loads(completion.choices[0].message.content)
        formatted_text = response_json.get("result", "Could not find 'result' in response.")
    except json.JSONDecodeError:
        formatted_text = "Invalid JSON response."

    return formatted_text


# Function to generate a snake_case filename from the title
def generate_filename(title):
    # Remove special symbols and convert to lowercase snake_case
    filename = re.sub(r'[^a-zA-Z0-9\s]', '', title)  # Remove special characters
    filename = re.sub(r'\s+', '_', filename.strip())  # Replace spaces with underscores
    return filename.lower()


def save_formatted_section(file_path, chapter_number, title, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"{chapter_number}. {title}\n\n{content}")

def calculate_text_stats(text):
    num_chars = len(text)
    words = re.findall(r'\w+', text)
    num_words = len(words)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    num_sentences = len(sentences)
    return num_chars, num_words, num_sentences

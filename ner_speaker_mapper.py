# Does For all the scenario
# import spacy
# import re
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Load spaCy's transformer-based model
# nlp = spacy.load("en_core_web_trf")

# def read_transcript(file_path):
#     """Read the transcript file."""
#     with open(file_path, 'r', encoding='utf-8') as file:
#         return file.read()

# def extract_title_and_name(dialogue):
#     """Extract title and name using regex."""
#     title_pattern = r"\b(Dr\.|Prof\.|Professor|Mr\.|Ms\.|Mrs\.)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\b"
#     match = re.search(title_pattern, dialogue)
    
#     if match:
#         title, name = match.groups()
#         return f"{title} {capitalize_name(name)}"
    
#     return None

# def capitalize_name(name):
#     """Ensure that names are properly capitalized."""
#     return " ".join([word.capitalize() for word in name.split()])

# def preprocess_text(dialogue):
#     """Preprocess the text (lowercasing, removing extra spaces, etc.)."""
#     return re.sub(r'\s+', ' ', dialogue).strip()

# def extract_person_name(dialogue, known_speakers):
#     """Extract person names (with titles) from a single sentence, avoiding misinterpretations."""
#     title_and_name = extract_title_and_name(dialogue)
#     if title_and_name and title_and_name.lower() not in known_speakers:
#         return title_and_name
    
#     doc = nlp(dialogue)
#     person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    
#     filtered_names = []
#     for name in person_entities:
#         if re.search(rf"\b(Thanks|Hello|Hey|Hi)\s+{re.escape(name)}\b", dialogue, re.IGNORECASE):
#             continue
#         if name.lower() not in known_speakers:
#             filtered_names.append(capitalize_name(name))
    
#     return filtered_names[0] if filtered_names else None

# def is_self_introduction(dialogue):
#     """Detect if the dialogue is a self-introduction."""
#     patterns = [
#         r"\b(i|my)\s+(am|m)\s+[a-zA-Z]+",
#         r"\b(my name is)\s+[a-zA-Z]+",
#         r"\b(this is)\s+[a-zA-Z]+",
#         r"\b(i’m)\s+[a-zA-Z]+",
#     ]
    
#     return any(re.search(pattern, dialogue, re.IGNORECASE) for pattern in patterns)

# def map_speakers_with_repeated_names(transcript):
#     """Map speakers dynamically and reuse names for repeated mentions."""
#     lines = transcript.strip().split("\n")
#     speakers_dict = {}
#     updated_lines = []

#     for line in lines:
#         match = re.match(r"(Speaker\d+):\s*(.+)", line)
#         if not match:
#             updated_lines.append(line)
#             continue
        
#         speaker_label, dialogue = match.groups()
#         preprocessed_dialogue = preprocess_text(dialogue)

#         if speaker_label in speakers_dict:
#             speaker_name = speakers_dict[speaker_label]
#         else:
#             speaker_name = extract_person_name(preprocessed_dialogue, [name.lower() for name in speakers_dict.values()])
            
#             if not speaker_name:
#                 speaker_name = f"Unknown_{speaker_label}"
            
#             speakers_dict[speaker_label] = speaker_name

#         updated_lines.append(f"{speaker_name}: {dialogue}")
    
#     return "\n".join(updated_lines)

# def write_output(file_path, content):
#     """Write the updated transcript to a file."""
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(content)

# def main():
#     input_file = os.getenv("INPUT_FILE")
#     output_file = os.getenv("OUTPUT_FILE")

#     if not input_file or not output_file:
#         print("Error: INPUT_FILE or OUTPUT_FILE is not set in the .env file.")
#         return

#     transcript = read_transcript(input_file)
#     updated_transcript = map_speakers_with_repeated_names(transcript)
#     write_output(output_file, updated_transcript)
#     print("\n--- Process Completed ---")

# if __name__ == "__main__":
#     main()




#Our use Case
# #2
import spacy
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Step 1: Read the transcript
def read_transcript(file_path):
    """Read the transcript file."""
    with open(file_path, 'r') as file:
        transcript = file.read()
    print("\n--- Original Transcript ---")
    print(transcript)
    return transcript

# Step 2: Extract named entities
def extract_entities(text):
    """Extract named entities using SpaCy."""
    nlp = spacy.load("en_core_web_sm")  # Load the SpaCy English model
    doc = nlp(text)
    entities = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    print("\n--- Extracted Entities ---")
    print(entities)
    return entities

# Step 3: Filter unique speakers
def filter_speakers(entities):
    """Filter and return unique speaker names."""
    seen = set()
    unique_entities = []
    for entity in entities:
        if entity not in seen and len(entity.split()) > 1:  # Prefer full names
            seen.add(entity)
            unique_entities.append(entity)
    print("\n--- Filtered Unique Speakers ---")
    print(unique_entities)
    return unique_entities

# Step 4: Replace SpeakerX labels
def replace_speaker_labels(transcript, speaker_names):
    """Replace SpeakerX labels with actual speaker names."""
    print("\n--- Speaker Names for Replacement ---")
    print(speaker_names)

    speaker_pattern = re.compile(r"Speaker(\d+)::?")  # Match SpeakerX labels (with optional extra colon)
    
    # Replace labels dynamically with fallback logic
    def replacement(match):
        speaker_index = int(match.group(1)) - 1  # Convert to 0-based index
        if speaker_index < len(speaker_names):
            return f"{speaker_names[speaker_index]}:"
        else:
            return f"Unknown_Speaker{match.group(1)}:"

    updated_transcript = speaker_pattern.sub(replacement, transcript)

    # Post-process for fallback cases and overlaps
    for speaker in speaker_names:
        if f"{speaker}:" in updated_transcript:
            updated_transcript = re.sub(
                fr"(?<!{speaker}){speaker.split()[0]}:",  # Avoid partial matches
                f"{speaker.split()[0]}:",
                updated_transcript,
            )

    print("\n--- Updated Transcript ---")
    print(updated_transcript)
    return updated_transcript

# Step 5: Write output to file
def write_output(file_path, content):
    """Write the updated transcript to a file."""
    with open(file_path, 'w') as file:
        file.write(content)
    print("\n--- Updated Transcript Written to File ---")
    print(f"Output File: {file_path}")

# Step 6: Main function
def main():
    input_file = os.getenv("INPUT_FILE")
    output_file = os.getenv("OUTPUT_FILE")

    # Ensure input and output file paths are set
    if not input_file or not output_file:
        print("Error: INPUT_FILE or OUTPUT_FILE is not set in the .env file.")
        return

    # Read the transcript
    transcript = read_transcript(input_file)

    # Extract entities
    entities = extract_entities(transcript)

    # Filter speaker names
    speakers = filter_speakers(entities)

    # Replace SpeakerX labels
    updated_transcript = replace_speaker_labels(transcript, speakers)

    # Write the updated transcript
    write_output(output_file, updated_transcript)

    print("\n--- Process Completed ---")

if __name__ == "__main__":
    main()



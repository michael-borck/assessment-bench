from docx import Document

def read_word_document(file_path):
    """
    Reads a Word document and returns its text content.
    """
    try:
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading Word document {file_path}: {e}")
        return None

def read_text_file(file_path):
    """
    Reads a text file and returns its content.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_text_file(file_path, content):
    """
    Writes content to a text file.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")

# Additional utility functions can be added here as needed.


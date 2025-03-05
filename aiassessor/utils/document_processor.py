import os
from docx import Document

class DocumentProcessor:
    @staticmethod
    def read_word_document(file_path):
        """
        Read text from a Word document.
        
        Args:
            file_path (str): Path to the Word document
            
        Returns:
            str: Text content of the document
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other document processing errors
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            doc = Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Error reading Word document: {str(e)}")
    
    @staticmethod
    def read_text_file(file_path):
        """
        Read text from a plain text file.
        
        Args:
            file_path (str): Path to the text file
            
        Returns:
            str: Content of the text file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other file reading errors
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")
    
    @staticmethod
    def write_text_file(file_path, content):
        """
        Write text to a file.
        
        Args:
            file_path (str): Path to the text file
            content (str): Content to write
            
        Raises:
            Exception: If file cannot be written
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise Exception(f"Error writing to file: {str(e)}")
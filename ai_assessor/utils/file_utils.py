import os

class FileUtils:
    @staticmethod
    def get_docx_files(folder_path):
        """
        Get all .docx files in a directory.
        
        Args:
            folder_path (str): Path to the folder
            
        Returns:
            list: List of .docx filenames
            
        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Directory not found: {folder_path}")
            
        if not os.path.isdir(folder_path):
            raise ValueError(f"Not a directory: {folder_path}")
            
        return [file for file in os.listdir(folder_path) if file.endswith(".docx")]
    
    @staticmethod
    def ensure_dir_exists(dir_path):
        """
        Create directory if it doesn't exist.
        
        Args:
            dir_path (str): Path to the directory
            
        Returns:
            bool: True if directory exists or was created
            
        Raises:
            Exception: If directory cannot be created
        """
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            return True
        except Exception as e:
            raise Exception(f"Failed to create directory: {str(e)}")
    
    @staticmethod
    def validate_path(path, must_exist=True, must_be_dir=False, must_be_file=False):
        """
        Validate a file or directory path.
        
        Args:
            path (str): Path to validate
            must_exist (bool): Whether the path must exist
            must_be_dir (bool): Whether the path must be a directory
            must_be_file (bool): Whether the path must be a file
            
        Returns:
            bool: True if valid
            
        Raises:
            FileNotFoundError: If path doesn't exist and must_exist is True
            ValueError: If path doesn't meet directory/file requirements
        """
        if must_exist and not os.path.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")
            
        if must_be_dir and not os.path.isdir(path):
            raise ValueError(f"Not a directory: {path}")
            
        if must_be_file and not os.path.isfile(path):
            raise ValueError(f"Not a file: {path}")
            
        return True
import os
import logging
from ..utils.document_processor import DocumentProcessor
from ..utils.file_utils import FileUtils
from ..utils.error_handling import ErrorHandler

class Assessor:
    """
    Core business logic for assessment functionality.
    """
    
    def __init__(self, api_client, config_manager):
        """
        Initialize the assessor.
        
        Args:
            api_client (OpenAIClient): API client for AI interactions
            config_manager (ConfigManager): Configuration manager
        """
        self.api_client = api_client
        self.config = config_manager
        
        # Initialize document processor
        self.doc_processor = DocumentProcessor()
    
    def prepare_system_content(self, system_prompt, support_files_path):
        """
        Prepare system content with support files.
        
        Args:
            system_prompt (str): System prompt text
            support_files_path (str): Path to support files
            
        Returns:
            str: Complete system content
        """
        system_content = f"System: {system_prompt}\n"
        
        # Add support files if path exists
        if support_files_path and os.path.exists(support_files_path):
            try:
                # Get all Word documents in the support folder
                docx_files = FileUtils.get_docx_files(support_files_path)
                
                # Read and append each support file
                for idx, filename in enumerate(docx_files):
                    file_path = os.path.join(support_files_path, filename)
                    file_content = self.doc_processor.read_word_document(file_path)
                    system_content += f"\nSupport File {idx + 1} ({filename}):\n{file_content}\n"
            except Exception as e:
                ErrorHandler.handle_file_error(e, support_files_path)
                
        return system_content
    
    def prepare_user_content(self, user_prompt, submission_path):
        """
        Prepare user content with submission.
        
        Args:
            user_prompt (str): User prompt text
            submission_path (str): Path to submission file
            
        Returns:
            str: Complete user content
        """
        try:
            # Read the student's submission
            student_work = self.doc_processor.read_word_document(submission_path)
            
            # Combine with user prompt
            return f"{user_prompt}\nStudent's Submission:\n{student_work}\n"
        except Exception as e:
            ErrorHandler.handle_file_error(e, submission_path)
            return user_prompt
    
    def grade_submission(self, submission_file, system_prompt, user_prompt, 
                         support_files=None, output_folder=None, model="GPT-4", temperature=0.7):
        """
        Grade a single submission.
        
        Args:
            submission_file (str): Path to submission file
            system_prompt (str): System prompt text
            user_prompt (str): User prompt text
            support_files (str, optional): Path to support files folder
            output_folder (str, optional): Path to output folder
            model (str): Model to use (e.g., "GPT-3", "GPT-4")
            temperature (float): Temperature setting (0-1)
            
        Returns:
            tuple: (success, feedback or error message)
        """
        try:
            # Validate inputs
            FileUtils.validate_path(submission_file, must_exist=True, must_be_file=True)
            
            if output_folder:
                FileUtils.ensure_dir_exists(output_folder)
            
            # Prepare content
            system_content = self.prepare_system_content(system_prompt, support_files)
            user_content = self.prepare_user_content(user_prompt, submission_file)
            
            # Get actual model name from config
            model_name = self.config.get_model_name(model)
            
            # Validate temperature
            if not isinstance(temperature, float) or temperature < 0 or temperature > 1:
                temperature = float(self.config.get_value("API", "Temperature", "0.7"))
            
            # Call the API
            feedback = self.api_client.generate_assessment(
                system_content=system_content,
                user_content=user_content,
                model=model_name,
                temperature=temperature
            )
            
            # Save feedback if output folder is provided
            if output_folder:
                feedback_filename = os.path.basename(submission_file).replace(".docx", "_feedback.txt")
                feedback_path = os.path.join(output_folder, feedback_filename)
                self.doc_processor.write_text_file(feedback_path, feedback)
                
            logging.info(f"Submission graded: {submission_file}")
            return True, feedback
            
        except Exception as e:
            error_msg = ErrorHandler.handle_api_error(e, f"Failed to grade {submission_file}")
            return False, error_msg
    
    def grade_all_submissions(self, submissions_folder, system_prompt, user_prompt, 
                             support_files=None, output_folder=None, model="GPT-4", temperature=0.7):
        """
        Grade all submissions in a folder.
        
        Args:
            submissions_folder (str): Path to submissions folder
            system_prompt (str): System prompt text
            user_prompt (str): User prompt text
            support_files (str, optional): Path to support files folder
            output_folder (str, optional): Path to output folder
            model (str): Model to use (e.g., "GPT-3", "GPT-4")
            temperature (float): Temperature setting (0-1)
            
        Returns:
            tuple: (success_count, fail_count, results)
        """
        try:
            # Validate submissions folder
            FileUtils.validate_path(submissions_folder, must_exist=True, must_be_dir=True)
            
            # Get all Word documents in the submissions folder
            docx_files = FileUtils.get_docx_files(submissions_folder)
            
            # Results storage
            results = {}
            success_count = 0
            fail_count = 0
            
            # Process each submission
            for filename in docx_files:
                submission_path = os.path.join(submissions_folder, filename)
                success, feedback = self.grade_submission(
                    submission_file=submission_path,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    support_files=support_files,
                    output_folder=output_folder,
                    model=model,
                    temperature=temperature
                )
                
                # Track results
                results[filename] = {"success": success, "feedback": feedback}
                if success:
                    success_count += 1
                else:
                    fail_count += 1
            
            logging.info(f"Graded {success_count} submissions successfully, {fail_count} failed")
            return success_count, fail_count, results
            
        except Exception as e:
            error_msg = ErrorHandler.handle_file_error(e, submissions_folder)
            logging.error(error_msg)
            return 0, 0, {"error": error_msg}
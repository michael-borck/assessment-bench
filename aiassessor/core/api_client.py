import openai

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        
    def initialize(self):
        """Initialize the OpenAI API client."""
        openai.api_key = self.api_key
        self.client = openai
        
    def generate_assessment(self, system_content, user_content, model, temperature=0.7, max_tokens=3500):
        """
        Generate an assessment using OpenAI API.
        
        Args:
            system_content (str): The system prompt with any support materials
            user_content (str): The user prompt with student submission
            model (str): The model to use (e.g., "gpt-4-32k-0613")
            temperature (float): The temperature setting (0-1)
            max_tokens (int): Maximum tokens in the response
            
        Returns:
            str: The generated feedback
            
        Raises:
            Exception: If API call fails
        """
        try:
            self.initialize()
            response = self.client.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract the response
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
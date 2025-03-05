# AI Assessor

AI Assessor is a Python application designed to automate the grading of student submissions using OpenAI's API. It now features both a graphical user interface and a command-line interface, making it flexible for various use cases.

## Features

- Multiple interface options:
  - GUI for easy interaction and configuration
  - CLI for automation and scripting
- Grade student submissions (Word documents) using OpenAI's API
- Load and edit system and user prompts
- Include support files for reference during grading
- Configure model parameters (GPT-3/GPT-4, temperature)
- Grade individual or all student submissions
- View student work alongside generated feedback

## Prerequisites

- Python 3.6 or higher
- Required packages (see Installation)

## Installation

### Using Anaconda (Optional)

If you are using Anaconda, you can create a new environment specifically for this project:

1. **Create a New Anaconda Environment**

   ```bash
   conda create --name aiassessor python=3.11
   conda activate aiassessor
   ```

2. **Install Required Packages**

   ```bash
   conda install -c anaconda tk
   conda install -c conda-forge python-docx tqdm python-dotenv
   pip install openai
   ```

### Using Native Python

If you are not using Anaconda, you can set up a virtual environment using Python's built-in `venv`:

1. **Create a Virtual Environment**

   ```bash
   python3 -m venv aiassessor_env
   
   # Activate:
   # Windows: aiassessor_env\Scripts\activate
   # macOS/Linux: source aiassessor_env/bin/activate
   ```

2. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

### Clone the Repository

```bash
git clone https://github.com/yourusername/aiassessor.git
cd aiassessor
```

## Usage

### GUI Interface

Run the main application:

```bash
python main.py
```

1. In the "Configuration and Prompts" tab:
   - Enter your OpenAI API key
   - Set paths for system/user prompts
   - Configure folders for submissions, support files, and outputs
   - Select model and temperature

2. In the "Grading" tab:
   - View the list of submissions
   - Select submissions to grade
   - View submission content and feedback

### Command-line Interface

Run the CLI:

```bash
python aiassessor_cli.py [command] [options]
```

Available commands:

- `config`: Configure application settings
  ```bash
  python aiassessor_cli.py config --list
  python aiassessor_cli.py config --set API.Key your_api_key
  python aiassessor_cli.py config --get Paths.OutputFolder
  ```

- `grade`: Grade submissions
  ```bash
  # Grade a single file
  python aiassessor_cli.py grade --file path/to/submission.docx

  # Grade all files in a directory
  python aiassessor_cli.py grade --dir path/to/submissions
  ```

- `interactive`: Start interactive CLI mode
  ```bash
  python aiassessor_cli.py interactive
  ```

## Contributing

Contributions to AI Assessor are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - email@example.com

Project Link: https://github.com/yourusername/aiassessor
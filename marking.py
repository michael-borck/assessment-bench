import openai
import os
from docx import Document
from utils import read_word_document


def grade_submission(
    api_key,
    system_prompt,
    user_prompt,
    submission_file,
    support_files,
    output_folder,
    model,
    temperature,
):
    """
    Grades a single student's submission using OpenAI's API.
    """
    # Set the API key
    openai.api_key = api_key

    # Read text from each support file
    support_texts = [
        read_word_document(os.path.join(support_files, f))
        for f in os.listdir(support_files)
        if f.endswith(".docx")
    ]

    # Append support texts to the prompt
    system_content = f"System: {system_prompt}"
    for idx, text in enumerate(support_texts):
        system_content += f"\nSupport File {idx + 1}:\n{text}\n"

    # Read the student's submission text
    student_work = read_word_document(submission_file)

    # Prepare the prompt for the OpenAI API
    user_content = f"{user_prompt}\nStudent's Submission:\n{student_work}\n"
    if model == "GPT-3":
        model = "gpt-4-32k-0613"
    else:
        model = "gpt-4-1106-preview"
    # print(f"Using model: {model}\n Temperature: {temperature}")
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            max_tokens=3500,
        )

        # Extract the response
        feedback = response.choices[0].message.content.strip()

        # Save the feedback to a file
        feedback_filename = os.path.basename(submission_file).replace(
            ".docx", "_feedback.txt"
        )
        feedback_file = os.path.join(output_folder.get(), feedback_filename)
        with open(feedback_file, "w") as f:
            f.write(feedback)

        print(f"Feedback generated for {submission_file}")

    except Exception as e:
        print(f"An error occurred while grading {submission_file}: {e}")


def grade_all_submissions(
    api_key, system_prompt, user_prompt, submissions_folder, output_folder
):
    """
    Grades all submissions in the specified folder.
    """
    for filename in os.listdir(submissions_folder):
        if filename.endswith(".docx"):
            submission_file = os.path.join(submissions_folder, filename)
            grade_submission(
                api_key, system_prompt, user_prompt, submission_file, output_folder
            )

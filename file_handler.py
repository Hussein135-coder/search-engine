import os
import win32com.client
from werkzeug.utils import secure_filename

PROJECT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
UPLOAD_FOLDER = os.path.join(PROJECT_DIRECTORY, 'uploads')  # Directory to store uploaded files
ALLOWED_EXTENSIONS = {'doc', 'docx'}  # Allowed file extensions for upload


def allowed_file(filename):
    """
    Checks if the file extension is allowed for upload.

    Args:
    - filename: Name of the file

    Returns:
    - bool: True if the file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_files(request):
    """
    Handles file upload from the request.

    Args:
    - request: HTTP request containing files

    Returns:
    - list: Paths of the uploaded files
    """
    uploaded_files = request.files.getlist('files')
    file_paths = []
    temp_directory = UPLOAD_FOLDER  # Temporary directory to store uploaded files

    # Create the temporary directory if it doesn't exist
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)

    # Process each uploaded file
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_directory, filename)
            file.save(file_path)
            file_paths.append(file_path)

    return file_paths


def convert_to_docx(file_paths):
    converted_paths = []
    word = None  # Initialize word variable outside the try block
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                print(f"Converting file: {file_path}")
                base_name = os.path.splitext(os.path.basename(file_path))[0]

                # Create a new path for the converted DOCX file
                docx_filename = f"{base_name}.docx"
                docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)

                # Load the existing DOC file using pywin32 and save it as DOCX
                word = win32com.client.Dispatch("Word.Application")
                doc = word.Documents.Open(file_path)
                doc.SaveAs(docx_path, 12)  # Save as DOCX format (value 12)
                doc.Close()
                converted_paths.append(docx_path)
                print(f"Converted file path: {docx_path}")

                # Remove the original DOC file after successful conversion
                os.remove(file_path)
                print(f"Removed original DOC file: {file_path}")
            else:
                print(f"File not found at '{file_path}'")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error converting file '{os.path.abspath(file_path)}' to DOCX: {e}")
        finally:
            if word:
                word.Quit()  # Ensure Word is closed even if an exception occurs
                word = None  # Reset word variable to None after quitting Word

    return converted_paths  # Return paths of all successfully converted files

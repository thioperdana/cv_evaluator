import PyPDF2
import docx
import pandas as pd
import os
import tempfile

def read_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def read_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None

def read_excel(file_path):
    """Extract text from Excel file"""
    try:
        df = pd.read_excel(file_path)
        return df.to_string()
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return None

def read_document(file, file_type=None):
    """Read document based on file type"""
    if file_type is None:
        # Try to determine file type from file name
        file_name = file.name.lower()
        if file_name.endswith('.pdf'):
            file_type = 'pdf'
        elif file_name.endswith('.docx'):
            file_type = 'docx'
        elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            file_type = 'excel'
        else:
            return None
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name
    
    # Read file based on type
    if file_type == 'pdf':
        text = read_pdf(temp_file_path)
    elif file_type == 'docx':
        text = read_docx(temp_file_path)
    elif file_type == 'excel':
        text = read_excel(temp_file_path)
    else:
        text = None
    
    # Clean up temporary file
    os.unlink(temp_file_path)
    
    return text
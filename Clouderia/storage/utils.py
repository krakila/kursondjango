import os
import mimetypes
def get_file_type(file):
    if not file:
        return "unknown"

    ext = os.path.splitext(file.name)[-1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
        return "image"
    elif ext in ['.doc', '.docx']:
        return "word"
    elif ext in ['.pdf']:
        return "pdf"
    elif ext in ['.xls', '.xlsx']:
        return "excel"
    elif ext in ['.ppt', '.pptx']:
        return "powerpoint"
    elif ext in ['.zip', '.rar', '.7z']:
        return "archive"
    else:
        return "other"
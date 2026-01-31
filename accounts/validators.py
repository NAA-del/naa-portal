"""
NAA Portal - File Validators
Security validation for file uploads to prevent malicious files
"""

import mimetypes
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions


# File size limits
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_PDF_SIZE = 10 * 1024 * 1024   # 10MB

# Allowed file types with magic bytes
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': b'\xff\xd8\xff',
    'image/png': b'\x89PNG\r\n\x1a\n',
    'image/webp': b'RIFF',
}

ALLOWED_DOCUMENT_TYPES = {
    'application/pdf': b'%PDF-',
}


def validate_image_file(file):
    """
    Validates that uploaded file is a real, safe image.
    
    Security checks:
    1. File size (prevents DoS)
    2. MIME type (prevents wrong file types)
    3. Magic bytes (prevents file spoofing)
    4. Image dimensions (prevents zip bombs)
    
    Args:
        file: Django UploadedFile object
    
    Returns:
        file: Validated file object
    
    Raises:
        ValidationError: If file fails any validation check
    """
    if not file:
        return file
    
    # Check 1: File size
    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            f'Image file too large. Maximum size is {MAX_IMAGE_SIZE / 1024 / 1024}MB.'
        )
    
    # Check 2: MIME type
    mime_type, _ = mimetypes.guess_type(file.name)
    if mime_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(
            'Invalid image type. Only JPEG, PNG, and WebP are allowed.'
        )
    
    # Check 3: Magic bytes (verify actual file content)
    file.seek(0)
    header = file.read(512)
    file.seek(0)  # Reset file pointer
    
    magic_bytes = ALLOWED_IMAGE_TYPES[mime_type]
    if not header.startswith(magic_bytes):
        raise ValidationError(
            f'File appears to be corrupted or not a valid {mime_type}.'
        )
    
    # Check 4: Image dimensions
    try:
        width, height = get_image_dimensions(file)
        if width is None or height is None:
            raise ValidationError('Cannot read image dimensions.')
        
        # Prevent extremely large images (zip bomb protection)
        if width > 10000 or height > 10000:
            raise ValidationError('Image dimensions too large (max 10000x10000).')
    
    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')
    
    return file


def validate_pdf_file(file):
    """
    Validates that uploaded file is a real PDF document.
    
    Security checks:
    1. File size
    2. File extension
    3. PDF signature (magic bytes)
    
    Args:
        file: Django UploadedFile object
    
    Returns:
        file: Validated file object
    
    Raises:
        ValidationError: If file fails validation
    """
    if not file:
        return file
    
    # Check 1: File size
    if file.size > MAX_PDF_SIZE:
        raise ValidationError(
            f'PDF file too large. Maximum size is {MAX_PDF_SIZE / 1024 / 1024}MB.'
        )
    
    # Check 2: File extension
    if not file.name.lower().endswith('.pdf'):
        raise ValidationError('File must have .pdf extension.')
    
    # Check 3: PDF signature
    file.seek(0)
    header = file.read(5)
    file.seek(0)
    
    if not header.startswith(b'%PDF-'):
        raise ValidationError('File is not a valid PDF document.')
    
    return file


def validate_file_name(file):
    """
    Validates filename for security issues.
    
    Prevents:
    1. Path traversal attacks (../, /)
    2. Executable file extensions
    3. Hidden files
    4. Special characters
    5. Excessively long filenames
    
    Args:
        file: Django UploadedFile object
    
    Returns:
        file: Validated file object
    
    Raises:
        ValidationError: If filename contains dangerous patterns
    """
    if not file:
        return file
    
    import re
    import os
    
    filename = os.path.basename(file.name)
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        raise ValidationError('Invalid filename: contains illegal path characters.')
    
    # Check for dangerous file extensions
    dangerous_patterns = [
        r'\.(exe|bat|cmd|sh|php|asp|aspx|jsp|js)$',  # Executables
        r'^\.',  # Hidden files
        r'[<>:"|?*]',  # Windows illegal characters
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            raise ValidationError('Invalid filename: contains unsafe pattern.')
    
    # Check filename length
    if len(filename) > 255:
        raise ValidationError('Filename too long (max 255 characters).')
    
    # Check for null bytes (security issue)
    if '\x00' in filename:
        raise ValidationError('Invalid filename: contains null bytes.')
    
    return file


def validate_certificate_file(file):
    """
    Validates certificate uploads (PDF or images).
    
    Args:
        file: Django UploadedFile object
    
    Returns:
        file: Validated file object
    
    Raises:
        ValidationError: If file fails validation
    """
    if not file:
        return file
    
    # Check file extension
    ext = file.name.lower().split('.')[-1]
    
    if ext == 'pdf':
        return validate_pdf_file(file)
    elif ext in ['jpg', 'jpeg', 'png', 'webp']:
        return validate_image_file(file)
    else:
        raise ValidationError(
            'Invalid file type. Only PDF and images (JPEG, PNG, WebP) are allowed.'
        )
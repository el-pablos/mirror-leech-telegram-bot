"""
Security utilities for input validation and sanitization.
Prevents path traversal, command injection, and other security issues.
"""

from pathlib import Path
from re import sub, match
from os import path as ospath


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to prevent path traversal and invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed length
        
    Returns:
        Sanitized filename safe for filesystem operations
    """
    if not filename:
        return "unnamed_file"
    
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove parent directory references
    filename = filename.replace('..', '')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Remove control characters
    filename = sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Replace multiple spaces with single space
    filename = sub(r'\s+', ' ', filename)
    
    # Limit length
    if len(filename) > max_length:
        name, ext = ospath.splitext(filename)
        if ext:
            max_name_length = max_length - len(ext)
            filename = name[:max_name_length] + ext
        else:
            filename = filename[:max_length]
    
    # Fallback if empty after sanitization
    if not filename:
        return "unnamed_file"
    
    return filename


def sanitize_path(path: str, base_dir: str = None) -> str:
    """
    Sanitize and validate path to prevent directory traversal.
    
    Args:
        path: Path to sanitize
        base_dir: Base directory to restrict access to
        
    Returns:
        Sanitized absolute path
        
    Raises:
        ValueError: If path attempts to escape base_dir
    """
    # Resolve to absolute path
    abs_path = ospath.abspath(path)
    
    # If base_dir specified, ensure path is within it
    if base_dir:
        base_abs = ospath.abspath(base_dir)
        
        # Check if path is within base_dir
        try:
            Path(abs_path).relative_to(base_abs)
        except ValueError:
            raise ValueError(f"Path '{path}' attempts to escape base directory '{base_dir}'")
    
    return abs_path


def validate_url(url: str) -> bool:
    """
    Basic URL validation to prevent injection attacks.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL appears valid, False otherwise
    """
    if not url:
        return False
    
    # Check for common URL schemes
    valid_schemes = ['http://', 'https://', 'ftp://', 'magnet:']
    
    if not any(url.startswith(scheme) for scheme in valid_schemes):
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        'file://',
        'javascript:',
        'data:',
        'vbscript:',
    ]
    
    if any(pattern in url.lower() for pattern in suspicious_patterns):
        return False
    
    return True


def sanitize_command_arg(arg: str) -> str:
    """
    Sanitize command line argument to prevent injection.
    
    Args:
        arg: Command argument to sanitize
        
    Returns:
        Sanitized argument
    """
    # Remove shell metacharacters
    dangerous_chars = ['|', '&', ';', '$', '`', '\n', '\r', '(', ')', '<', '>', '\\']
    
    for char in dangerous_chars:
        arg = arg.replace(char, '')
    
    return arg.strip()


def validate_user_input(input_str: str, max_length: int = 1000, allow_newlines: bool = False) -> str:
    """
    Validate and sanitize general user input.
    
    Args:
        input_str: User input to validate
        max_length: Maximum allowed length
        allow_newlines: Whether to allow newline characters
        
    Returns:
        Sanitized input
        
    Raises:
        ValueError: If input is invalid
    """
    if not input_str:
        return ""
    
    # Check length
    if len(input_str) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")
    
    # Remove null bytes
    input_str = input_str.replace('\x00', '')
    
    # Handle newlines
    if not allow_newlines:
        input_str = input_str.replace('\n', ' ').replace('\r', ' ')
    
    # Remove control characters except newlines if allowed
    if allow_newlines:
        input_str = sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', input_str)
    else:
        input_str = sub(r'[\x00-\x1f\x7f-\x9f]', '', input_str)
    
    return input_str.strip()


def is_safe_extension(filename: str, allowed_extensions: list = None) -> bool:
    """
    Check if file extension is safe/allowed.
    
    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (with or without dot)
        
    Returns:
        True if extension is safe, False otherwise
    """
    if not filename:
        return False
    
    # Get extension
    _, ext = ospath.splitext(filename.lower())
    
    # Remove leading dot if present
    ext = ext.lstrip('.')
    
    # Dangerous extensions that should never be allowed
    dangerous_extensions = [
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js',
        'jar', 'msi', 'app', 'deb', 'rpm', 'dmg', 'pkg', 'sh',
        'bash', 'csh', 'ksh', 'ps1', 'psm1'
    ]
    
    if ext in dangerous_extensions:
        return False
    
    # If allowed list specified, check against it
    if allowed_extensions:
        # Normalize allowed extensions
        allowed = [e.lstrip('.').lower() for e in allowed_extensions]
        return ext in allowed
    
    return True


def sanitize_telegram_text(text: str, max_length: int = 4096) -> str:
    """
    Sanitize text for Telegram messages.
    
    Args:
        text: Text to sanitize
        max_length: Maximum message length (Telegram limit is 4096)
        
    Returns:
        Sanitized text safe for Telegram
    """
    if not text:
        return ""
    
    # Telegram message length limit
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    return text


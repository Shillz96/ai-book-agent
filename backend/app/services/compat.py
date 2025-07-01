"""
Compatibility module for Python 3.13 and other version-specific issues.
"""

import sys

# Handle imghdr removal in Python 3.13
if sys.version_info >= (3, 13):
    # Create a minimal imghdr replacement for Python 3.13+
    class ImgHdrCompat:
        @staticmethod
        def what(file, h=None):
            """
            Simple image type detection for compatibility.
            Returns None if unable to determine type.
            """
            if hasattr(file, 'read'):
                header = file.read(32)
                file.seek(0)  # Reset file position
            elif isinstance(file, (str, bytes)):
                if isinstance(file, str):
                    with open(file, 'rb') as f:
                        header = f.read(32)
                else:
                    header = file[:32]
            else:
                return None
            
            # Basic image format detection
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'png'
            elif header.startswith(b'\xff\xd8\xff'):
                return 'jpeg'
            elif header.startswith(b'GIF8'):
                return 'gif'
            elif header.startswith(b'RIFF') and b'WEBP' in header:
                return 'webp'
            elif header.startswith(b'BM'):
                return 'bmp'
            else:
                return None
    
    # Replace imghdr with our compatibility version
    sys.modules['imghdr'] = ImgHdrCompat()

# Other Python 3.13 compatibility fixes can be added here
def ensure_compatibility():
    """Ensure compatibility across Python versions."""
    pass 
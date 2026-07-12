import base64
from io import BytesIO

import qrcode


def generate_qr_base64(text: str) -> str:
    img = qrcode.make(text)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

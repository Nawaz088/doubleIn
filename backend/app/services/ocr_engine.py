import subprocess
import tempfile
import os
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.receipts import Receipt


async def run_ocr(file_url: str) -> str:
    try:
        import urllib.request
        with urllib.request.urlopen(file_url) as response:
            image_data = response.read()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_data)
            tmp_path = tmp.name

        result = subprocess.run(
            ["tesseract", tmp_path, "stdout", "--psm", "6"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        os.unlink(tmp_path)
        return result.stdout.strip()
    except Exception as e:
        return f"OCR Error: {str(e)}"


async def process_receipt_ocr(
    db: AsyncSession,
    receipt: Receipt,
) -> dict:
    ocr_text = await run_ocr(receipt.file_url)
    receipt.ocr_text = ocr_text

    extracted = {}
    if ocr_text and not ocr_text.startswith("OCR Error"):
        lines = ocr_text.split("\n")
        for line in lines:
            line = line.strip()
            if "$" in line:
                for word in line.split():
                    if word.startswith("$"):
                        try:
                            extracted["amount"] = float(word.replace("$", "").replace(",", ""))
                        except ValueError:
                            pass
            if any(kw in line.lower() for kw in ["total", "amount", "due"]):
                extracted.setdefault("total_line", line)
            if len(line) > 3 and not any(c.isdigit() for c in line[:3]):
                extracted.setdefault("vendor", line)

    receipt.extracted_data = extracted
    receipt.status = "ready"

    await db.commit()
    return extracted

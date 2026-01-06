#!/usr/bin/env python3
"""
PDF -> Compressed JPG images (one image per page)

- Uses PyMuPDF for rendering and Pillow for JPEG compression/resizing
- Supports:
  - Single PDF input OR a folder of PDFs
  - Zoom (quality), JPEG quality, optional max-width resize
  - Optional ZIP output
  - Safe filenames and clean output structure

Install:
  pip install pymupdf pillow

Examples:
  python pdf_to_compressed_images.py --input "input.pdf"
  python pdf_to_compressed_images.py --input "input.pdf" --quality 65 --zoom 2.0 --max-width 1600 --zip
  python pdf_to_compressed_images.py --input "./pdfs" --out "./outputs" --zip
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise SystemExit("Missing dependency: pymupdf\nInstall with: pip install pymupdf") from e

try:
    from PIL import Image
except ImportError as e:
    raise SystemExit("Missing dependency: pillow\nInstall with: pip install pillow") from e


@dataclass
class ConvertOptions:
    zoom: float
    quality: int
    max_width: Optional[int]
    prefix: str
    make_zip: bool
    overwrite: bool


def sanitize_name(s: str, fallback: str = "page") -> str:
    s = s.strip()
    if not s:
        return fallback
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^A-Za-z0-9._-]+", "", s)
    return s or fallback


def iter_pdfs(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() == ".pdf":
            yield input_path
        return

    if input_path.is_dir():
        for p in sorted(input_path.glob("*.pdf")):
            if p.is_file():
                yield p
        return

    raise FileNotFoundError(f"Input not found: {input_path}")


def render_page_to_pil(page: "fitz.Page", zoom: float) -> Image.Image:
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return img


def maybe_resize(img: Image.Image, max_width: Optional[int]) -> Image.Image:
    if not max_width:
        return img
    if img.width <= max_width:
        return img
    new_h = int(img.height * (max_width / img.width))
    return img.resize((max_width, new_h), Image.LANCZOS)


def convert_pdf(pdf_path: Path, out_root: Path, opts: ConvertOptions) -> tuple[Path, list[Path]]:
    """
    Converts one PDF and returns (output_folder, list_of_image_paths).
    Output folder: out_root/<pdf_stem>/
    """
    pdf_stem = sanitize_name(pdf_path.stem, fallback="document")
    out_dir = out_root / pdf_stem

    if out_dir.exists():
        if not opts.overwrite:
            raise FileExistsError(
                f"Output folder already exists: {out_dir}\n"
                f"Use --overwrite to replace it, or choose another --out directory."
            )
        # Clean existing folder
        for item in out_dir.glob("*"):
            if item.is_file():
                item.unlink()
    else:
        out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    total = len(doc)
    if total == 0:
        doc.close()
        raise ValueError(f"No pages found in PDF: {pdf_path}")

    prefix = sanitize_name(opts.prefix, fallback="page")

    image_paths: list[Path] = []
    print(f"\n📄 {pdf_path.name}  ({total} pages)")
    for i in range(total):
        page = doc[i]
        img = render_page_to_pil(page, opts.zoom)
        img = maybe_resize(img, opts.max_width)

        out_file = out_dir / f"{prefix}_{i+1:03d}.jpg"
        img.save(
            out_file,
            format="JPEG",
            quality=int(opts.quality),
            optimize=True,
            progressive=True,
        )
        image_paths.append(out_file)

        # Simple progress
        if total == 1:
            print("  ✅ Page 1/1 saved")
        else:
            print(f"  ✅ Page {i+1}/{total} saved: {out_file.name}")

    doc.close()
    return out_dir, image_paths


def make_zip(zip_path: Path, files_to_zip: list[Path]) -> Path:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files_to_zip:
            zf.write(f, arcname=f.name)
    return zip_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Convert PDF pages to separate compressed JPG images (one per page).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--input", "-i",
        required=True,
        help="Input PDF file path OR a folder containing PDFs",
    )
    p.add_argument(
        "--out", "-o",
        default="output_images",
        help="Output root folder (each PDF gets its own subfolder inside)",
    )
    p.add_argument(
        "--zoom",
        type=float,
        default=2.0,
        help="Render scale (higher = clearer, bigger files). 2.0 is a good balance.",
    )
    p.add_argument(
        "--quality",
        type=int,
        default=65,
        help="JPEG quality (30-95). Lower = smaller, higher = clearer.",
    )
    p.add_argument(
        "--max-width",
        type=int,
        default=1600,
        help="Resize images to this max width for smaller size. Use 0 to disable.",
    )
    p.add_argument(
        "--prefix",
        default="page",
        help="Output image filename prefix (e.g., 'output_page' -> output_page_001.jpg)",
    )
    p.add_argument(
        "--zip",
        action="store_true",
        help="Create a ZIP per PDF (inside the PDF output folder)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output folder if it already exists",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_root = Path(args.out).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    zoom = float(args.zoom)
    quality = int(args.quality)
    if not (30 <= quality <= 95):
        print("❌ --quality must be between 30 and 95", file=sys.stderr)
        return 2

    max_width = int(args.max_width)
    if max_width <= 0:
        max_width = None

    opts = ConvertOptions(
        zoom=zoom,
        quality=quality,
        max_width=max_width,
        prefix=args.prefix,
        make_zip=bool(args.zip),
        overwrite=bool(args.overwrite),
    )

    pdfs = list(iter_pdfs(input_path))
    if not pdfs:
        print("❌ No PDF files found.", file=sys.stderr)
        return 1

    print(f"📁 Output root: {out_root}")
    print(f"⚙️  Settings: zoom={opts.zoom}, quality={opts.quality}, max_width={opts.max_width}, zip={opts.make_zip}")

    for pdf in pdfs:
        try:
            out_dir, image_paths = convert_pdf(pdf, out_root, opts)

            if opts.make_zip:
                zip_path = out_dir / f"{sanitize_name(pdf.stem)}_images.zip"
                make_zip(zip_path, image_paths)
                size_mb = zip_path.stat().st_size / (1024 * 1024)
                print(f"  🧾 ZIP created: {zip_path.name} ({size_mb:.2f} MB)")

        except Exception as e:
            print(f"❌ Failed for {pdf.name}: {e}", file=sys.stderr)

    print("\n✅ Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

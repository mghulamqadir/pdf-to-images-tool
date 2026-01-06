# PDF → Compressed JPGs (One Image Per Page) | Preview + Download (Colab & Python)

Convert any PDF into **separate compressed JPG images** — **1 image per page** — with adjustable quality/compression.

This repo includes:
- ✅ **Notebook (`.ipynb`)**: user-friendly UI for **upload → convert → preview → download ZIP**
- ✅ **Python script (`.py`)**: run locally from terminal to batch convert PDFs

---

## Open in Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/mghulamqadir/pdf-to-images-tool/blob/main/main.ipynb
)

---

## Features

- **Separate JPG per page** (no combining pages)
- Adjustable:
  - **Zoom** (render quality / DPI-like)
  - **JPEG quality** (compression)
  - **Max width resize** (smaller files)
  - **Filename prefix**
- **Preview images first** in notebook
- Download all images as a **ZIP**
- Handles **multiple uploads** + **duplicate filenames** (e.g. `file.pdf`, `file (2).pdf`)


## Requirements

### Notebook (Colab)
No setup needed — Colab installs dependencies in the first cell.

### Local (Python Script)
- Python 3.9+
- Dependencies:
  - `pymupdf`
  - `pillow`

Install:
```bash
pip install pymupdf pillow
````

---

## Usage (Notebook / Colab)

1. Open the notebook in **Google Colab**
2. Run all cells
3. Upload your PDF(s)
4. Adjust settings:

   * Zoom
   * JPG Quality
   * Max Width
   * Prefix
5. Click **Convert & Preview**
6. Preview generated images
7. Click **Download ZIP**

---

## Usage (Python Script)

> Example usage (adjust to match your script args if they differ):

```bash
python main.py \
  --input "file.pdf" \
  --out "output_images" \
  --zoom 2.0 \
  --quality 65 \
  --max-width 1600 \
  --prefix "page"
```

### Recommended Settings

For scanned IDs / forms:

* Zoom: `2.0`
* JPG Quality: `60–70`
* Max Width: `1600` (balanced)

Smaller files:

* Zoom `1.5`, Quality `50–60`, Max Width `1200`

Better clarity:

* Zoom `2.5–3.0`, Quality `70–80`, Max Width `2000` or disable resize

---

## Output

* Images saved as:

  * `prefix_001.jpg`, `prefix_002.jpg`, ...
* ZIP file generated as:

  * `<pdf_name>_images.zip`

---

## Common Issues

### Only 1 file appears after uploading 2 PDFs

If both uploads have the **same filename**, some upload widgets overwrite one entry.
This repo’s notebook version should store them as:

* `file.pdf`
* `file (2).pdf`

### Images look “combined”

They are **separate files** — the notebook preview just displays them one after another.

---

## License

Choose a license and add a `LICENSE` file:

* MIT (simple & popular)
* Apache-2.0
* GPL-3.0

---

## Credits

Built with:

* **PyMuPDF (fitz)** for PDF rendering
* **Pillow** for image compression/resizing
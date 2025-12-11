import io
import base64

import streamlit as st
from PIL import Image

st.set_page_config(page_title="Image to SVG / EPS / PNG", page_icon="🖼️")

st.title("Image → SVG / EPS / PNG Converter")

st.write(
    "Upload a PNG or JPG image and download it as:\n"
    "- PNG (re-saved/normalized)\n"
    "- SVG (image embedded inside SVG)\n"
    "- EPS (bitmap EPS for print/design programs)\n\n"
    "Note: These are **bitmap-based** outputs (no auto vector tracing), so they keep "
    "the original look of photos and complex artwork."
)

uploaded_file = st.file_uploader(
    "Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=False
)

if uploaded_file is not None:
    # ❗ IMPORTANT: read the bytes ONCE and reuse them everywhere
    file_bytes = uploaded_file.read()

    # Open image from bytes for display and conversions
    image = Image.open(io.BytesIO(file_bytes))
    st.subheader("Original image")
    st.image(image, use_column_width=True)

    if st.button("Convert to SVG / EPS / PNG"):
        with st.spinner("Converting…"):

            # ---------- 1) PNG output ----------
            # Normalize to PNG (this also handles JPG uploads)
            png_buffer = io.BytesIO()
            image.save(png_buffer, format="PNG")
            png_bytes = png_buffer.getvalue()

            # ---------- 2) SVG output (embed PNG as base64) ----------
            width, height = image.size
            png_b64 = base64.b64encode(png_bytes).decode("ascii")
            svg_str = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <image href="data:image/png;base64,{png_b64}"
         width="{width}" height="{height}" />
</svg>
'''
            svg_bytes = svg_str.encode("utf-8")

            # ---------- 3) EPS output ----------
            eps_buffer = io.BytesIO()
            image_rgb = image.convert("RGB")  # EPS doesn't support alpha
            image_rgb.save(eps_buffer, format="EPS")
            eps_bytes = eps_buffer.getvalue()

        st.success("Conversion complete!")

        st.subheader("Download your files")

        st.download_button(
            "⬇️ Download PNG",
            data=png_bytes,
            file_name="image.png",
            mime="image/png",
        )

        st.download_button(
            "⬇️ Download SVG",
            data=svg_bytes,
            file_name="image.svg",
            mime="image/svg+xml",
        )

        st.download_button(
            "⬇️ Download EPS",
            data=eps_bytes,
            file_name="image.eps",
            mime="application/postscript",
        )

        st.caption(
            "Tip: Use the SVG or EPS in Illustrator/Inkscape/etc. "
            "For true vector paths from logos only, we could later add an optional "
            "‘vector trace’ mode."
        )

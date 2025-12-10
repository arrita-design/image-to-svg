import io
import base64

import streamlit as st
from PIL import Image

st.set_page_config(page_title="Image to SVG/EPS Converter", page_icon="🖼️")

st.title("Image → SVG / EPS Converter")

st.write(
    "Upload a PNG or JPG image and this app will convert it to SVG and EPS files.\n\n"
    "- The **SVG** contains your image embedded inside an SVG container.\n"
    "- The **EPS** is a bitmap EPS created with Pillow.\n\n"
    "Both work well for many design and print workflows."
)

uploaded_file = st.file_uploader(
    "Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=False
)

if uploaded_file is not None:
    # Open image with Pillow
    image = Image.open(uploaded_file)
    st.subheader("Original image")
    st.image(image, use_column_width=True)

    if st.button("Convert to SVG & EPS"):
        with st.spinner("Converting…"):
            # ---- 1) Ensure image is in a standard mode ----
            # Use RGBA for SVG/PNG; RGB for EPS (no alpha)
            image_rgba = image.convert("RGBA")
            image_rgb = image.convert("RGB")
            width, height = image_rgba.size

            # ---- 2) Build SVG with embedded PNG (base64) ----
            png_buffer = io.BytesIO()
            image_rgba.save(png_buffer, format="PNG")
            png_bytes = png_buffer.getvalue()
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

            # ---- 3) Create EPS using Pillow ----
            eps_buffer = io.BytesIO()
            image_rgb.save(eps_buffer, format="EPS")
            eps_bytes = eps_buffer.getvalue()

        st.success("Conversion complete!")

        st.subheader("Download your files")

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
            "Note: These are **bitmap-based** SVG/EPS files. "
            "They scale well for many uses, but they are not hand-drawn vector paths. "
            "If you want true vectorization for simple logos only, we can add a separate "
            "‘experimental vector mode’ later."
        )

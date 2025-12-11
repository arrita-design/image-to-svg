import io
import base64
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Image Converter", page_icon="🖼️")

st.title("Image → SVG / EPS / PNG Converter (Bitmap Mode)")

uploaded_file = st.file_uploader(
    "Upload PNG or JPG", type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    img_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(img_bytes))

    st.image(image, caption="Original Image", width=500)

    if st.button("Convert"):
        with st.spinner("Converting…"):

            # PNG output
            png_buffer = io.BytesIO()
            image.save(png_buffer, format="PNG")
            png_bytes = png_buffer.getvalue()

            # SVG output (embed PNG inside SVG)
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

            # EPS output
            eps_buffer = io.BytesIO()
            image.convert("RGB").save(eps_buffer, format="EPS")
            eps_bytes = eps_buffer.getvalue()

        st.success("Done!")

        st.download_button("Download PNG", png_bytes, "image.png", "image/png")
        st.download_button("Download SVG", svg_bytes, "image.svg", "image/svg+xml")
        st.download_button("Download EPS", eps_bytes, "image.eps", "application/postscript")

import base64
import io

import streamlit as st

st.set_page_config(page_title="Image to SVG Converter", page_icon="🖼️")

st.title("Image → SVG Converter")

st.write(
    "Upload a PNG or JPG image and this app will put it inside an SVG file so "
    "you can download it.\n\n"
    "Note: This is a **bitmap embedded in SVG**, not hand-drawn vector paths, "
    "so it keeps the original look of photos and artwork."
)

uploaded_file = st.file_uploader(
    "Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=False
)

if uploaded_file is not None:
    # Show preview
    st.subheader("Original image")
    st.image(uploaded_file, use_column_width=True)

    if st.button("Convert to SVG"):
        with st.spinner("Converting…"):
            # Read the raw bytes of the uploaded file
            img_bytes = uploaded_file.read()

            # Guess mime type from upload (e.g. image/png, image/jpeg)
            mime = uploaded_file.type or "image/png"

            # NOTE: We don't know the exact pixel width/height without Pillow,
            # so we use 100% width and height. Programs will size it to fit.
            b64 = base64.b64encode(img_bytes).decode("ascii")

            svg_str = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="100%" height="100%">
  <image href="data:{mime};base64,{b64}"
         width="100%" height="100%" />
</svg>
'''
            svg_bytes = svg_str.encode("utf-8")

        st.success("Conversion complete!")

        st.download_button(
            "⬇️ Download SVG",
            data=svg_bytes,
            file_name="image.svg",
            mime="image/svg+xml",
        )

        st.caption(
            "This SVG keeps your original image as-is, which works well for complex "
            "photos and artwork. For true vector tracing of simple logos only, we can "
            "add a separate experimental mode later."
        )

import io
import tempfile
from pathlib import Path

import streamlit as st
from pixels2svg import pixels2svg
from PIL import Image

st.set_page_config(page_title="Image to SVG/EPS Converter", page_icon="🖼️")

st.title("Image → SVG / EPS Converter")
st.write(
    "Upload a PNG or JPG image and this app will try to convert it into vector SVG, "
    "and also give you an EPS version."
)

uploaded_file = st.file_uploader(
    "Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=False
)

if uploaded_file is not None:
    # Open image with Pillow so we can reuse it later
    image = Image.open(uploaded_file).convert("RGBA")

    st.subheader("Original image")
    st.image(image, use_column_width=True)

    st.subheader("Conversion options")
    color_tolerance = st.slider(
        "Color tolerance (merge similar colors)",
        min_value=1,
        max_value=50,
        value=5,
        help=(
            "Higher values merge more similar colors into single shapes. "
            "If the result looks too blocky, try a lower value."
        ),
    )
    remove_background = st.checkbox(
        "Try to remove solid background",
        value=False,
        help="Useful if your image has a flat background color.",
    )

    if st.button("Convert to SVG & EPS"):
        with st.spinner("Converting… this may take a few seconds for large images"):

            # ---- 1) Save the image to a temp PNG for pixels2svg ----
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_in:
                image.save(tmp_in, format="PNG")
                input_path = tmp_in.name

            tmp_svg_path = input_path + ".svg"

            # ---- 2) Create SVG using pixels2svg (vector) ----
            try:
                pixels2svg(
                    input_path,
                    tmp_svg_path,
                    color_tolerance=color_tolerance,
                    remove_background=remove_background,
                )
            except Exception as e:
                st.error(f"SVG conversion failed: {e}")
                st.stop()

            svg_bytes = Path(tmp_svg_path).read_bytes()

            # ---- 3) Create EPS using Pillow (bitmap inside EPS) ----
            eps_buffer = io.BytesIO()
            try:
                # EPS does not support transparency → convert to RGB
                image_rgb = image.convert("RGB")
                image_rgb.save(eps_buffer, format="EPS")
                eps_bytes = eps_buffer.getvalue()
            except Exception as e:
                st.warning(
                    f"Could not create EPS file: {e}. "
                    "You can still download the SVG."
                )
                eps_bytes = None

        st.success("Conversion complete!")

        st.subheader("Download your files")

        st.download_button(
            "⬇️ Download SVG (vector)",
            data=svg_bytes,
            file_name="vectorized.svg",
            mime="image/svg+xml",
        )

        if eps_bytes is not None:
            st.download_button(
                "⬇️ Download EPS",
                data=eps_bytes,
                file_name="image.eps",
                mime="application/postscript",
            )

        st.caption(
            "Note: SVG is a true vector file (best for editing). "
            "The EPS provided here is a bitmap wrapped in an EPS container, "
            "which many print / design programs accept."
        )

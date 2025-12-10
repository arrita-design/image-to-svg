import tempfile
from pathlib import Path

import streamlit as st
from pixels2svg import pixels2svg
import cairosvg

st.set_page_config(page_title="Image to SVG/EPS Converter", page_icon="🖼️")

st.title("Image → SVG / EPS Converter")
st.write(
    "Upload a PNG or JPG image and this app will try to convert it into vector formats "
    "(SVG and EPS) so you can scale it without losing quality."
)

uploaded_file = st.file_uploader(
    "Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=False
)

if uploaded_file is not None:
    # Show original image preview
    st.subheader("Original image")
    st.image(uploaded_file, use_column_width=True)

    # Let the user tweak a couple of options
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
            # 1) Save uploaded image to a temp file
            suffix = Path(uploaded_file.name).suffix.lower()
            if suffix not in [".png", ".jpg", ".jpeg"]:
                # force a valid extension if something weird comes in
                suffix = ".png"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
                tmp_in.write(uploaded_file.read())
                input_path = tmp_in.name

            # 2) Run pixels2svg to get SVG
            tmp_svg_path = input_path + ".svg"

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

            # 3) Use CairoSVG to convert SVG → EPS (PostScript)
            try:
                # This returns EPS/PS bytes; EPS is widely accepted as PostScript
                eps_bytes = cairosvg.svg2ps(bytestring=svg_bytes)
            except Exception as e:
                st.warning(
                    f"Could not create EPS (PostScript) version: {e}. "
                    "You can still download the SVG file."
                )
                eps_bytes = None

        st.success("Conversion complete!")

        # 4) Download buttons
        st.subheader("Download your vector files")

        st.download_button(
            "⬇️ Download SVG",
            data=svg_bytes,
            file_name="vectorized.svg",
            mime="image/svg+xml",
        )

        if eps_bytes is not None:
            st.download_button(
                "⬇️ Download EPS",
                data=eps_bytes,
                file_name="vectorized.eps",
                mime="application/postscript",
            )

        st.caption(
            "Tip: Results are usually best on logos, icons, and simple artwork. "
            "Photos can look chunky because they’re made from many tiny shapes."
        )

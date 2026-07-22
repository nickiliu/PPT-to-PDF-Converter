import streamlit as st
import tempfile
import subprocess
from pathlib import Path

st.title("幻灯片转PDF_PPT to PDF Converter")

st.write(
    "Upload a PPT or PPTX file and convert it to PDF."
)

uploaded_file = st.file_uploader(
    "Choose a PowerPoint file",
    type=["ppt", "pptx"]
)

if uploaded_file:

    if st.button("Convert"):

        try:

            with tempfile.TemporaryDirectory() as tmpdir:

                ppt_path = Path(tmpdir) / uploaded_file.name

                with open(ppt_path, "wb") as f:
                    f.write(uploaded_file.read())

                subprocess.run(
                    [
                        "soffice",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        str(ppt_path),
                        "--outdir",
                        tmpdir
                    ],
                    check=True
                )

                pdf_path = ppt_path.with_suffix(".pdf")

                if pdf_path.exists():

                    st.success("Conversion completed.")

                    with open(pdf_path, "rb") as f:

                        st.download_button(
                            label="Download PDF",
                            data=f.read(),
                            file_name=pdf_path.name,
                            mime="application/pdf"
                        )
                else:
                    st.error("PDF generation failed.")

        except Exception as e:

            st.error(f"Error: {e}")

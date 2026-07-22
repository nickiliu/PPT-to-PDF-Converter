import streamlit as st
import tempfile
import subprocess
from pathlib import Path
import zipfile
import io

st.title("幻灯片转PDF_PPT to PDF Converter")

st.write(
    "Upload PPT or PPTX files to convert them to PDF."
)

uploaded_files = st.file_uploader(
    "Choose PowerPoint files",
    type=["ppt", "pptx"],
    accept_multiple_files=True
)

if uploaded_files:

    if st.button("Convert All"):

        try:

            with tempfile.TemporaryDirectory() as tmpdir:

                tmppath = Path(tmpdir)

                converted_pdfs = []

                progress_bar = st.progress(0)

                status_text = st.empty()

                total_files = len(uploaded_files)

                for idx, uploaded_file in enumerate(uploaded_files):

                    status_text.text(
                        f"Converting ({idx+1}/{total_files}): "
                        f"{uploaded_file.name}"
                    )

                    ppt_path = tmppath / uploaded_file.name

                    # 使用 getbuffer() 更稳定
                    with open(ppt_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # 转换前已有PDF
                    pdfs_before = set(
                        tmppath.glob("*.pdf")
                    )

                    result = subprocess.run(
                        [
                            "soffice",
                            "--headless",
                            "--convert-to",
                            "pdf",
                            str(ppt_path),
                            "--outdir",
                            str(tmppath)
                        ],
                        capture_output=True,
                        text=True
                    )

                    # 转换后PDF
                    pdfs_after = set(
                        tmppath.glob("*.pdf")
                    )

                    new_pdfs = list(
                        pdfs_after - pdfs_before
                    )

                    if new_pdfs:

                        converted_pdfs.extend(
                            new_pdfs
                        )

                    else:

                        # 尝试再检查一次标准文件名
                        expected_pdf = ppt_path.with_suffix(
                            ".pdf"
                        )

                        if expected_pdf.exists():

                            converted_pdfs.append(
                                expected_pdf
                            )

                        else:

                            st.error(
                                f"Failed to convert: "
                                f"{uploaded_file.name}"
                            )

                            if result.stdout:
                                st.code(
                                    result.stdout
                                )

                            if result.stderr:
                                st.code(
                                    result.stderr
                                )

                    progress_bar.progress(
                        (idx + 1) / total_files
                    )

                status_text.text(
                    "Conversion finished!"
                )

                if converted_pdfs:

                    st.success(
                        f"Successfully converted "
                        f"{len(converted_pdfs)} file(s)."
                    )

                    # 单文件直接下载
                    if len(converted_pdfs) == 1:

                        pdf_file = converted_pdfs[0]

                        with open(
                            pdf_file,
                            "rb"
                        ) as f:

                            st.download_button(
                                label="Download PDF",
                                data=f.read(),
                                file_name=pdf_file.name,
                                mime="application/pdf"
                            )

                    # 多文件ZIP下载
                    else:

                        zip_buffer = io.BytesIO()

                        with zipfile.ZipFile(
                            zip_buffer,
                            "w",
                            zipfile.ZIP_DEFLATED
                        ) as zip_file:

                            for pdf in converted_pdfs:

                                zip_file.write(
                                    pdf,
                                    arcname=pdf.name
                                )

                        st.download_button(
                            label="Download All PDFs (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="converted_pdfs.zip",
                            mime="application/zip"
                        )

                else:

                    st.error(
                        "No PDFs were generated."
                    )

        except Exception as e:

            st.error(
                f"Error occurred during conversion: "
                f"{e}"
            )
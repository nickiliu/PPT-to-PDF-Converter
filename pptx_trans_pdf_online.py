import streamlit as st
import tempfile
import subprocess
from pathlib import Path
import zipfile
import io

st.title("幻灯片转PDF_PPT to PDF Converter")

st.write("Upload PPT or PPTX files to convert them to PDF.")

# 1. 开启多文件上传功能
uploaded_files = st.file_uploader(
    "Choose PowerPoint files",
    type=["ppt", "pptx"],
    accept_multiple_files=True  # <--- 允许选择多个文件
)

if uploaded_files:
    if st.button("Convert All"):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                converted_pdfs = []
                
                # 创建进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 2. 循环处理每一个上传的文件
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Converting ({idx+1}/{len(uploaded_files)}): {uploaded_file.name}...")
                    
                    ppt_path = tmppath / uploaded_file.name
                    
                    # 写入临时文件
                    with open(ppt_path, "wb") as f:
                        f.write(uploaded_file.read())

                    # 调用 LibreOffice (soffice) 进行转换
                    subprocess.run(
                        [
                            "soffice",
                            "--headless",
                            "--convert-to",
                            "pdf",
                            str(ppt_path),
                            "--outdir",
                            str(tmppath)
                        ],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    pdf_path = ppt_path.with_suffix(".pdf")
                    if pdf_path.exists():
                        converted_pdfs.append(pdf_path)
                    
                    # 更新进度条
                    progress_bar.progress((idx + 1) / len(uploaded_files))

                status_text.text("Conversion finished!")

                # 3. 根据转换结果提供下载选项
                if converted_pdfs:
                    st.success(f"Successfully converted {len(converted_pdfs)} file(s)!")

                    # 如果只有一个文件，直接提供 PDF 下载
                    if len(converted_pdfs) == 1:
                        single_pdf = converted_pdfs[0]
                        with open(single_pdf, "rb") as f:
                            st.download_button(
                                label="Download PDF",
                                data=f.read(),
                                file_name=single_pdf.name,
                                mime="application/pdf"
                            )
                    # 如果有多个文件，打包成 ZIP 下载
                    else:
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for pdf in converted_pdfs:
                                zip_file.write(pdf, arcname=pdf.name)
                        
                        st.download_button(
                            label="Download All PDFs (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="converted_pdfs.zip",
                            mime="application/zip"
                        )
                else:
                    st.error("No PDFs were generated successfully.")

        except Exception as e:
            st.error(f"Error occurred during conversion: {e}")
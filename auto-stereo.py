import streamlit as st
import os
import tempfile
import subprocess
import zipfile
import io

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_to_stereo(input_file, output_file):
    try:
        command = [
            "ffmpeg",
            "-i", input_file,
            "-ac", "2",  # 2 channels (stereo)
            "-y",  # Overwrite output file if it exists
            output_file
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Error converting {input_file}: {e.stderr}")
        return False

def process_files(uploaded_files, progress_bar):
    if not check_ffmpeg():
        st.error("FFmpeg is not installed or not found in the system PATH. Please install FFmpeg to use this application.")
        return None

    with tempfile.TemporaryDirectory() as temp_dir:
        converted_files = []
        total_files = len(uploaded_files)

        for i, uploaded_file in enumerate(uploaded_files):
            input_path = os.path.join(temp_dir, uploaded_file.name)
            output_path = os.path.join(temp_dir, f"stereo_{uploaded_file.name}")

            # Save uploaded file
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Convert to stereo
            if convert_to_stereo(input_path, output_path):
                converted_files.append(output_path)

            # Update progress
            progress = (i + 1) / total_files
            progress_bar.progress(progress)

        # Create a zip file containing all converted files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file in converted_files:
                zip_file.write(file, os.path.basename(file))

        return zip_buffer.getvalue()

def main():
    st.title("MP3 to Stereo Converter")

    st.write("이 앱은 여러 MP3 파일을 스테레오로 변환합니다.")

    uploaded_files = st.file_uploader("MP3 파일들을 선택하세요", type=["mp3"], accept_multiple_files=True)

    if uploaded_files:
        if st.button("스테레오로 변환"):
            progress_bar = st.progress(0)
            with st.spinner("파일 변환 중..."):
                zip_data = process_files(uploaded_files, progress_bar)

            if zip_data:
                st.success("모든 파일이 성공적으로 변환되었습니다!")
                st.download_button(
                    label="변환된 파일 다운로드 (ZIP)",
                    data=zip_data,
                    file_name="converted_stereo_files.zip",
                    mime="application/zip"
                )
            else:
                st.error("파일 변환 중 오류가 발생했습니다. 로그를 확인해 주세요.")

if __name__ == "__main__":
    main()
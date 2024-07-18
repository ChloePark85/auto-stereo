import streamlit as st
import os
import tempfile
import zipfile
import io
import subprocess
import urllib.request
import shutil
import lzma
import tarfile

# FFmpeg 다운로드 URL (Linux x64 정적 빌드)
FFMPEG_URL = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

def download_and_extract_ffmpeg():
    with tempfile.TemporaryDirectory() as temp_dir:
        # FFmpeg 다운로드
        ffmpeg_archive = os.path.join(temp_dir, "ffmpeg.tar.xz")
        urllib.request.urlretrieve(FFMPEG_URL, ffmpeg_archive)
        
        # tar.xz 파일 압축 해제
        with lzma.open(ffmpeg_archive) as xz_file:
            with tarfile.open(fileobj=xz_file) as tar_file:
                # FFmpeg 실행 파일만 추출
                ffmpeg_member = next(m for m in tar_file.getmembers() if m.name.endswith('ffmpeg'))
                ffmpeg_member.name = os.path.basename(ffmpeg_member.name)  # 파일 이름만 사용
                tar_file.extract(ffmpeg_member, temp_dir)
        
        # FFmpeg 실행 파일 복사
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg")
        shutil.copy(os.path.join(temp_dir, "ffmpeg"), ffmpeg_path)
        os.chmod(ffmpeg_path, 0o755)  # 실행 권한 부여
    
    return ffmpeg_path

def convert_to_stereo(input_file, output_file, ffmpeg_path):
    try:
        # FFmpeg를 사용하여 MP3를 스테레오 WAV로 변환
        subprocess.run([ffmpeg_path, "-i", input_file, "-ac", "2", "-acodec", "pcm_s16le", "-y", output_file], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Error converting {input_file}: {e.stderr}")
        return False

def process_files(uploaded_files, progress_bar, ffmpeg_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        converted_files = []
        total_files = len(uploaded_files)

        for i, uploaded_file in enumerate(uploaded_files):
            input_path = os.path.join(temp_dir, uploaded_file.name)
            output_filename = os.path.splitext(uploaded_file.name)[0] + '.wav'
            output_path = os.path.join(temp_dir, output_filename)

            # Save uploaded file
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Convert to stereo
            if convert_to_stereo(input_path, output_path, ffmpeg_path):
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
    st.title("MP3 to Stereo WAV Converter")

    st.write("이 앱은 여러 MP3 파일을 스테레오 WAV 파일로 변환합니다.")

    # FFmpeg 다운로드 및 압축 해제
    with st.spinner("FFmpeg 준비 중..."):
        ffmpeg_path = download_and_extract_ffmpeg()
    
    st.success("FFmpeg 준비 완료!")

    uploaded_files = st.file_uploader("MP3 파일들을 선택하세요", type=["mp3"], accept_multiple_files=True)

    if uploaded_files:
        if st.button("스테레오로 변환"):
            progress_bar = st.progress(0)
            with st.spinner("파일 변환 중..."):
                zip_data = process_files(uploaded_files, progress_bar, ffmpeg_path)

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
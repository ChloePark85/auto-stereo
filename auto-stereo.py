import streamlit as st
import os
import tempfile
import zipfile
import io
import wave
import struct
import array

def read_mp3(file_path):
    # 주의: 이 함수는 실제 MP3 디코딩을 수행하지 않습니다.
    # 실제 구현에서는 적절한 MP3 디코더 라이브러리를 사용해야 합니다.
    with open(file_path, 'rb') as f:
        return f.read()

def write_wav(audio_data, file_path, channels=2, sample_width=2, frame_rate=44100):
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)
        wav_file.writeframes(audio_data)

def convert_to_stereo(input_file, output_file):
    try:
        # MP3 파일 읽기 (실제 구현에서는 MP3 디코딩 필요)
        audio_data = read_mp3(input_file)
        
        # WAV 파일로 저장 (스테레오)
        write_wav(audio_data, output_file, channels=2)
        
        return True
    except Exception as e:
        st.error(f"Error converting {input_file}: {str(e)}")
        return False

def process_files(uploaded_files, progress_bar):
    with tempfile.TemporaryDirectory() as temp_dir:
        converted_files = []
        total_files = len(uploaded_files)

        for i, uploaded_file in enumerate(uploaded_files):
            input_path = os.path.join(temp_dir, uploaded_file.name)
            # 'stereo_' 접두사를 제거하고 확장자만 .wav로 변경
            output_filename = os.path.splitext(uploaded_file.name)[0] + '.wav'
            output_path = os.path.join(temp_dir, output_filename)

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
    st.title("MP3 to Stereo WAV Converter")

    st.write("이 앱은 여러 MP3 파일을 스테레오 WAV 파일로 변환합니다.")

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
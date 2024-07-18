# import os
# import subprocess
# from tqdm import tqdm

# def convert_to_stereo(input_file, output_file):
#     try:
#         # FFmpeg 명령어: MP3를 스테레오 WAV로 변환
#         command = [
#             'ffmpeg',
#             '-i', input_file,
#             '-acodec', 'pcm_s16le',  # 16-bit PCM 코덱
#             '-ac', '2',              # 2 채널 (스테레오)
#             '-ar', '44100',          # 샘플레이트 44.1kHz (필요에 따라 조정 가능)
#             '-y',                    # 기존 파일 덮어쓰기
#             output_file
#         ]
        
#         # FFmpeg 실행
#         subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#         return True
#     except subprocess.CalledProcessError as e:
#         print(f"Error converting {input_file}: {str(e)}")
#         return False

# def process_folder(input_folder, output_folder):
#     # 출력 폴더가 없으면 생성
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     # 입력 폴더에서 모든 MP3 파일 찾기
#     mp3_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.mp3')]

#     # 진행 상황을 표시하기 위한 tqdm 사용
#     for mp3_file in tqdm(mp3_files, desc="Converting files"):
#         input_path = os.path.join(input_folder, mp3_file)
#         output_filename = os.path.splitext(mp3_file)[0] + '.wav'
#         output_path = os.path.join(output_folder, output_filename)

#         if convert_to_stereo(input_path, output_path):
#             print(f"Successfully converted: {mp3_file}")
#         else:
#             print(f"Failed to convert: {mp3_file}")

# def main():
#     input_folder = input("Enter the path to the folder containing MP3 files:").strip()
#     output_folder = input("Enter the path to save converted WAV files:").strip()

#     if not os.path.exists(input_folder):
#         print("Input folder does not exist.")
#         return

#     print(f"Converting MP3 files from {input_folder} to stereo WAV files in {output_folder}")
#     process_folder(input_folder, output_folder)
#     print("Conversion process completed.")

# if __name__ == "__main__":
#     main()
import streamlit as st
import os
import tempfile
import subprocess
import zipfile
import io

def convert_to_stereo(input_file, output_file):
    try:
        command = [
            'ffmpeg',
            '-i', input_file,
            '-acodec', 'pcm_s16le',
            '-ac', '2',
            '-ar', '44100',
            '-y',
            output_file
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Error converting {input_file}: {e.stderr}")
        return False

def process_files(uploaded_files):
    with tempfile.TemporaryDirectory() as temp_dir:
        converted_files = []
        
        for uploaded_file in uploaded_files:
            input_path = os.path.join(temp_dir, uploaded_file.name)
            output_filename = os.path.splitext(uploaded_file.name)[0] + '.wav'
            output_path = os.path.join(temp_dir, output_filename)
            
            # Save uploaded file
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Convert to stereo
            if convert_to_stereo(input_path, output_path):
                converted_files.append(output_path)
                st.success(f"Successfully converted: {uploaded_file.name}")
            else:
                st.error(f"Failed to convert: {uploaded_file.name}")
        
        # Create a zip file containing all converted files
        if converted_files:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file in converted_files:
                    zip_file.write(file, os.path.basename(file))
            
            return zip_buffer.getvalue()
        else:
            return None

def main():
    st.title("MP3 to Stereo WAV Converter")
    st.write("Upload your MP3 files and convert them to stereo WAV files.")

    uploaded_files = st.file_uploader("Choose MP3 files", type="mp3", accept_multiple_files=True)

    if uploaded_files:
        if st.button("Convert to Stereo WAV"):
            with st.spinner("Converting files..."):
                zip_data = process_files(uploaded_files)
            
            if zip_data:
                st.success("Conversion completed!")
                st.download_button(
                    label="Download converted files (ZIP)",
                    data=zip_data,
                    file_name="converted_stereo_files.zip",
                    mime="application/zip"
                )
            else:
                st.error("No files were successfully converted.")

if __name__ == "__main__":
    main()
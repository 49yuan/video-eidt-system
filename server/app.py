from flask import Flask, request, jsonify, send_from_directory,send_file
from flask_cors import CORS  # 添加这一行
import whisper
import os
from moviepy import VideoFileClip
import subprocess
import uuid
import shutil

app = Flask(__name__)
CORS(app)  # 启用CORS
# 获取当前文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 设置 UPLOAD_FOLDER 为项目根目录下的 uploads 文件夹
UPLOAD_FOLDER = os.path.join(current_dir, '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True, mode=0o777)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 加载 Whisper 模型
model = whisper.load_model("base").to("cpu")

def convert_audio_format(audio_path, work_dir):
    output_path = os.path.abspath(os.path.join(work_dir, "converted_audio.wav"))
    result = subprocess.run([
        "ffmpeg", "-i", os.path.abspath(audio_path), 
        "-ar", "16000", 
        "-ac", "1", 
        output_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr.decode('utf-8')}")
    return output_path
    
def generate_srt(result):
    srt_lines = []
    for i, segment in enumerate(result["segments"]):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()
        
        # 确保文本以句号结尾，如果没有则添加
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
            
        srt_lines.append(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n")
    return "\n".join(srt_lines)

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")

def format_text_output(result):
    """将Whisper结果格式化为有良好断句的文本"""
    formatted_text = []
    for segment in result["segments"]:
        text = segment["text"].strip()
        
        # 确保每段以句号结尾
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
            
        formatted_text.append(text)
    
    # 每段之间用换行分隔
    return "\n".join(formatted_text)

@app.route('/upload', methods=['POST'])
def upload_video():
    # 为每个请求创建唯一的工作目录
    work_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        if 'file' not in request.files:
            raise ValueError("No file uploaded")

        file = request.files['file']
        if file.filename == '':
            raise ValueError("No file selected")

        # 保存上传的视频文件到工作目录
        video_path = os.path.join(work_dir, "uploaded_video.mp4")
        file.save(video_path)

        # 提取音频到工作目录
        audio_path = os.path.join(work_dir, "extracted_audio.wav")
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        video.close()

        # 转换音频格式到工作目录
        converted_audio_path = convert_audio_format(audio_path, work_dir)

        # 使用 Whisper 转换音频
        result = model.transcribe(converted_audio_path, task="transcribe", word_timestamps=True)
        
        # 生成SRT文件到工作目录
        srt_path = os.path.abspath(os.path.join(work_dir, "subtitle.srt"))
        print("Writing SRT to:", srt_path)  # 添加日志
        with open(srt_path, "w", encoding="utf-8") as f:
            srt_content = generate_srt(result)
            f.write(srt_content)

        # 写入后立即检查
        if not os.path.exists(srt_path):
            raise Exception("SRT file was not created")
        print("SRT file created successfully")

        # 生成正确的下载 URL
        relative_srt_path = os.path.relpath(srt_path, start=app.config['UPLOAD_FOLDER'])
        srt_url = f"/download/{relative_srt_path}"

        return jsonify({
            "text": format_text_output(result),
            "srt_url": srt_url
        })

    except Exception as e:
        # 出错时清理工作目录
        if 'work_dir' in locals() and os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        return jsonify({"error": str(e)}), 500

@app.route('/download/<path:file_path>')
def download_file(file_path):
    try:
        # 将路径中的 URL 编码部分解码
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
            
        # 设置下载完成后自动清理工作目录
        response = send_file(file_path, as_attachment=True)
        
        @response.call_on_close
        def cleanup():
            try:
                work_dir = os.path.dirname(file_path)
                if os.path.exists(work_dir):
                    shutil.rmtree(work_dir)
            except Exception as e:
                print(f"Cleanup error: {e}")
                
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
// src/plugins/ffmpegManager.js
import { createFFmpeg, fetchFile } from '@ffmpeg/ffmpeg';

const ffmpeg = createFFmpeg({ log: true });

// 确保 FFmpeg 加载完成
async function initFFmpeg() {
    await ffmpeg.load();
}

// 提供一个函数来访问 FFmpeg 实例
function getFFmpegInstance() {
    return ffmpeg;
}

export { initFFmpeg, getFFmpegInstance };
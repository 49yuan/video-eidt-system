// src/plugins/installFFmpeg.js
import { initFFmpeg, getFFmpegInstance } from './ffmpegManager'; // 导入 ffmpegManager.js

const installFFmpeg = {
    install(app) {
        // 注册全局 ffmpeg 接口
        const ffmpegIns = {
            init: initFFmpeg,
            instance: getFFmpegInstance()
        };

        // 使用 Hooks
        ffmpegIns.init().then(() => {
            app.config.globalProperties.$ElLoading.visible.value = false;
        }).catch(() => {
            app.config.globalProperties.$ElLoading.visible.value = false;
        });

        app.provide('ffmpeg', ffmpegIns);
        console.log(ffmpegIns);
    }
};

export default installFFmpeg;
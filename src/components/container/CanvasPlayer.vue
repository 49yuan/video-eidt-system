<template>
    <div class="container">
        <!-- 左侧：视频播放器和轨道 -->
        <div class="left-panel">
            <div class="video-container-wrapper" :style="{ backgroundColor: '#000' }">
                <!-- 背景层 -->
                <div v-if="isBackgroundApplied" class="background-layer">
                    <img :src="backgroundPreview" alt="背景" class="background-image">
                </div>

                <!-- 原始视频容器 -->
                <div class="video-container" :style="{ aspectRatio: videoAspectRatio }">
                    <div v-if="!video" class="video-upload-placeholder">
                        <input @change="changFile" type="file" id="uploader" accept="video/*" class="hidden-uploader">
                        <label for="uploader" class="upload-label">
                            <span class="upload-icon">+</span>
                            <span>选择视频文件</span>
                        </label>
                    </div>

                    <video v-else id="screen-video" ref="screenVideo" controls @loadedmetadata="handleVideoLoaded"
                        @error="handleVideoError"></video>

                    <div id="preview-elements" ref="previewElements"></div>
                </div>
            </div>

            <div class="track-container">
                <div class="track">
                    <img v-for="(img, index) in track" :key="index" :src="img" alt="序列帧" draggable="true"
                        @dragstart="dragStart" @dragend="dragEnd">
                </div>
            </div>
        </div>

        <!-- 右侧：视频信息和操作 -->
        <div class="right-panel">
            <el-tabs v-model="activeTab">
                <el-tab-pane label="模板编辑" name="template-edit">
                    <div class="editable-fields">
                        <!-- 动态生成的可编辑字段 -->
                        <div v-for="(field, index) in editableFields" :key="index" class="field-item">
                            <div class="field-header">
                                <label>{{ field.label }}:</label>
                                <input v-model="field.value" class="field-input">
                                <button @click="toggleEditPanel(index)" class="edit-btn">
                                    {{ field.showEditPanel ? '隐藏编辑' : '编辑样式' }}
                                </button>
                            </div>

                            <!-- 编辑面板 - 只在点击编辑时显示 -->
                            <div v-if="field.showEditPanel" class="edit-panel">
                                <div class="style-controls">
                                    <div class="control-group">
                                        <label>字体:</label>
                                        <select v-model="field.style.fontFamily">
                                            <option value="Arial">Arial</option>
                                            <option value="Times New Roman">Times New Roman</option>
                                            <option value="Courier New">Courier New</option>
                                            <option value="Georgia">Georgia</option>
                                            <option value="Verdana">Verdana</option>
                                        </select>
                                    </div>

                                    <div class="control-group">
                                        <label>字体大小:</label>
                                        <input type="range" v-model="field.style.fontSize" min="10" max="72" step="1">
                                        <span>{{ field.style.fontSize }}px</span>
                                    </div>

                                    <div class="control-group">
                                        <label>字体颜色:</label>
                                        <input type="color" v-model="field.style.fontColor">
                                    </div>

                                    <div class="control-group">
                                        <label>背景颜色:</label>
                                        <input type="color" v-model="field.style.backgroundColor">
                                    </div>

                                    <div class="control-group">
                                        <label>X位置:</label>
                                        <input type="range" v-model="field.style.xPosition" min="0" :max="videoWidth"
                                            step="1">
                                        <span>{{ field.style.xPosition }}px</span>
                                    </div>

                                    <div class="control-group">
                                        <label>Y位置:</label>
                                        <input type="range" v-model="field.style.yPosition" min="0"
                                            :max="isBackgroundApplied ? backgroundHeight : videoHeight" step="1">
                                        <span>{{ field.style.yPosition }}px</span>
                                    </div>

                                    <div class="apply-controls">
                                        <button @click="applyStyleToVideo(field)" class="apply-btn">应用到视频</button>
                                        <button @click="removePreviewElement(field.previewElementId)" class="cancel-btn"
                                            v-if="field.previewElementId">取消应用</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="control-panel">
                        <!-- 背景图片上传和预览 -->
                        <div class="upload-preview-group">
                            <div class="file-upload">
                                <input @change="handleBackground" type="file" id="uploaderBackground" accept="image/*">
                                <label for="uploaderBackground">选择背景图片</label>
                            </div>

                            <div v-if="backgroundPreview" class="preview-options">
                                <div class="size-options">
                                    <label>视频尺寸:</label>
                                    <select v-model="videoSizeOption">
                                        <option value="match">匹配图片尺寸</option>
                                        <option value="custom">自定义尺寸</option>
                                    </select>
                                    <div v-if="videoSizeOption === 'custom'" class="custom-size">
                                        <input type="number" v-model="customWidth" placeholder="宽度"
                                            @input="updateCustomSize">
                                        <span>x</span>
                                        <input type="number" v-model="customHeight" placeholder="高度"
                                            @input="updateCustomSize">
                                    </div>
                                </div>
                                <div class="apply-controls">
                                    <button @click.stop="previewBackground" class="preview-btn"
                                        :disabled="!backgroundPreview">
                                        预览效果
                                    </button>
                                    <button @click.stop="removeBackgroundElement" class="cancel-btn"
                                        :disabled="!isBackgroundApplied">
                                        取消应用
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- 水印图片上传和预览 -->
                        <div class="upload-preview-group">
                            <div class="file-upload">
                                <input @change="changImage" type="file" id="uploaderImage" accept="image/*">
                                <label for="uploaderImage">添加图片水印</label>
                            </div>

                            <!-- 水印列表 -->
                            <div v-for="(watermark, index) in watermarkPreviews" :key="watermark.id" class="watermark-item">
                                <div class="watermark-thumbnail"
                                    @click="activeWatermarkIndex = index; showWatermarkEdit = true">
                                    <img :src="watermark.preview" alt="水印预览">
                                    <span class="watermark-index">水印 {{ index + 1 }}</span>
                                </div>
                                <button @click.stop="removeWatermarkElement(index)" class="remove-watermark-btn">
                                    移除
                                </button>
                            </div>

                            <!-- 水印编辑面板 -->
                            <div v-if="showWatermarkEdit && activeWatermarkIndex >= 0" class="watermark-options">
                                <div class="watermark-controls-row">
                                    <div class="watermark-control">
                                        <label>X位置</label>
                                        <input type="range" v-model="watermarkPreviews[activeWatermarkIndex].x" min="0"
                                            :max="videoWidth" @input="updateWatermarkElement(activeWatermarkIndex)">
                                        <span>{{ watermarkPreviews[activeWatermarkIndex].x }}px</span>
                                    </div>
                                    <div class="watermark-control">
                                        <label>Y位置</label>
                                        <input type="range" v-model="watermarkPreviews[activeWatermarkIndex].y" min="0"
                                            :max="backgroundHeight" @input="updateWatermarkElement(activeWatermarkIndex)">
                                        <span>{{ watermarkPreviews[activeWatermarkIndex].y }}px</span>
                                    </div>
                                    <div class="watermark-control">
                                        <label>大小</label>
                                        <input type="range" v-model="watermarkPreviews[activeWatermarkIndex].size" min="10"
                                            max="200" @input="updateWatermarkElement(activeWatermarkIndex)">
                                        <span>{{ watermarkPreviews[activeWatermarkIndex].size }}%</span>
                                    </div>
                                    <div class="watermark-control">
                                        <label>透明度</label>
                                        <input type="range" v-model="watermarkPreviews[activeWatermarkIndex].opacity"
                                            min="0" max="100" @input="updateWatermarkElement(activeWatermarkIndex)">
                                        <span>{{ watermarkPreviews[activeWatermarkIndex].opacity }}%</span>
                                    </div>
                                    <button @click.stop="showWatermarkEdit = false" class="cancel-btn1">
                                        完成编辑
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div class="caption-control-row">
                            <div class="file-upload">
                                <input @change="changCaptions" type="file" id="uploaderCaptions" accept=".vtt,.srt">
                                <label for="uploaderCaptions">选择字幕文件</label>
                            </div>
                            <el-switch v-model="autoGenerateSubtitles" active-text="一键生成字幕" inactive-text="关闭生成"
                                class="subtitle-switch" @change="handleSubtitleToggle" :disabled="isGeneratingSubtitles"
                                :loading="isGeneratingSubtitles">
                            </el-switch>
                            <el-button v-if="subtitleSrtUrl" type="primary" size="small" @click="exportSubtitle"
                                :disabled="isGeneratingSubtitles">
                                导出字幕(.srt)
                            </el-button>
                        </div>

                        <div class="save-template">
                            <button @click="saveTemplate" class="save-btn">保存编辑模板</button>
                        </div>
                        <div class="render-export-row">
                            <button @click="resetAllPreviews" class="reset-btn">重置所有编辑</button>
                            <button @click="renderVideo" class="render-btn">渲染视频</button>
                            <button @click="exportVideo" class="export-btn">导出视频</button>
                        </div>
                    </div>
                </el-tab-pane>

                <el-tab-pane label="素材库" name="material-library">
                    <div class="material-library">
                        <div class="material-section">
                            <h3>背景图片</h3>
                            <div class="material-grid">
                                <div v-for="(item, index) in backgroundImages" :key="index" class="material-item">
                                    <img :src="item.url" alt="背景图片" @click="selectMaterial(item, 'background')">
                                </div>
                            </div>
                            <el-pagination v-model="currentPage" :page-size="12" :total="backgroundImages.length"
                                layout="prev, pager, next" @current-change="handlePageChange" />
                        </div>

                        <div class="material-section">
                            <h3>水印图片</h3>
                            <div class="material-grid">
                                <div v-for="(item, index) in watermarkImages" :key="index" class="material-item">
                                    <img :src="item.url" alt="水印图片" @click="selectMaterial(item, 'watermark')">
                                </div>
                            </div>
                            <el-pagination v-model="currentPage" :page-size="12" :total="watermarkImages.length"
                                layout="prev, pager, next" @current-change="handlePageChange" />
                        </div>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup>
import { clearEmpty } from '@/utils/string.js';
import { createFFmpeg, fetchFile } from '@ffmpeg/ffmpeg';
import { reactive, ref, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { onMounted, onUnmounted, computed } from 'vue';
import axios from 'axios';
// 配置
const frameDir = 'frame';

// 变量
let step = '';
const activeTab = ref('template-edit');
const backgroundImages = ref([]);
const watermarkImages = ref([]);
const currentPage = ref(1);

const track = ref([]);
const filename = ref('');
const image = ref('');

const percent = ref(0);
const eTime = ref('');
const message = ref('');
const ffmpeg = createFFmpeg({
    log: true,
    corePath: 'https://unpkg.com/@ffmpeg/core@0.11.0/dist/ffmpeg-core.js'
});
const screenVideo = ref(null);
const previewElements = ref(null);
const video = ref(null);
const watermark = ref(null);
const captions = ref(null);
const videoAspectRatio = ref('16/9');
//字幕生成
const api = axios.create({
    baseURL: 'http://localhost:5000', // Flask默认端口
});
const subtitleText = ref('');
const subtitleSrtUrl = ref('');
const isGeneratingSubtitles = ref(false);
const handleSubtitleToggle = async (value) => {
    if (value) {
        try {
            isGeneratingSubtitles.value = true;
            ElMessage.info('正在生成字幕...');

            if (!video.value) {
                throw new Error('请先上传视频文件');
            }

            const formData = new FormData();
            formData.append('file', video.value);

            // 使用axios发送请求
            const response = await api.post('/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            subtitleText.value = response.data.text;
            subtitleSrtUrl.value = response.data.srt_url;

            ElMessage.success('字幕生成成功');
        } catch (error) {
            console.error('生成字幕失败:', error);
            ElMessage.error(`生成字幕失败: ${error.response?.data?.error || error.message}`);
            autoGenerateSubtitles.value = false;
        } finally {
            isGeneratingSubtitles.value = false;
        }
    } else {
        subtitleText.value = '';
        subtitleSrtUrl.value = '';
    }
};

// 导出字幕函数同样使用axios
const exportSubtitle = async () => {
    if (!subtitleSrtUrl.value) {
        ElMessage.warning('没有可导出的字幕文件');
        return;
    }

    try {
        // 直接从后端下载文件
        window.open(`http://localhost:5000${subtitleSrtUrl.value}`, '_blank');
    } catch (error) {
        console.error('导出字幕失败:', error);
        ElMessage.error('导出字幕失败');
    }
};
// 新增的可编辑字段数据
const editableFields = ref([
    {
        id: 'theme',
        label: '主题抽取',
        value: '',
        showEditPanel: false,
        previewElementId: null,
        style: {
            fontFamily: 'Arial',
            fontSize: 24,
            fontColor: '#ffffff',
            backgroundColor: '#000000',
            opacity: 0.8,
            xPosition: 50,
            yPosition: 50
        }
    },
    {
        id: 'summary',
        label: '自动摘要',
        value: '',
        showEditPanel: false,
        previewElementId: null,
        style: {
            fontFamily: 'Arial',
            fontSize: 16,
            fontColor: '#ffffff',
            backgroundColor: 'transparent',
            opacity: 0.8,
            xPosition: 50,
            yPosition: 100
        }
    },
    {
        id: 'keywords',
        label: '高频词提取',
        value: '',
        showEditPanel: false,
        previewElementId: null,
        style: {
            fontFamily: 'Arial',
            fontSize: 18,
            fontColor: '#ffffff',
            backgroundColor: 'rgba(0,0,0,0.5)',
            opacity: 0.8,
            xPosition: 50,
            yPosition: 150
        }
    }
]);

const videoWidth = ref(800);
const videoHeight = ref(450);

// 背景图片相关
const backgroundPreview = ref(null);
const backgroundElementId = ref(null); //跟踪背景元素ID
const isBackgroundApplied = ref(false);
const videoSizeOption = ref('match');
const customWidth = ref(1080);
const customHeight = ref(1920);

// 水印相关
const watermarkPreviews = ref([]);
const activeWatermarkIndex = ref(-1); // 当前激活的水印索引
const watermarkX = ref(10);
const watermarkY = ref(10);
const watermarkSize = ref(100);
const watermarkOpacity = ref(100);
const watermarkElementId = ref(null); //跟踪水印元素ID
const isWatermarkApplied = ref(false);
const showWatermarkEdit = ref(false);

ffmpeg.setLogger(({ type, message }) => {
    if (type === 'fferr') {
        message = clearEmpty(message);
        fileInfoFilter(message);
    }
});
ffmpeg.setProgress((progress) => {
    percent.value = progress.ratio;
    eTime.value = progress.time;
});

const changFile = async (event) => {
    if (!event.target.files?.[0]) return;

    try {
        const file = event.target.files[0];
        filename.value = file.name;
        video.value = file; // 更新响应式变量

        // 先创建临时预览
        await createVideoPreview(file);

        // 等待视频元素准备好
        await nextTick();
        if (!screenVideo.value) {
            throw new Error('视频元素未初始化');
        }

        // 加载到FFmpeg
        await handleLoad(file);

        // 生成序列帧
        await handleFrame();

        // 分析视频内容
        const analysis = await generateAnalysis(file);
        editableFields.value[0].value = analysis.theme;
        editableFields.value[1].value = analysis.summary;
        editableFields.value[2].value = analysis.keywords;

    } catch (error) {
        console.error('视频处理错误:', error);
        ElMessage.error(`视频处理失败: ${error.message}`);
        resetVideoState();
    }
};
// 视频预览
const createVideoPreview = (file) => {
    return new Promise((resolve, reject) => {
        const videoUrl = URL.createObjectURL(file);
        const tempVideo = document.createElement('video');
        tempVideo.src = videoUrl;

        tempVideo.onloadedmetadata = () => {
            videoWidth.value = tempVideo.videoWidth;
            videoHeight.value = tempVideo.videoHeight;

            // Set to 9:16 vertical aspect ratio
            videoAspectRatio.value = '9/16';

            URL.revokeObjectURL(videoUrl);
            resolve();
        };

        tempVideo.onerror = () => {
            URL.revokeObjectURL(videoUrl);
            reject(new Error('视频预览创建失败'));
        };
    });
};
const generateAnalysis = async (video) => {
    // 调用 API 生成主题抽取、自动摘要和高频词提取
    return {
        theme: '主题抽取结果',
        summary: '自动摘要结果',
        keywords: '高频词1, 高频词2, 高频词3'
    };
};

// const changImage = async (file) => {
//     watermark.value = file.target.files[0];
//     ffmpeg.FS('writeFile', 'watermark.png', await fetchFile(watermark.value));
// };

const changCaptions = async (file) => {
    captions.value = file.target.files[0];
};

const handleLoad = async (file) => {
    if (!isFFmpegLoaded.value) { // 使用状态标记而非直接调用 isLoaded()
        throw new Error('FFmpeg 未初始化完成，请稍后重试');
    }

    try {
        ffmpeg.FS('writeFile', 'input.mp4', await fetchFile(file));
        await ffmpeg.run('-i', 'input.mp4');

        const data = ffmpeg.FS('readFile', 'input.mp4');
        screenVideo.value.src = URL.createObjectURL(
            new Blob([data.buffer], { type: 'video/mp4' })
        );
    } catch (error) {
        console.error('视频加载失败:', error);
        throw new Error(`视频处理失败: ${error.message}`);
    }
};

const handleRender = async () => {
    if (!ffmpeg.isLoaded()) {
        alert('请加载视频');
        return;
    }
    const cmd = '-i infile -vf movie=watermark.png,colorkey=white:0.01:1.0[wm];[in][wm]overlay=30:10[out] outfile.mp4';
    const args = cmd.split(' ');
    await ffmpeg.run(...args);
    const data = ffmpeg.FS('readFile', 'outfile.mp4');
    screenVideo.value.src = URL.createObjectURL(new Blob([data.buffer], { type: 'video/mp4' }));
};

const handleFrame = async () => {
    if (!ffmpeg.isLoaded()) {
        throw new Error('FFmpeg未加载');
    }

    try {
        // 创建目录
        try { ffmpeg.FS('mkdir', frameDir); } catch { }

        // 生成帧
        await ffmpeg.run(
            '-i', 'input.mp4',
            '-vf', 'fps=1',
            `${frameDir}/frame-%03d.png`
        );

        // 读取生成的帧
        const frames = ffmpeg.FS('readdir', frameDir)
            .filter(file => file.match(/frame-\d+\.png/));

        track.value = frames.map(frame => {
            const data = ffmpeg.FS('readFile', `${frameDir}/${frame}`);
            return URL.createObjectURL(new Blob([data.buffer], { type: 'image/png' }));
        });

    } catch (error) {
        console.error('生成序列帧失败:', error);
        throw new Error('生成序列帧时出错');
    }
};
const updateCustomSize = () => {
    if (isBackgroundApplied.value) {
        const backgroundImage = document.querySelector('.background-image');
        if (backgroundImage) {
            const container = document.querySelector('.video-container-wrapper');
            const containerHeight = container.clientHeight;
            const aspectRatio = customWidth.value / customHeight.value;

            backgroundImage.style.width = `${containerHeight * aspectRatio}px`;
            backgroundImage.style.height = `${containerHeight}px`;

            // 重新调整视频大小
            adjustVideoSize();
        }
    }
};
const handleBackground = async (event) => {
    const backgroundFile = event.target.files[0];
    if (!backgroundFile) return;

    // 清理之前的URL对象
    if (backgroundPreview.value) {
        URL.revokeObjectURL(backgroundPreview.value);
    }

    // 重置文件输入，允许重复上传同一文件
    event.target.value = '';
    // 创建预览
    backgroundPreview.value = URL.createObjectURL(backgroundFile);
    isBackgroundApplied.value = false; // 重置应用状态

    // 如果是图片，获取尺寸
    if (backgroundFile.type.startsWith('image/')) {
        const img = new Image();
        img.onload = () => {
            if (videoSizeOption.value === 'match') {
                customWidth.value = img.width;
                customHeight.value = img.height;
            }
        };
        img.src = backgroundPreview.value;
    }
};

const previewBackground = async (event) => {
    event.stopPropagation();
    if (!backgroundPreview.value) {
        ElMessage.warning('请先选择背景图片');
        return;
    }
    try {
        // 获取图片原始尺寸
        const img = new Image();
        await new Promise((resolve) => {
            img.onload = resolve;
            img.src = backgroundPreview.value;
        });

        // 更新背景尺寸
        if (videoSizeOption.value === 'match') {
            customWidth.value = img.width;
            customHeight.value = img.height;
            //videoAspectRatio.value = `${img.width}/${img.height}`;
        }

        const backgroundLayer = document.querySelector('.background-layer');
        const backgroundImage = document.querySelector('.background-image');

        if (backgroundLayer && backgroundImage) {
            const container = document.querySelector('.video-container-wrapper');
            const containerHeight = container.clientHeight;
            const aspectRatio = customWidth.value / customHeight.value;

            backgroundImage.style.width = `${containerHeight * aspectRatio}px`;
            backgroundImage.style.height = `${containerHeight}px`;
            backgroundImage.style.objectFit = 'cover';

            // 更新视频高度为背景高度
            videoHeight.value = containerHeight;
        }

        isBackgroundApplied.value = true;
        ElMessage.success('背景预览已更新');

        // 调整视频大小
        adjustVideoSize();
        // 重置所有字段的Y位置
        editableFields.value.forEach(field => {
            field.style.yPosition = Math.min(field.style.yPosition, videoHeight.value);
        });
        // try {
        //     // 移除旧的背景元素
        //     removeBackgroundElement();

        //     // 创建新的背景元素
        //     const bgElement = document.createElement('div');
        //     bgElement.id = 'background-' + Date.now();
        //     backgroundElementId.value = bgElement.id;

        //     bgElement.style.cssText = `
        //         position: absolute;
        //         top: 0;
        //         left: 0;
        //         width: 100%;
        //         height: 100%;
        //         background-image: url(${backgroundPreview.value});
        //         background-size: cover;
        //         background-position: center;
        //         z-index: 0;
        //     `;

        //     // 添加到视频容器
        //     const videoContainer = document.querySelector('.video-container');
        //     if (videoContainer) {
        //         // 确保视频元素在最上层
        //         const videoElement = videoContainer.querySelector('video');
        //         if (videoElement) {
        //             videoElement.style.position = 'relative';
        //             videoElement.style.zIndex = '1';
        //         }

        //         videoContainer.appendChild(bgElement);
        //         isBackgroundApplied.value = true;
        //         ElMessage.success('背景预览已更新');
        //     }
    } catch (error) {
        console.error('背景预览失败:', error);
        ElMessage.error('背景预览失败');
    }
};
const adjustVideoSize = () => {
    nextTick(() => {
        if (isBackgroundApplied.value && screenVideo.value) {
            const backgroundImg = document.querySelector('.background-image');
            if (backgroundImg) {
                const container = document.querySelector('.video-container');
                const videoElement = screenVideo.value;

                // 更新视频尺寸
                videoElement.style.width = `${backgroundImg.clientWidth}px`;
                videoElement.style.height = 'auto';

                // 更新容器尺寸
                container.style.width = 'auto';
                container.style.height = 'auto';

                // 更新存储的尺寸值
                videoWidth.value = backgroundImg.clientWidth;
                videoHeight.value = backgroundImg.clientHeight;

                // 重新定位所有元素
                editableFields.value.forEach(field => {
                    if (field.previewElementId) {
                        applyStyleToVideo(field);
                    }
                });

                // 重新定位所有水印
                watermarkPreviews.value.forEach((_, index) => {
                    updateWatermarkElement(index);
                });
            }
        }
    });
};
const removeBackgroundElement = () => {
    if (backgroundPreview.value) {
        URL.revokeObjectURL(backgroundPreview.value);
        backgroundPreview.value = null;
    }

    // 重置背景应用状态
    isBackgroundApplied.value = false;

    // 重置视频尺寸
    if (video.value && screenVideo.value) {
        videoWidth.value = screenVideo.value.videoWidth;
        videoHeight.value = screenVideo.value.videoHeight;
        videoAspectRatio.value = `${videoWidth.value}/${videoHeight.value}`;
    }

    ElMessage.success('背景已移除');
};
// 新增变量
const originalWatermarkWidth = ref(0);
const originalWatermarkHeight = ref(0);
// 添加比例计算函数
const getActualVideoDimensions = () => {
    // 1. 用户明确选择自定义尺寸
    if (videoSizeOption.value === 'custom') {
        return {
            width: parseInt(customWidth.value),
            height: parseInt(customHeight.value)
        };
    }

    // 2. 用户选择匹配背景尺寸且有背景
    if (videoSizeOption.value === 'match' && isBackgroundApplied.value) {
        const bgImg = document.querySelector('.background-image');
        if (bgImg) {
            return {
                width: bgImg.naturalWidth || bgImg.width,
                height: bgImg.naturalHeight || bgImg.height
            };
        }
    }

    // 3. 默认使用视频原始尺寸
    if (screenVideo.value) {
        return {
            width: screenVideo.value.videoWidth,
            height: screenVideo.value.videoHeight
        };
    }

    // 4. 回退值
    return {
        width: 1280,
        height: 720
    };
};
const calculateScaleRatio = () => {
    const container = document.querySelector('.video-container');
    if (!container) return { x: 1, y: 1 };

    const actualDimensions = getActualVideoDimensions();
    const displayDimensions = getDisplayVideoDimensions(); // 获取当前显示尺寸

    return {
        x: actualDimensions.width / displayDimensions.width,
        y: actualDimensions.height / displayDimensions.height
    };
};

// 获取当前视频显示尺寸（网页中实际显示的像素尺寸）
const getDisplayVideoDimensions = () => {
    const container = document.querySelector('.video-container');
    if (!container) return { width: 0, height: 0 };

    // 如果有背景图片且已应用，使用背景图片的显示尺寸
    if (isBackgroundApplied.value) {
        const bgImg = document.querySelector('.background-image');
        if (bgImg) {
            return {
                width: bgImg.clientWidth,
                height: bgImg.clientHeight
            };
        }
    }

    // 否则使用视频容器的尺寸
    return {
        width: container.clientWidth,
        height: container.clientHeight
    };
};
const changImage = async (file) => {
    const watermarkFile = file.target.files[0];
    if (!watermarkFile) return;

    // 创建新水印项
    const newWatermark = {
        id: Date.now(),
        file: watermarkFile,
        preview: URL.createObjectURL(watermarkFile),
        x: 10,
        y: 10,
        size: 100,
        opacity: 100,
        elementId: null,
        originalWidth: 0,
        originalHeight: 0
    };

    // 获取图片原始尺寸
    const img = new Image();
    await new Promise((resolve) => {
        img.onload = () => {
            newWatermark.originalWidth = img.width;
            newWatermark.originalHeight = img.height;
            resolve();
        };
        img.src = newWatermark.preview;
    });

    watermarkPreviews.value.push(newWatermark);
    activeWatermarkIndex.value = watermarkPreviews.value.length - 1;
    showWatermarkEdit.value = true;

    await ffmpeg.FS('writeFile', `watermark-${newWatermark.id}.png`, await fetchFile(watermarkFile));
};

const updateWatermarkElement = (index) => {
    if (index < 0 || index >= watermarkPreviews.value.length) return;

    const watermark = watermarkPreviews.value[index];
    const container = document.querySelector('.video-container');
    if (!container) return;

    const elementId = `watermark-${watermark.id}`;

    let watermarkElement = document.getElementById(elementId);
    if (!watermarkElement) {
        watermarkElement = document.createElement('img');
        watermarkElement.id = elementId;
        watermarkElement.src = watermark.preview;
        container.appendChild(watermarkElement);

        // 更新watermark对象的elementId引用
        watermark.elementId = elementId;

        watermarkElement.onerror = () => {
            console.error('水印图片加载失败:', watermark.preview);
            watermarkElement.style.backgroundColor = 'rgba(255,0,0,0.3)';
        };
    } else {
        watermarkElement.src = watermark.preview;
    }

    // 获取比例和偏移量
    const ratio = calculateScaleRatio();
    const displayDimensions = getDisplayVideoDimensions();
    let offsetX = 0;
    let offsetY = 0;
    // 计算基准Y位置
    //let baseY = 0;
    if (isBackgroundApplied.value) {
        const bgImg = document.querySelector('.background-image');
        if (bgImg) {
            offsetX = (container.clientWidth - bgImg.clientWidth) / 2;
            offsetY = (container.clientHeight - bgImg.clientHeight) / 2;
        }
    }

    // 确保Y位置不超过最大值
    // const maxY = isBackgroundApplied.value ? backgroundHeight.value : videoHeight.value;
    // watermark.y = Math.min(watermark.y, maxY);

    // 计算实际大小
    // const actualWidth = (watermark.originalWidth * watermark.size) / 100;
    // const actualHeight = (watermark.originalHeight * watermark.size) / 100;
    // 计算显示位置和大小
    const displayX = (watermark.x / ratio.x) + offsetX;
    const displayY = (watermark.y / ratio.y) + offsetY;
    const displayWidth = (watermark.originalWidth * (watermark.size / 100)) / ratio.x;
    const displayHeight = (watermark.originalHeight * (watermark.size / 100)) / ratio.y;
    // 更新元素样式
    Object.assign(watermarkElement.style, {
        position: 'absolute',
        left: `${displayX}px`,
        top: `${displayY}px`,
        width: `${displayWidth}px`,
        height: `${displayHeight}px`,
        opacity: `${watermark.opacity / 100}`,
        pointerEvents: 'none',
        objectFit: 'contain',
        maxWidth: `${videoWidth.value}px`,
        maxHeight: `${videoHeight.value}px`,
        zIndex: '15', // 介于视频和文本之间
        display: 'block'
    });

    // console.log('水印位置更新:', {
    //     index,
    //     x: watermark.x,
    //     y: watermark.y,
    //     baseY,
    //     finalY: baseY + watermark.y
    // });
};

const removeWatermarkElement = (index) => {
    if (index >= 0 && index < watermarkPreviews.value.length) {
        const watermark = watermarkPreviews.value[index];

        // 移除DOM元素（现在使用统一ID查找）
        if (watermark.elementId) {
            const element = document.getElementById(watermark.elementId);
            if (element) {
                element.remove();
            }
        }

        // 从数组中移除
        watermarkPreviews.value.splice(index, 1);

        // 清理URL对象
        if (watermark.preview) {
            URL.revokeObjectURL(watermark.preview);
        }

        // 调整激活索引
        if (activeWatermarkIndex.value === index) {
            activeWatermarkIndex.value = -1;
            showWatermarkEdit.value = false;
        } else if (activeWatermarkIndex.value > index) {
            activeWatermarkIndex.value--;
        }

        ElMessage.success('水印已移除');
    }
};
const previewWatermark = (event) => {
    if (watermarkPreviews.value.length === 0) {
        ElMessage.warning('请先添加水印图片');
        return;
    }

    // 更新当前激活的水印
    if (activeWatermarkIndex.value >= 0) {
        updateWatermarkElement(activeWatermarkIndex.value);
    }

    ElMessage.success('水印预览已更新');
};

const isPreviewLoading = ref(false);

// const handleBackground = async (event) => {
//     const backgroundFile = event.target.files[0];
//     if (!backgroundFile) {
//         alert('请选择背景图片');
//         return;
//     }

//     if (!ffmpeg.isLoaded()) {
//         alert('FFmpeg 未加载，请等待加载完成');
//         return;
//     }

//     try {
//         const backgroundData = await fetchFile(backgroundFile);
//         ffmpeg.FS('writeFile', 'background.jpg', backgroundData);
//     } catch (error) {
//         console.error('写入背景图片时出错:', error);
//         ElMessage.error('写入背景图片时出错，请检查控制台日志');
//         return;
//     }

//     const backgroundUrl = URL.createObjectURL(backgroundFile);
//     backgroundImages.value = [{ url: backgroundUrl, name: backgroundFile.name }];

//     if (!video.value) {
//         alert('请先选择视频文件');
//         return;
//     }

//     if (!ffmpeg.FS('exists', 'infile')) {
//         alert('视频文件未加载，请重新加载视频');
//         return;
//     }

//     // Force 9:16 vertical aspect ratio
//     try {
//         await ffmpeg.run(
//             '-i', 'background.jpg',
//             '-i', 'infile',
//             '-filter_complex',
//             '[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[fg];[0:v][fg]overlay=(W-w)/2:(H-h)/2',
//             '-c:v', 'libx264',
//             '-crf', '23',
//             '-preset', 'veryfast',
//             'output.mp4'
//         );

//         const data = ffmpeg.FS('readFile', 'output.mp4');
//         screenVideo.value.src = URL.createObjectURL(new Blob([data.buffer], { type: 'video/mp4' }));

//         // Update aspect ratio for the container
//         videoAspectRatio.value = '9/16';
//         videoWidth.value = 1080;
//         videoHeight.value = 1920;

//         ElMessage.success('视频已成功嵌入到背景图片中，并设置为9:16竖屏模式');
//     } catch (error) {
//         console.error('嵌入背景图片时出错:', error);
//         ElMessage.error('嵌入背景图片时出错，请检查控制台日志');
//     }
// };

const dragStart = (event) => {
    const img = event.target;
    const frameIndex = track.value.indexOf(img.src);
    console.log('拖动开始', frameIndex);
    // 保存拖动的帧索引
    img.dataset.frameIndex = frameIndex;
};

const dragEnd = (event) => {
    const img = event.target;
    const frameIndex = img.dataset.frameIndex;
    console.log('拖动结束', frameIndex);
    // 根据帧索引跳转到视频的对应时间
    const videoElement = screenVideo.value;
    const duration = videoElement.duration;
    const frameRate = 30; // 假设默认帧率为30
    const seekTime = (frameIndex / frameRate) * duration;
    videoElement.currentTime = seekTime;
};

const handlePageChange = (newPage) => {
    currentPage.value = newPage;
};

const selectMaterial = (item, type) => {
    // 处理素材选择逻辑
    ElMessage.success(`选择了 ${type}：${item.name}`);
};
const toggleEditPanel = (index) => {
    // 先同步状态
    syncPreviewElements();
    // 再切换面板状态
    editableFields.value[index].showEditPanel = !editableFields.value[index].showEditPanel;
};
const backgroundHeight = computed(() => {
    if (isBackgroundApplied.value) {
        const bgImg = document.querySelector('.background-image');
        return bgImg ? bgImg.clientHeight : videoHeight.value;
    }
    return videoHeight.value;
});
const applyStyleToVideo = (field) => {
    syncPreviewElements();
    const container = document.querySelector('.video-container');
    if (!container) {
        console.error('视频容器未找到!');
        return;
    }

    // 移除旧元素
    const existingElement = field.previewElementId ? document.getElementById(field.previewElementId) : null;
    if (existingElement) {
        existingElement.remove();
    }

    // 创建新元素
    const elementId = `preview-${field.id}-${Date.now()}`;
    field.previewElementId = elementId;

    const previewElement = document.createElement('div');
    previewElement.id = elementId;
    previewElement.className = `preview-element font-${field.style.fontFamily.toLowerCase().replace(/\s+/g, '-')}`;
    previewElement.textContent = field.value;

    // // 计算基准Y位置
    // let baseY = 0;
    // if (isBackgroundApplied.value) {
    //     const bgImg = document.querySelector('.background-image');
    //     if (bgImg) {
    //         // 计算背景图片顶部偏移量
    //         baseY = (container.clientHeight - bgImg.clientHeight) / 2;
    //     }
    // }

    // // 确保Y位置不超过最大值
    // const maxY = isBackgroundApplied.value ? backgroundHeight.value : videoHeight.value;
    // field.style.yPosition = Math.min(field.style.yPosition, maxY);

    // 获取比例和实际尺寸
    const ratio = calculateScaleRatio();
    const actualDimensions = getActualVideoDimensions();
    const displayDimensions = getDisplayVideoDimensions();

    // 计算显示位置（考虑可能的居中偏移）
    let offsetX = 0;
    let offsetY = 0;

    if (isBackgroundApplied.value) {
        const bgImg = document.querySelector('.background-image');
        if (bgImg) {
            offsetX = (container.clientWidth - bgImg.clientWidth) / 2;
            offsetY = (container.clientHeight - bgImg.clientHeight) / 2;
        }
    }

    // 应用缩放后的位置
    const displayX = (field.style.xPosition / ratio.x) + offsetX;
    const displayY = (field.style.yPosition / ratio.y) + offsetY;

    Object.assign(previewElement.style, {
        position: 'absolute',
        left: `${displayX}px`,
        top: `${displayY}px`,
        fontSize: `${field.style.fontSize / ratio.y}px`,
        fontFamily: field.style.fontFamily,
        color: field.style.fontColor,
        backgroundColor: field.style.backgroundColor,
        padding: '5px 10px',
        borderRadius: '4px',
        maxWidth: `${actualDimensions.width * 0.8 / ratio.x}px`,
        wordBreak: 'break-word',
        pointerEvents: 'none',
        zIndex: '20', // 提高z-index确保在视频和背景之上
        display: 'block'
    });

    // 确保添加到正确的容器
    container.appendChild(previewElement);
    // console.log('元素位置:', {
    //     x: field.style.xPosition,
    //     y: field.style.yPosition,
    //     baseY,
    //     finalY: baseY + field.style.yPosition,
    //     containerHeight: container.clientHeight
    // });
};
const removePreviewElement = (elementId) => {
    try {
        if (!elementId) {
            throw new Error('无效的元素ID');
        }

        const element = document.getElementById(elementId);
        if (element) {
            element.remove();
            ElMessage.success('样式已移除');
        } else {
            ElMessage.warning('未找到对应的预览元素');
        }

        // 使用map保持响应式
        editableFields.value = editableFields.value.map(field => {
            if (field.previewElementId === elementId) {
                return { ...field, previewElementId: null };
            }
            return field;
        });
    } catch (error) {
        console.error('移除预览元素失败:', error);
        ElMessage.error(`移除失败: ${error.message}`);
    }
};
// 同步预览元素状态
const syncPreviewElements = () => {
    editableFields.value = editableFields.value.map(field => {
        // 如果已经有previewElementId但DOM中不存在，则重置
        if (field.previewElementId && !document.getElementById(field.previewElementId)) {
            return { ...field, previewElementId: null };
        }
        return field;
    });
};
const saveTemplate = () => {
    // 收集所有编辑信息
    const templateData = {
        fields: editableFields.value.map(field => ({
            id: field.id,
            label: field.label,
            value: field.value,
            style: field.style
        })),
        videoInfo: {
            filename: filename.value,
            width: videoWidth.value,
            height: videoHeight.value
        },
        backgroundImage: backgroundImages.value[0]?.url || null,
        watermark: watermark ? 'watermark.png' : null,
        captions: captions ? captions.name : null
    };

    // 这里应该是发送到后端的逻辑
    console.log('保存模板数据:', templateData);
    ElMessage.success('模板信息已保存，将使用FFmpeg渲染最终视频');

    // 实际应用中，这里应该是API调用
    // sendTemplateToBackend(templateData).then(...)
};

const isFFmpegLoaded = ref(false);
const observer = new ResizeObserver(() => {
    if (isBackgroundApplied.value) {
        adjustVideoSize();
    }
});
onMounted(async () => {
    window.addEventListener('resize', handleResize);
    try {
        if (!ffmpeg.isLoaded()) {
            await ffmpeg.load(); // 显式加载
            isFFmpegLoaded.value = true;
            console.log('FFmpeg 初始化完成');
        }
    } catch (error) {
        console.error('FFmpeg 加载失败:', error);
        ElMessage.error('FFmpeg 初始化失败，请刷新页面重试');
    }
    const container = document.querySelector('.video-container');
    if (container) {
        observer.observe(container);
    }

});
onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    // 清理所有创建的URL对象
    if (backgroundPreview.value) {
        URL.revokeObjectURL(backgroundPreview.value);
    }
    // 清理水印URL
    watermarkPreviews.value.forEach(watermark => {
        if (watermark.preview) {
            URL.revokeObjectURL(watermark.preview);
        }
    });
    // 清理序列帧URL
    track.value.forEach(url => URL.revokeObjectURL(url));
    observer.disconnect();
});
const updateAllElementPositions = () => {
    // 更新文本元素
    editableFields.value.forEach(field => {
        if (field.previewElementId) {
            applyStyleToVideo(field);
        }
    });

    // 更新水印元素
    watermarkPreviews.value.forEach((_, index) => {
        updateWatermarkElement(index);
    });
};
const debounce = (func, wait) => {
    let timeout;
    return function () {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
};
const handleResize = debounce(() => {
    if (isBackgroundApplied.value && video.value) {
        adjustVideoSize();
    }
    updateAllElementPositions();
}, 200);

const handleVideoLoaded = () => {
    console.log('视频元数据加载完成');
    if (isBackgroundApplied.value) {
        adjustVideoSize();
        const bgImg = document.querySelector('.background-image');
        if (bgImg) {
            videoHeight.value = bgImg.clientHeight;
            // 重新计算所有预览元素的Y位置
            editableFields.value.forEach(field => {
                if (field.previewElementId) {
                    const element = document.getElementById(field.previewElementId);
                    if (element) {
                        const bgTop = (document.querySelector('.video-container').clientHeight - bgImg.clientHeight) / 2;
                        element.style.top = `${bgTop + field.style.yPosition}px`;
                    }
                }
            });
            // 重新计算所有水印的Y位置
            watermarkPreviews.value.forEach(watermark => {
                if (watermark.elementId) {
                    const element = document.getElementById(watermark.elementId);
                    if (element) {
                        const bgTop = (document.querySelector('.video-container').clientHeight - bgImg.clientHeight) / 2;
                        element.style.top = `${bgTop + watermark.y}px`;
                    }
                }
            });
        }
    } else {
        // 没有背景时保持原始宽高比
        videoWidth.value = screenVideo.value.videoWidth;
        videoHeight.value = screenVideo.value.videoHeight;
        videoAspectRatio.value = `${videoWidth.value}/${videoHeight.value}`;
    }
    // 确保Y坐标不超过最大高度
    editableFields.value.forEach(field => {
        field.style.yPosition = Math.min(field.style.yPosition, videoHeight.value);
    });
};

const handleVideoError = (error) => {
    console.error('视频播放错误:', error);
    ElMessage.error('视频播放失败，请检查文件格式');
    resetVideoState();
};
const resetVideoState = () => {
    video.value = null;
    filename.value = '';
    track.value = [];
};

const autoGenerateSubtitles = ref(false);

const fontFiles = {
    'Arial': '/fonts/arial.ttf',
    'Times New Roman': '/fonts/times.ttf',
    'Courier New': '/fonts/courier.ttf',
    'Georgia': '/fonts/georgia.ttf',
    'Verdana': '/fonts/verdana.ttf'
};

async function loadFont(fontName) {
    try {
        const fontPath = fontFiles[fontName];
        if (!fontPath) throw new Error(`字体${fontName}未配置`);

        const response = await fetch(fontPath);
        if (!response.ok) throw new Error('字体加载失败');

        const fontData = await response.arrayBuffer();
        ffmpeg.FS('writeFile', `font_${fontName.replace(/\s+/g, '_')}.ttf`, new Uint8Array(fontData));
        return `font_${fontName.replace(/\s+/g, '_')}.ttf`;
    } catch (e) {
        console.error(`字体加载失败: ${e.message}`);
        return 'default_font.ttf'; // 回退字体
    }
}
//待完善的方法
const renderVideo = async () => {
    let command = [];
    let filterComplex = [];
    let currentOutput = '[0:v]';
    try {
        ElMessage.info('正在渲染视频...');
        if (!ffmpeg.isLoaded()) await ffmpeg.load();

        // 1. 准备输入文件
        const videoData = await fetchFile(video.value);
        ffmpeg.FS('writeFile', 'input.mp4', videoData);

        // 2. 构建命令基础
        command = ['-i', 'input.mp4'];
        filterComplex = [];
        currentOutput = '[0:v]'; // 初始视频流
        let hasBackground = false;

        // 3. 背景处理（修复尺寸问题）
        if (backgroundPreview.value) {
            const bgData = await fetchFile(await (await fetch(backgroundPreview.value)).blob());
            ffmpeg.FS('writeFile', 'background.png', bgData);
            command.push('-i', 'background.png');
            hasBackground = true;

            // 获取背景实际尺寸
            const bgImg = await new Promise(resolve => {
                const img = new Image();
                img.onload = () => resolve(img);
                img.src = backgroundPreview.value;
            });

            // 确定输出尺寸
            let outputWidth, outputHeight;
            if (videoSizeOption.value === 'custom') {
                // 使用用户自定义尺寸
                outputWidth = parseInt(customWidth.value);
                outputHeight = parseInt(customHeight.value);
            } else {
                // 使用背景图片尺寸（'match' 模式）
                outputWidth = bgImg.naturalWidth || bgImg.width;
                outputHeight = bgImg.naturalHeight || bgImg.height;
            }

            // 确保尺寸为偶数（编码器要求）
            const makeEven = num => 2 * Math.round(num / 2);
            outputWidth = makeEven(outputWidth);
            outputHeight = makeEven(outputHeight);

            filterComplex.push(
                `[1:v]scale=${outputWidth}:${outputHeight}[bg];` +
                `[0:v]scale=${outputWidth}:${outputHeight}:force_original_aspect_ratio=decrease[fg];` +
                `[bg][fg]overlay=(W-w)/2:(H-h)/2[outv]`
            );
            currentOutput = '[outv]';
        }

        // 4. 水印处理（修复连接逻辑）
        await Promise.all(watermarkPreviews.value.map(async (wm, i) => {
            const wmData = await fetchFile(await (await fetch(wm.preview)).blob());
            ffmpeg.FS('writeFile', `wm${i}.png`, wmData);
            command.push('-i', `wm${i}.png`);

            const wmIndex = i + (hasBackground ? 2 : 1);
            filterComplex.push(
                `[${wmIndex}]scale=iw*${wm.size / 100}:-1,` +
                `format=rgba,colorchannelmixer=aa=${wm.opacity / 100}[wm${i}];` +
                `${currentOutput}[wm${i}]overlay=${wm.x}:${wm.y}:format=auto[outv]`
            );
            currentOutput = '[outv]'; // 确保使用正确的输出标签
        }));

        // 5. 文字处理（确保使用正确的输出流）
        const textFields = editableFields.value.filter(f => f.previewElementId && f.value);
        if (textFields.length > 0) {
            for (const [index, field] of textFields.entries()) {
                const fontPath = await loadFont(field.style.fontFamily);
                const style = field.style;

                filterComplex.push(
                    `${currentOutput}` +
                    `drawtext=text='${field.value.replace(/'/g, "'\\\\''")}':` +
                    `x=${style.xPosition}:y=${style.yPosition}:` +
                    `fontsize=${style.fontSize}:` +
                    `fontcolor=${style.fontColor.replace('#', '0x')}:` +
                    `fontfile=${fontPath}:` +
                    `box=1:boxcolor=${style.backgroundColor.replace('#', '0x')}` +
                    `[outv]`
                );
                currentOutput = '[outv]';
            }
        }

        // 6. 命令组合（确保最终使用[outv]）
        command.push(
            '-filter_complex', filterComplex.join(';'),
            '-map', currentOutput, // 使用最终的输出流
            '-map', '0:a?',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-profile:v', 'main',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'copy',
            '-y',
            'output.mp4'
        );

        console.log('完整命令:', command.join(' '));
        await ffmpeg.run(...command);

        // 7. 验证输出
        const data = ffmpeg.FS('readFile', 'output.mp4');
        const blob = new Blob([data.buffer], { type: 'video/mp4' });
        screenVideo.value.src = URL.createObjectURL(blob);
        video.value = new File([blob], 'rendered.mp4', { type: 'video/mp4' });

        ElMessage.success('渲染成功!');
        resetAllPreviews();
    } catch (error) {
        console.error('完整错误:', {
            command: command?.join(' '),
            filterChain: filterComplex,
            error: error.message,
            stack: error.stack
        });
        ElMessage.error(`渲染失败: ${error.message}`);
    }
};
// 辅助函数：获取图片尺寸
function getImageDimensions(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve({
            width: img.width,
            height: img.height
        });
        img.src = url;
    });
}
const exportVideo = async () => {
    try {
        ElMessage.info('正在导出视频...');
        // 创建下载链接
        const videoSrc = screenVideo.value.src;
        const a = document.createElement('a');
        a.href = videoSrc;
        a.download = `exported_video_${Date.now()}.mp4`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        ElMessage.success('视频导出成功！');
    } catch (error) {
        console.error('导出失败:', error);
        ElMessage.error(`导出失败: ${error.message}`);
    }
};
//重置所有编辑
const resetAllPreviews = () => {
    editableFields.value.forEach(field => {
        if (field.previewElementId) {
            removePreviewElement(field.previewElementId);
        }
        field.showEditPanel = false;
    });
    removeBackgroundElement();
    while (watermarkPreviews.value.length > 0) {
        removeWatermarkElement(0);
    }
    watermarkPreviews.value = [];
};
</script>

<style lang="less" scoped>
/* 字体样式 */
.font-arial {
    font-family: Arial, sans-serif;
}

.font-times-new-roman {
    font-family: "Times New Roman", serif;
}

.font-courier-new {
    font-family: "Courier New", monospace;
}

.font-georgia {
    font-family: Georgia, serif;
}

.font-verdana {
    font-family: Verdana, sans-serif;
}

/* 字体样式 */
.container {
    display: flex;
    height: 100vh;
    width: 100vw;
    padding: 10px;
    box-sizing: border-box;
}

.left-panel {
    width: 60%;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.video-container-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
    background-color: #000;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}

.background-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 0;
    overflow: hidden;
    z-index: 0;
}

.background-image {
    height: 100%;
    width: auto;
    object-fit: contain;
}

.video-container {
    position: relative;
    z-index: 1;
    width: auto;
    max-width: 100%;
    max-height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.video-upload-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0.3);
    color: white;
    cursor: pointer;
}

.video-container video {
    // position: relative;
    // top: 50%;
    // transform: translateY(-50%);
    max-width: 100%;
    max-height: 100%;
    display: block;
}

#screen-video {
    z-index: 1;
}

.video-upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    cursor: pointer;
}

.hidden-uploader {
    display: none;
}

.upload-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    cursor: pointer;
    padding: 20px;
    border: 2px dashed #ccc;
    border-radius: 8px;
    width: 80%;
    height: 80%;
    transition: all 0.3s;

    &:hover {
        border-color: #409EFF;
        background-color: rgba(64, 158, 255, 0.1);
    }
}

.upload-icon {
    font-size: 48px;
    margin-bottom: 10px;
}

#preview-elements {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 12;
}

.preview-element {
    z-index: 12;
}

.track-container {
    height: 150px;
    margin-top: 10px;
    margin-bottom: 96px;
}

.track {
    height: 100%;
    overflow-x: auto;
    white-space: nowrap;
    background-color: #333;
    padding: 10px;
}

.track img {
    display: inline-block;
    height: 100%;
    margin-right: 5px;
}

.right-panel {
    width: 40%;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    margin-left: 20px;
    margin-right: 10px;
}

.editable-fields {
    margin-bottom: 20px;
}

.field-item {
    position: relative;
    margin-bottom: 15px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    padding: 10px;
    overflow: hidden;
    /* 防止内容溢出 */
}

.field-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.field-header label {
    margin-right: 10px;
    font-weight: bold;
    min-width: 100px;
}

.field-input {
    flex: 1;
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 3px;
}

.edit-btn {
    margin-left: 10px;
    padding: 5px 10px;
    background-color: #409EFF;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}

.edit-panel {
    position: relative;
    width: calc(100% - 20px);
    margin-top: 10px;
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
    box-sizing: border-box;
    overflow: auto;
    max-height: 400px;
}

.style-controls {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}

.control-group {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.control-group label {
    min-width: 40px;
    margin-right: 10px;
}

.control-group select,
.control-group input[type="range"],
.control-group input[type="color"] {
    flex: 1;
}

.control-group span {
    margin-left: 10px;
    min-width: 40px;
}

.apply-controls {
    grid-column: span 2;
    display: flex;
    gap: 10px;
}

.apply-btn {
    flex: 1;
    padding: 8px;
    background-color: #67C23A;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}

.cancel-btn {
    flex: 1;
    padding: 8px;
    background-color: #f56c6c;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.cancel-btn:hover {
    background-color: #f78989;
}

.file-upload {
    position: relative;
    margin-bottom: 20px;
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    padding: 15px;
    transition: border-color 0.3s;
}

.file-upload:hover {
    border-color: #409eff;
}

.file-upload input[type="file"] {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    opacity: 0;
    cursor: pointer;
}

.file-upload label {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
    color: #606266;
    cursor: pointer;
    transition: all 0.3s;
}

.file-upload label:hover {
    background-color: #ecf5ff;
    color: #409eff;
}

.preview-options,
.watermark-options {
    margin-top: 15px;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 6px;
    border: 1px solid #e9ecef;
}

.size-options,
.watermark-control {
    margin-bottom: 12px;
}

.upload-preview-group {
    margin-bottom: 20px;
    border: 1px solid #ebeef5;
    border-radius: 6px;
    padding: 15px;
}

.file-upload {
    position: relative;
    margin-bottom: 15px;
}

.preview-options,
.watermark-options {
    padding-top: 15px;
    border-top: 1px solid #eee;
    margin-top: 15px;
}

/* 水印列表样式 */
.watermark-item {
    display: flex;
    align-items: center;
    margin-top: 10px;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.watermark-thumbnail {
    flex: 1;
    display: flex;
    align-items: center;
    cursor: pointer;
}

.watermark-thumbnail img {
    width: 40px;
    height: 40px;
    object-fit: contain;
    margin-right: 10px;
}

.watermark-index {
    font-size: 14px;
}

.remove-watermark-btn {
    margin-left: 10px;
    padding: 4px 8px;
    background-color: #f56c6c;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}

/* 水印编辑面板 */
.watermark-options {
    margin-top: 15px;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 6px;
    border: 1px solid #e9ecef;
}

.watermark-controls-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.watermark-control {
    display: flex;
    align-items: center;
    min-width: 120px;
}

.watermark-control label {
    white-space: nowrap;
    margin-right: 5px;
    font-size: 14px;
}

.watermark-control input[type="range"] {
    flex: 1;
    min-width: 80px;
}

.watermark-control span {
    min-width: 40px;
    text-align: right;
    font-size: 13px;
    margin-left: 5px;
}

.preview-btn {
    flex: 1;
    padding: 8px 15px;
    background-color: #409eff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.subtitle-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
}

.download-btn {
    padding: 8px 15px;
    background-color: #67c23a;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.save-template {
    margin-top: 20px;
}

.save-btn {
    width: 100%;
    padding: 12px;
    background-color: #409EFF;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;

    &:hover {
        background-color: #337ecc;
    }
}

.material-library {
    flex: 1;
    overflow-y: auto;
}

.material-section {
    margin-bottom: 20px;
}

.material-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.material-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.material-item {
    aspect-ratio: 1 / 1;
    border: 1px solid #ccc;
    cursor: pointer;
}

.material-item:hover {
    border-color: #007bff;
}

/* Caption control row */
.caption-control-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
}

.subtitle-switch {
    margin-left: 20px;
}

/* Full-width render/export buttons */
.render-export-row {
    display: flex;
    width: 100%;
    gap: 15px;
    margin-top: 15px;
    margin-bottom: 75px;
}

.reset-btn,
.render-btn {
    flex: 1;
    padding: 12px 0;
    background-color: #409eff;
    /* Default blue */
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.render-btn:hover {
    background-color: #66b1ff;
}

.export-btn {
    flex: 1;
    padding: 12px 0;
    background-color: #67c23a;
    /* Default green */
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.export-btn:hover {
    background-color: #85ce61;
}

.size-options,
.watermark-control {
    margin-bottom: 12px;
}

.size-options label,
.watermark-control label {
    display: block;
    margin-bottom: 5px;
    font-size: 14px;
    color: #495057;
}

.watermark-control {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 120px;
}

.watermark-control label {
    white-space: nowrap;
    font-size: 14px;
    color: #606266;
}

.watermark-control input[type="range"] {
    flex: 1;
    min-width: 80px;
}

.watermark-control span {
    min-width: 40px;
    text-align: right;
    font-size: 13px;
    color: #909399;
}

.cancel-btn1 {
    padding: 8px 15px;
    background-color: #f56c6c;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
    white-space: nowrap;
}

.cancel-btn1:hover:not(:disabled) {
    background-color: #f78989;
}

.cancel-btn1:disabled {
    background-color: #c0c4cc;
    cursor: not-allowed;
    opacity: 0.6;
}

.custom-size {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 8px;
}

.custom-size input {
    flex: 1;
    padding: 6px 10px;
    border: 1px solid #ced4da;
    border-radius: 4px;
}

.preview-btn {
    padding: 8px 16px;
    background-color: #4e73df;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.preview-btn:hover {
    background-color: #2e59d9;
}

/* 水印预览元素 */
.watermark-preview {
    position: absolute;
    pointer-events: none;
    transition: all 0.3s;
    z-index: 10;
    object-fit: contain;
}
</style>
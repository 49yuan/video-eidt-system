<template>
    <div class="container">
        <!-- 左侧：视频播放器和轨道 -->
        <div class="left-panel">
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
                                        <input type="range" v-model="field.style.yPosition" min="0" :max="videoHeight"
                                            step="1">
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
                                        <input type="number" v-model="customWidth" placeholder="宽度">
                                        <span>x</span>
                                        <input type="number" v-model="customHeight" placeholder="高度">
                                    </div>
                                </div>
                                <div class="apply-controls">
                                    <button @click.stop="previewBackground" class="preview-btn">预览效果</button>
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
                                <label for="uploaderImage">选择图片水印文件</label>
                            </div>

                            <div v-if="watermarkPreview" class="watermark-options">
                                <div class="watermark-controls-row">
                                    <div class="watermark-control">
                                        <label>X位置</label>
                                        <input type="range" v-model="watermarkX" min="0" :max="videoWidth"
                                            @input="updateWatermarkElement">
                                        <span>{{ watermarkX }}px</span>
                                    </div>
                                    <div class="watermark-control">
                                        <label>Y位置</label>
                                        <input type="range" v-model="watermarkY" min="0" :max="videoHeight"
                                            @input="updateWatermarkElement">
                                        <span>{{ watermarkY }}px</span>
                                    </div>
                                    <div class="watermark-control">
                                        <label>大小</label>
                                        <input type="range" v-model="watermarkSize" min="10" max="200"
                                            @input="updateWatermarkElement">
                                        <span>{{ watermarkSize }}%</span>
                                    </div>
                                    <button @click.stop="removeWatermarkElement" class="cancel-btn1"
                                        :disabled="!isWatermarkApplied">
                                        取消应用
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
                                class="subtitle-switch" @change="handleSubtitleToggle">
                            </el-switch>
                        </div>

                        <div class="save-template">
                            <button @click="saveTemplate" class="save-btn">保存编辑模板</button>
                        </div>
                        <div class="render-export-row">
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
import { onMounted, reactive, ref, nextTick } from 'vue';
import { ElMessage } from 'element-plus';

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
const watermarkPreview = ref(null);
const watermarkX = ref(10);
const watermarkY = ref(10);
const watermarkSize = ref(100);
const watermarkOpacity = ref(100);
const watermarkElementId = ref(null); //跟踪水印元素ID
const isWatermarkApplied = ref(false);

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
const handleBackground = async (event) => {
    const backgroundFile = event.target.files[0];
    if (!backgroundFile) return;

    // 清理之前的URL对象
    if (backgroundPreview.value) {
        URL.revokeObjectURL(backgroundPreview.value);
    }

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
        // 移除旧的背景元素
        removeBackgroundElement();

        // 创建新的背景元素
        const bgElement = document.createElement('div');
        bgElement.id = 'background-' + Date.now();
        backgroundElementId.value = bgElement.id;

        bgElement.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url(${backgroundPreview.value});
            background-size: cover;
            background-position: center;
            z-index: -1;
        `;

        // 添加到视频容器
        document.querySelector('.video-container').appendChild(bgElement);
        isBackgroundApplied.value = true;

        ElMessage.success('背景预览已更新');
    } catch (error) {
        console.error('背景预览失败:', error);
        ElMessage.error('背景预览失败');
    }
};

const removeBackgroundElement = () => {
    if (backgroundElementId.value) {
        const element = document.getElementById(backgroundElementId.value);
        if (element) {
            element.remove();
        }
        backgroundElementId.value = null;
        isBackgroundApplied.value = false;
    }
};
// 新增变量
const originalWatermarkWidth = ref(0);
const originalWatermarkHeight = ref(0);

const changImage = async (file) => {
    const watermarkFile = file.target.files[0];
    if (!watermarkFile) return;

    // 清理之前的URL对象
    if (watermarkPreview.value) {
        URL.revokeObjectURL(watermarkPreview.value);
    }

    watermark.value = watermarkFile;
    watermarkPreview.value = URL.createObjectURL(watermarkFile);

    // 获取图片原始尺寸
    const img = new Image();
    img.onload = () => {
        originalWatermarkWidth.value = img.width;
        originalWatermarkHeight.value = img.height;
        updateWatermarkElement(); // 初始化水印元素
    };
    img.src = watermarkPreview.value;

    await ffmpeg.FS('writeFile', 'watermark.png', await fetchFile(watermark.value));
};

const updateWatermarkElement = () => {
    if (!watermarkPreview.value) return;

    let watermarkElement = watermarkElementId.value
        ? document.getElementById(watermarkElementId.value)
        : null;

    if (!watermarkElement) {
        // 创建新水印元素
        watermarkElement = document.createElement('img');
        watermarkElement.id = 'watermark-' + Date.now();
        watermarkElementId.value = watermarkElement.id;
        document.querySelector('.video-container').appendChild(watermarkElement);
    }

    // 计算实际大小（基于原始尺寸的百分比）
    const actualWidth = (originalWatermarkWidth.value * watermarkSize.value) / 100;
    const actualHeight = (originalWatermarkHeight.value * watermarkSize.value) / 100;

    // 更新水印属性
    watermarkElement.src = watermarkPreview.value;
    watermarkElement.className = 'watermark-preview';
    watermarkElement.style.position = 'absolute';
    watermarkElement.style.left = `${watermarkX.value}px`;
    watermarkElement.style.top = `${watermarkY.value}px`;
    watermarkElement.style.width = `${actualWidth}px`; // 使用实际像素值
    watermarkElement.style.height = `${actualHeight}px`; // 使用实际像素值
    watermarkElement.style.opacity = `${watermarkOpacity.value / 100}`;
    watermarkElement.style.pointerEvents = 'none';
    watermarkElement.style.objectFit = 'contain';
    watermarkElement.style.transformOrigin = '0 0';

    isWatermarkApplied.value = true;
};

const removeWatermarkElement = () => {
    if (watermarkElementId.value) {
        const element = document.getElementById(watermarkElementId.value);
        if (element) {
            element.remove();
        }
        watermarkElementId.value = null;
        isWatermarkApplied.value = false;
    }
};
const previewWatermark = (event) => {
    event.stopPropagation();
    if (!watermarkPreview.value) {
        ElMessage.warning('请先选择水印图片');
        return;
    }

    updateWatermarkElement();
    ElMessage.success('水印预览已更新');
};

const createWatermarkElement = () => {
    // 移除旧的水印
    const oldWatermark = document.querySelector('.watermark-preview');
    if (oldWatermark) oldWatermark.remove();

    if (!watermarkPreview.value) return;

    const watermarkElement = document.createElement('img');
    watermarkElement.className = 'watermark-preview';
    watermarkElement.src = watermarkPreview.value;
    watermarkElement.style.cssText = `
        position: absolute;
        left: ${watermarkX.value}px;
        top: ${watermarkY.value}px;
        width: ${watermarkSize.value}%;
        opacity: ${watermarkOpacity.value / 100};
        pointer-events: none;
        max-width: 30%;
        max-height: 30%;
        object-fit: contain;
    `;

    document.querySelector('.video-container').appendChild(watermarkElement);
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

const applyStyleToVideo = (field) => {
    // 先同步状态
    syncPreviewElements();

    // 移除之前的预览元素（如果存在）
    if (field.previewElementId) {
        removePreviewElement(field.previewElementId);
    }

    // 创建新的预览元素
    const elementId = `preview-${field.id}-${Date.now()}`;
    field.previewElementId = elementId;

    const previewElement = document.createElement('div');
    previewElement.id = elementId;
    previewElement.className = `preview-element font-${field.style.fontFamily.toLowerCase().replace(/\s+/g, '-')}`;
    previewElement.textContent = field.value;

    // 应用样式
    Object.assign(previewElement.style, {
        position: 'absolute',
        left: `${field.style.xPosition}px`,
        top: `${field.style.yPosition}px`,
        fontSize: `${field.style.fontSize}px`,
        color: field.style.fontColor,
        backgroundColor: field.style.backgroundColor,
        padding: '5px 10px',
        borderRadius: '4px',
        maxWidth: '80%',
        wordBreak: 'break-word',
        pointerEvents: 'none'
    });

    // 添加到预览容器
    previewElements.value.appendChild(previewElement);

    ElMessage.success(`已应用 ${field.label} 的样式到预览`);
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

onMounted(async () => {
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
});
const handleVideoLoaded = () => {
    console.log('视频元数据加载完成');
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
const handleSubtitleToggle = (value) => {
    if (value) {
        ElMessage.info('已开启自动生成字幕');
        // Add your auto-generation logic here
    } else {
        ElMessage.info('已关闭自动生成字幕');
    }
};
//待完善的方法
const renderVideo = async () => {
    try {
        ElMessage.info('正在渲染视频...');

        // 准备FFmpeg命令参数
        const commands = [
            '-i', 'input.mp4'
        ];

        // 添加背景图片处理
        if (backgroundPreview.value) {
            commands.push('-i', 'background.jpg');
            commands.push('-filter_complex',
                `[1]scale=${customWidth.value}:${customHeight.value}[bg];` +
                `[0]scale=${customWidth.value}:${customHeight.value}:force_original_aspect_ratio=decrease[fg];` +
                `[bg][fg]overlay=(W-w)/2:(H-h)/2`);
        }

        // 添加水印处理
        if (watermarkPreview.value) {
            commands.push('-i', 'watermark.png');
            commands.push('-filter_complex',
                `[2]scale=iw*${watermarkSize.value / 100}:-1,format=rgba,colorchannelmixer=aa=${watermarkOpacity.value / 100}[wm];` +
                `[0][wm]overlay=${watermarkX.value}:${watermarkY.value}`);
        }

        // 添加文字处理
        editableFields.value.forEach(field => {
            if (field.previewElementId) {
                commands.push('-vf',
                    `drawtext=text='${field.value}':x=${field.style.xPosition}:y=${field.style.yPosition}:` +
                    `fontsize=${field.style.fontSize}:fontcolor=${field.style.fontColor.replace('#', '0x')}@${Math.round(field.style.opacity * 255).toString(16)}:` +
                    `box=1:boxcolor=${field.style.backgroundColor.replace('#', '0x')}@${Math.round(field.style.opacity * 255).toString(16)}`);
            }
        });

        commands.push('-c:v', 'libx264', '-preset', 'fast', 'output.mp4');

        await ffmpeg.run(...commands);

        ElMessage.success('视频渲染完成');
    } catch (error) {
        console.error('视频渲染失败:', error);
        ElMessage.error(`视频渲染失败: ${error.message}`);
    }
};

const exportVideo = async () => {
    try {
        ElMessage.info('正在导出视频...');
        // Add your export logic here
        const data = ffmpeg.FS('readFile', 'output.mp4');
        const blob = new Blob([data.buffer], { type: 'video/mp4' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'exported_video.mp4';
        a.click();
        ElMessage.success('视频导出成功');
    } catch (error) {
        ElMessage.error(`视频导出失败: ${error.message}`);
    }
};
//重置所有编辑
const resetAllPreviews = () => {
    editableFields.value.forEach(field => {
        if (field.previewElementId) {
            removePreviewElement(field.previewElementId);
        }
    });
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

.video-container {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #000;
    overflow: hidden;
    position: relative;
}

#screen-video {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
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
}

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
}</style>
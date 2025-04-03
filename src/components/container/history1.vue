<template>
    <div class="menu-bar k-box-flex">
        <div class="file-upload">
            <input @change="changFile" type="file" id="uploader" placeholder="视频文件">
            <label for="uploader">选择视频文件</label>
        </div>
        <div class="file-upload">
            <input @change="changImage" type="file" id="uploaderImage" placeholder="图片水印">
            <label for="uploaderImage">选择图片水印文件</label>
        </div>
        <div class="file-upload">
            <input @change="changFont" type="file" id="uploaderFont" placeholder="字体文件">
            <label for="uploaderFont">选择字体文件</label>
        </div>
        <!-- <input @change="changCaptions" type="file" id="uploaderCaptions" placeholder="字幕文件"> -->
        <div class="br"></div>
        <input v-model="subtitle" placeholder="标题">
        <input type="color" v-model="fontColor" placeholder="字体颜色">
        <input type="color" v-model="boxColor" placeholder="背景颜色">
        <input v-model="xPosition" placeholder="X位置" style="width: 50px;">
        <input v-model="yPosition" placeholder="Y位置" style="width: 50px;">
    </div>
    <div class="video-screen k-box-flex">
        <video id="screen-video" ref="screenVideo" controls>
            <!-- <track kind="subtitles" src="subtitle.srt" srclang="zh-CH" label="简体中文"> -->
        </video>
    </div>
    <div class="track">
        <img v-for="img in track" :src="img" alt="序列帧">
    </div>
    <div class="message k-text-center">
        {{ message }}
    </div>
    <div class="progress">
        <progress max="1" :value="percent" />用时：{{ eTime }}
    </div>
    <div class="btn-bar k-box-flex">
        <button @click="handleLoad">
            加载视频
        </button>
        <button @click="handleFrame">
            生成序列帧
        </button>
        <!-- <button @click="handleCaptions">
            添加字幕
        </button> -->
        <button @click="handleSubtitle">
            添加标题
        </button>
        <button @click="handleRender">
            添加图片
        </button>
    </div>
    <div>
        <div class="file-info">
            <p>文件名：{{ filename }}</p>
            <p>时长：{{ duration }}</p>
            <p>格式：{{ majorBrand }}</p>
            <p>编码器：{{ encoder }}</p>
            <p>分辨率：{{ resolution }}</p>
            <p>比特率：{{ bitRate }}</p>
            <p>帧率：{{ fps }}</p>
            <p>音频格式：{{ audio }}</p>
            <p>音频采样率：{{ audioRate }}</p>
        </div>
    </div>
</template>

<script setup>
import { clearEmpty } from '@/utils/string.js'
import { createFFmpeg, fetchFile } from '@ffmpeg/ffmpeg'
import { onMounted, reactive, ref } from 'vue'
// 配置
const frameDir = 'frame'


// 变量
let step = ''
// 轨道
const track = ref([])
// 文件名
const filename = ref('')
// 时长
const duration = ref('')
// 格式
const majorBrand = ref('')
// 编码器
const encoder = ref('')
// 分辨率
const resolution = ref('')
// 比特率
const bitRate = ref('')
// 帧率
const fps = ref('')
// 音频格式
const audio = ref('')
// 音频采样率
const audioRate = ref('')
// 输出屏幕图片
const image = ref('')
// 标题
const subtitle = ref('这里是标题文本')
// const fontColor = ref('white') // 默认字体颜色
// const boxColor = ref('black') // 默认背景颜色
const fontColor = ref('#000000'); // 默认字体颜色
const boxColor = ref('#FFFFFF'); // 默认背景颜色
const xPosition = ref(100) // 默认X位置
const yPosition = ref(50) // 默认Y位置
// 进度条
const percent = ref(0)
const eTime = ref('')

const message = ref('')
const ffmpeg = createFFmpeg({
    log: true
})
ffmpeg.setLogger(({ type, message }) => {
    // console.log('日志',type, message);
    /*
     * type can be one of following:
     *
     * info: internal workflow debug messages
     * fferr: ffmpeg native stderr output
     * ffout: ffmpeg native stdout output
     */
    if (type === 'fferr') {
        message = clearEmpty(message)
        // 文件信息处理
        fileInfoFilter(message)
    }
});
ffmpeg.setProgress((progress) => {
    console.log('进度', progress);
    percent.value = progress.ratio
    eTime.value = progress.time
    /*
     * ratio is a float number between 0 to 1.
     */
});
const fileInfoFilter = (message) => {
    // 加载视频时候才处理
    if (step === 'load') {
        if (message.indexOf('Duration') !== -1) {
            duration.value = message.substring(message.indexOf('Duration:') + 'Duration:'.length, message.indexOf('Duration:') + 'Duration:'.length + '00:00:20.48'.length)
            console.log("时长", duration)
        }
        if (message.indexOf('Duration') !== -1 && message.indexOf('bitrate') !== -1) {
            bitRate.value = message.substring(message.indexOf('bitrate:') + 'bitrate:'.length)
            console.log("比特率", bitRate)
        }
        if (message.indexOf('major_brand') !== -1) {
            let key = 'major_brand:'
            majorBrand.value = message.substring(message.indexOf(key) + key.length)
            console.log("格式", majorBrand)
        }
        if (message.indexOf('encoder') !== -1) {
            let key = 'encoder:'
            encoder.value = message.substring(message.indexOf(key) + key.length)
            console.log("编码器", encoder)
        }
        if (message.indexOf('Video:') !== -1) {
            let key = 'Video:'
            let arr = message.substring(message.indexOf(key) + key.length)
            let arrList = arr.split(',')
            console.log("视频信息", arr,)
            resolution.value = arrList[2].substring(0, arrList[2].indexOf('['))
            console.log("分辨率", arr)
            fps.value = arrList[3]
            console.log("帧率", arr)
        }
        if (message.indexOf('Audio:') !== -1) {
            let key = 'Audio:'
            let arr = message.substring(message.indexOf(key) + key.length)
            let arrList = arr.split(',')
            console.log("音频信息", arr,)
            audio.value = arrList[0]
            console.log("音频格式", arr)
            audioRate.value = arrList[1]
            console.log("音频采样率", arr)
        }
    }
}
const screenVideo = ref(null)
let video = ''
onMounted(() => {
    console.log("screenVideo", screenVideo)
})

const changFile = (file) => {
    console.log("选择文件", file.target.files)
    video = file.target.files[0]
    filename.value = video.name
}

// 水印
let watermark = ''
const changImage = async (file) => {
    console.log("选择水印文件", file.target.files)
    watermark = file.target.files[0]
    ffmpeg.FS('writeFile', 'watermark.png', await fetchFile(watermark));
    const data = ffmpeg.FS('readFile', 'watermark.png');
    console.log("文件数据", data)
}

// 字体
const changFont = async (file) => {
    console.log("选择字体文件", file.target.files)
    let font = ''
    font = file.target.files[0]
    ffmpeg.FS('writeFile', 'font.ttf', await fetchFile(font));
    const data = ffmpeg.FS('readFile', 'font.ttf');
    console.log("文件数据", data)
}
//字幕
let captions = null
const changCaptions = async (file) => {
    console.log("选择字幕文件", file.target.files)
    captions = file.target.files[0]

}
const handleLoad = async () => {
    console.log("加载视频", video)
    if (!video) {
        alert('请选择视频')
        return
    }
    if (ffmpeg.isLoaded()) {
        alert('视频已加载')
        return
    }
    step = 'load'
    await ffmpeg.load();
    ffmpeg.FS('writeFile', 'infile', await fetchFile(video));
    await ffmpeg.run('-i', 'infile')
    step = ''
    // 设置视频 URL
    const data = ffmpeg.FS('readFile', 'infile');
    screenVideo.value.src = URL.createObjectURL(new Blob([data.buffer], { type: 'video/mp4' }));
}

const handleRender = async () => {
    console.log('screenVideo', screenVideo)
    if (!ffmpeg.isLoaded()) {
        alert('请加载视频')
        return
    }
    // const fontData = ffmpeg.FS( 'readFile' , 'font' );
    // console.log("文件数据",fontData)
    // const cmd = '-i infile -vf "drawtext=fontsize=60:fontfile=ariali.ttf:text=\'%{localtime\\:%Y\\-%m\\-%d%H-%M-%S}\':fontcolor=green:box=1:boxcolor=yellow" outfile.mp4'
    // 图片水印
    const cmd = '-i infile -vf movie=watermark.png,colorkey=white:0.01:1.0[wm];[in][wm]overlay=30:10[out] outfile.mp4'
    // const cmd = '-re -i infile -vf drawtext=fontsize=60:fontfile=\'font\':text=\'%{localtime\\:%Y\\-%m\\-%d%H-%M-%S}\':fontcolor=green:box=1:boxcolor=yellow outfile.mp4'
    let args = cmd.split(' ')
    console.log('args', args)
    await ffmpeg.run(...args)
    const data = ffmpeg.FS('readFile', 'outfile.mp4');
    console.log("文件数据", data)
    screenVideo.value.src = URL.createObjectURL(new Blob([data.buffer], { type: 'video/mp4' }));
}

const handleFrame = async () => {
    console.log("生成序列帧")
    if (!ffmpeg.isLoaded()) {
        alert('请加载视频')
        return
    }
    ffmpeg.FS('mkdir', frameDir)
    let cmd = '-i infile -r 1 -q:v 2 -f image2 /' + frameDir + '/%3d.jpeg'
    let args = cmd.split(' ')
    console.log('args', args)
    await ffmpeg.run(...args);
    // const data = ffmpeg.FS( 'readFile' , frameDir+'/001.jpeg' );
    // console.log("文件数据",data)
    // image.value = URL.createObjectURL( new Blob( [data.buffer] , { type: 'video/mp4' } ) );
    const fileList = ffmpeg.FS('readdir', '/' + frameDir)
    console.log("文件列表", fileList)
    track.value = []
    fileList.forEach(v => {
        if (v !== '.' && v !== '..') {
            const path = frameDir + '/' + v
            const img = ffmpeg.FS('readFile', path);
            let imgData = URL.createObjectURL(new Blob([img.buffer], { type: 'image/jpeg' }));
            track.value.push(imgData)
        }
    })
    console.log("轨道数据", track)
}

const handleSubtitle = async () => {
    console.log("添加标题", subtitle.value)
    if (!ffmpeg.isLoaded()) {
        alert('请加载视频')
        return
    }
    // 构建FFmpeg命令来添加标题
    const cmd = `-re -i infile -vf drawtext=fontsize=60:fontfile=font.ttf:text='${subtitle.value}':fontcolor=${fontColor.value}:box=1:boxcolor=${boxColor.value}:x=${xPosition.value}:y=${yPosition.value} outfile.mp4`
    let args = cmd.split(' ');
    console.log('args', args)
    await ffmpeg.run(...args)
    const data = ffmpeg.FS('readFile', 'outfile.mp4');
    console.log("文件数据", data)
    screenVideo.value.src = URL.createObjectURL(new Blob([data.buffer], { type: 'video/mp4' }));
}
const handleCaptions = async () => {
    console.log("添加字幕文件");
    if (!ffmpeg.isLoaded()) {
        alert('请加载视频');
        return;
    }
    if (!captions) {
        alert('请选择字幕文件');
        return;
    }
    const captionFile = captions;
    const captionFileName = captionFile.name;
    // 检查文件类型是否为.vtt或.srt
    if (!captionFileName.endsWith('.vtt') && !captionFileName.endsWith('.srt')) {
        alert('字幕文件必须是.vtt或.srt格式');
        return;
    }
    // 将字幕文件读为Uint8Array并写入FFmpeg的文件系统
    const captionArrayBuffer = await captionFile.arrayBuffer();
    ffmpeg.FS('writeFile', captionFileName, new Uint8Array(captionArrayBuffer));

    // 构建FFmpeg命令来添加字幕
    let cmd = `-i infile -vf subtitles=${captionFileName} output_srt.mp4`;
    let args = cmd.split(' ');
    console.log('args', args);
    await ffmpeg.run(...args);

    // 读取输出文件
    const data = ffmpeg.FS('readFile', 'output_srt.mp4');
    console.log("文件数据", data);

    // 更新视频源和字幕轨道
    const videoElement = document.getElementById('screen-video');
    videoElement.src = URL.createObjectURL(new Blob([data.buffer], { type: 'video/mp4' }));
    const trackElement = videoElement.querySelector('track');
    if (trackElement) {
        trackElement.src = URL.createObjectURL(new Blob([captionArrayBuffer], { type: 'text/vtt' }));
    }
};
</script>

<style lang="less" scoped>
.menu-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 5px 10px;
    padding: 10px;
    background-color: #f7f7f7;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.file-upload {
    position: relative;
    display: flex;
    align-items: center;
    background-color: #ffffff;
    border: 2px solid #ccc;
    border-radius: 4px;
    padding: 8px 12px;
    cursor: pointer;
    transition: border-color 0.3s ease-in-out;
}

.file-upload:hover {
    border-color: #007bff;
}

input[type="file"] {
    display: none;
}

label {
    font-weight: bold;
    cursor: pointer;
}

.br {
    width: 100vw;
}

.video-screen {
    width: 100%;
    height: 384px;

    #screen-video {
        width: 100%;
        height: 384px;
    }
}

.out-screen {
    width: 300px;
    height: 240px;

    img {
        max-height: 100%;
        max-width: 100%;
    }
}

.track {
    width: 100%;
    height: 130px;
    overflow-x: scroll;
    white-space: nowrap;

    img {
        display: inline-block;
        width: auto;
        height: 100px;
    }
}
</style>
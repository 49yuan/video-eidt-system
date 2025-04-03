// //代理服务器配置
// import express from 'express';
// const app = express();
// import { readFile } from 'fs';
// import { join } from 'path';
// import cors from 'cors';

// // 允许所有来源的跨域请求
// app.use(cors());
// // 允许所有来源的跨域请求
// app.use((req, res, next) => {
//     res.header('Access-Control-Allow-Origin', '*');
//     next();
// });

// // 代理请求到本地文件
// app.get('/file/*', (req, res) => {
//     const filePath = join(__dirname, 'D:\\2024\\作品集\\组会\\video-edit-system\\video-edit-system\\src\\assets', req.params[0]);
//     readFile(filePath, (err, data) => {
//         if (err) {
//             res.status(404).send('File not found');
//         } else {
//             res.type('text/vtt'); // 或者根据文件类型设置正确的MIME类型
//             res.send(data);
//         }
//     });
// });

// // 监听3000端口
// app.listen(3000, () => {
//     console.log('Proxy server running on port 3000');
// });
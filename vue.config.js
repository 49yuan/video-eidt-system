const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  devServer: {
    port: 8080,
    host: 'localhost', // 只在本地主机上可用
    https: false, // 不使用HTTPS，如果您需要HTTPS，请设置为true并提供证书
    open: true, // 启动时自动打开浏览器
    headers: {
      // 以下设置有助于防止跨域问题
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Embedder-Policy': 'require-corp',
    },
  },
  chainWebpack: (config) => {
    config.plugin('define').tap((definitions) => {
      Object.assign(definitions[0], {
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
      });
      return definitions;
    });
  },
  transpileDependencies: true,
});
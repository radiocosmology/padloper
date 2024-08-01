const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: `${process.env.API_URL || "http://127.0.0.1"}:4300`,
      changeOrigin: true,
    })
  );
};

const { createProxyMiddleware } = require('http-proxy-middleware');

// Dev-only request proxying for `react-scripts start` (CRA dev server on 4301).
// In production these routes are handled by nginx (see nginx.conf); this file
// is NOT included in the production build. It lets the SPA reach the Flask
// backend (4300) and the OAuth proxy server (4000) when running locally
// without Docker/nginx. Override the targets with API_URL / OAUTH_URL.
const API_TARGET = `${process.env.API_URL || "http://127.0.0.1"}:4300`;
const OAUTH_TARGET = `${process.env.OAUTH_URL || "http://127.0.0.1"}:4000`;

module.exports = function(app) {
  // --- Flask backend (/api) ---
  app.use(
    '/api',
    createProxyMiddleware({
      target: API_TARGET,
      changeOrigin: true,
    })
  );
  // Support running the SPA under a base path during local dev
  app.use(
    '/padloper/api',
    createProxyMiddleware({
      target: API_TARGET,
      changeOrigin: true,
      pathRewrite: { '^/padloper': '' },
    })
  );

  // --- OAuth proxy server (/oauth) ---
  // The frontend calls withBase('/oauth/...') = '/padloper/oauth/...'. The
  // oauth-proxy-server exposes those routes without the prefix (e.g.
  // /getAccessToken), so strip the prefix before forwarding to port 4000.
  // Without this, the OAuth login flow 404s under `npm start` (no nginx).
  app.use(
    '/oauth',
    createProxyMiddleware({
      target: OAUTH_TARGET,
      changeOrigin: true,
      pathRewrite: { '^/oauth': '' },
    })
  );
  app.use(
    '/padloper/oauth',
    createProxyMiddleware({
      target: OAUTH_TARGET,
      changeOrigin: true,
      pathRewrite: { '^/padloper/oauth': '' },
    })
  );
};

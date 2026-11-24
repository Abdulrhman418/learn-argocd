FROM nginx:1.27-alpine

COPY --chmod=644 index.html app.js /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
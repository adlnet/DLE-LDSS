FROM nginx:1.19.10

ARG SERVER_NAME

# Move our configuration into place

COPY nginx.conf /etc/nginx/nginx.conf
COPY proxy_headers.conf /etc/nginx/proxy_headers.conf

# Swap our environment variables

RUN cat /etc/nginx/nginx.conf | envsubst '$SERVER_NAME' | tee /tmp/nginx.conf
RUN mv /tmp/nginx.conf /etc/nginx/nginx.conf
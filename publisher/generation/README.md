## Build instructions:

docker buildx build . -t xxxx/generate-article --platform linux/amd64 && \
docker save xxxx/generate-article | bzip2 | pv |  ssh xxx@xxx.local docker load
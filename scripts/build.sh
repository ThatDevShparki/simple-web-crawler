# Poetry update
poetry update
poetry export -f requirements.txt --without-hashes > requirements.txt

# Docker build
export DOCKER_BUILDKIT=1 
docker build -t r2c-demo-webcrawler .
.PHONY: help docker-build docker-bb-test docker-test test

# Configurable variables
IMAGE_TAG ?= tin2dem-dev
DOCKERFILE ?= docker/Dockerfile
BUILD_ARGS ?=

help:
	@echo "Targets:"
	@echo "  docker-build    - Build Docker image (runs unit tests during build)"
	@echo "  docker-bb-test  - Run black-box tests against built image"
	@echo "  docker-test     - Build then run Docker black-box tests"
	@echo "  test            - Run local pytest suite"
	@echo ""
	@echo "Variables:"
	@echo "  IMAGE_TAG   (default: tin2dem-dev)"
	@echo "  DOCKERFILE  (default: docker/Dockerfile)"
	@echo "  BUILD_ARGS  (extra args for docker build, e.g. --progress=plain)"

docker-build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_TAG) $(BUILD_ARGS) .

docker-bb-test:
	$(MAKE) -C black-box-test clean test CMD="./indocker.sh $(IMAGE_TAG)"

docker-test: docker-build docker-bb-test

test:
	python3 -m pytest tests -vv --tb=short --durations=10



.PHONY: help lint test docker-build-cpu docker-build-gpu docker-bb-test-cpu docker-bb-test-gpu docker-test-cpu docker-test-gpu docker-push-cpu docker-push-gpu docker-push

# Configurable variables
DOCKERHUB_REPO ?= lekkks/tin2dem
BUILD_ARGS ?=

# Extract app version from setup.py (works with version = "X.Y.Z" or version="X.Y.Z")
APP_VERSION := $(shell grep -E '^\s*version\s*=' setup.py | sed -E "s/.*version\s*=\s*[\"']([^\"']+)[\"'].*/\1/" | head -1)

# Read Dockerfile versions
DOCKERFILE_VERSION_CPU := $(shell cat docker/VERSION.cpu 2>/dev/null || echo "1")
DOCKERFILE_VERSION_GPU := $(shell cat docker/VERSION.gpu 2>/dev/null || echo "1")

# Construct image tags (only full version and latest)
IMAGE_TAG_CPU_FULL := $(DOCKERHUB_REPO):$(APP_VERSION)-docker$(DOCKERFILE_VERSION_CPU)-cpu
IMAGE_TAG_GPU_FULL := $(DOCKERHUB_REPO):$(APP_VERSION)-docker$(DOCKERFILE_VERSION_GPU)-gpu
IMAGE_TAG_CPU_LATEST := $(DOCKERHUB_REPO):latest-cpu
IMAGE_TAG_GPU_LATEST := $(DOCKERHUB_REPO):latest-gpu

# Local dev tags (for testing only, not pushed)
IMAGE_TAG_CPU ?= tin2dem-cpu
IMAGE_TAG_GPU ?= tin2dem-gpu

help:
	@echo "Targets:"
	@echo "  docker-build-cpu - Build CPU image (POCL)"
	@echo "  docker-build-gpu - Build GPU image (no vendor ICDs)"
	@echo "  docker-bb-test-cpu - Black-box test CPU image"
	@echo "  docker-bb-test-gpu - Black-box test GPU image (requires GPU runtime)"
	@echo "  docker-test-cpu - Build then run Docker black-box tests (CPU)"
	@echo "  docker-test-gpu - Build then run Docker black-box tests (GPU)"
	@echo "  docker-push-cpu - Push CPU image to Docker Hub with all tags"
	@echo "  docker-push-gpu - Push GPU image to Docker Hub with all tags"
	@echo "  docker-push - Push both CPU and GPU images"
	@echo "  lint            - Run flake8 linter on Python code"
	@echo "  test            - Run local pytest suite"
	@echo ""
	@echo "Variables:"
	@echo "  DOCKERHUB_REPO (default: lekkks/tin2dem)"
	@echo "  IMAGE_TAG_CPU (default: tin2dem-cpu, for local dev only)"
	@echo "  IMAGE_TAG_GPU (default: tin2dem-gpu, for local dev only)"
	@echo "  BUILD_ARGS  (extra args for docker build, e.g. --progress=plain)"
	@echo ""
	@echo "Current versions:"
	@echo "  App version: $(APP_VERSION)"
	@echo "  Dockerfile CPU version: $(DOCKERFILE_VERSION_CPU)"
	@echo "  Dockerfile GPU version: $(DOCKERFILE_VERSION_GPU)"
	@echo "  CPU tags: $(IMAGE_TAG_CPU_FULL) $(IMAGE_TAG_CPU_LATEST)"
	@echo "  GPU tags: $(IMAGE_TAG_GPU_FULL) $(IMAGE_TAG_GPU_LATEST)"

lint:
	python3 -m flake8 tin2dem tests tools

test:
	python3 -m pytest tests -vv --tb=short --durations=10

# CPU/GPU specific targets
docker-build-cpu:
	docker build -f docker/Dockerfile.cpu \
		-t $(IMAGE_TAG_CPU) \
		-t $(IMAGE_TAG_CPU_FULL) \
		-t $(IMAGE_TAG_CPU_LATEST) \
		$(BUILD_ARGS) .

docker-build-gpu:
	docker build -f docker/Dockerfile.gpu \
		-t $(IMAGE_TAG_GPU) \
		-t $(IMAGE_TAG_GPU_FULL) \
		-t $(IMAGE_TAG_GPU_LATEST) \
		$(BUILD_ARGS) .

docker-bb-test-cpu:
	$(MAKE) -C black-box-test clean test CMD="./indocker.sh $(IMAGE_TAG_CPU)"

docker-bb-test-gpu:
	$(MAKE) -C black-box-test clean test CMD="./indocker.sh --gpu --mount-vendors $(IMAGE_TAG_GPU)"

docker-test-cpu: docker-build-cpu docker-bb-test-cpu

docker-test-gpu: docker-build-gpu docker-bb-test-gpu

# Push targets
docker-push-cpu: docker-build-cpu
	docker push $(IMAGE_TAG_CPU_FULL)
	docker push $(IMAGE_TAG_CPU_LATEST)

docker-push-gpu: docker-build-gpu
	docker push $(IMAGE_TAG_GPU_FULL)
	docker push $(IMAGE_TAG_GPU_LATEST)

docker-push: docker-push-cpu docker-push-gpu



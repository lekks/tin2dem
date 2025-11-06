.PHONY: help test docker-build-cpu docker-build-gpu docker-bb-test-cpu docker-bb-test-gpu docker-test-cpu docker-test-gpu

# Configurable variables
IMAGE_TAG_CPU ?= tin2dem-cpu
IMAGE_TAG_GPU ?= tin2dem-gpu
BUILD_ARGS ?=

help:
	@echo "Targets:"
	@echo "  docker-build-cpu - Build CPU image (POCL)"
	@echo "  docker-build-gpu - Build GPU image (no vendor ICDs)"
	@echo "  docker-bb-test-cpu - Black-box test CPU image"
	@echo "  docker-bb-test-gpu - Black-box test GPU image (requires GPU runtime)"
	@echo "  docker-test-cpu - Build then run Docker black-box tests (CPU)"
	@echo "  docker-test-gpu - Build then run Docker black-box tests (GPU)"
	@echo "  test            - Run local pytest suite"
	@echo ""
	@echo "Variables:"
	@echo "  IMAGE_TAG_CPU (default: tin2dem-cpu)"
	@echo "  IMAGE_TAG_GPU (default: tin2dem-gpu)"
	@echo "  BUILD_ARGS  (extra args for docker build, e.g. --progress=plain)"

test:
	python3 -m pytest tests -vv --tb=short --durations=10

# CPU/GPU specific targets
docker-build-cpu:
	docker build -f docker/Dockerfile.cpu -t $(IMAGE_TAG_CPU) $(BUILD_ARGS) .

docker-build-gpu:
	docker build -f docker/Dockerfile.gpu -t $(IMAGE_TAG_GPU) $(BUILD_ARGS) .

docker-bb-test-cpu:
	$(MAKE) -C black-box-test clean test CMD="./indocker.sh $(IMAGE_TAG_CPU)"

docker-bb-test-gpu:
	$(MAKE) -C black-box-test clean test CMD="./indocker.sh --gpu --mount-vendors $(IMAGE_TAG_GPU)"

docker-test-cpu: docker-build-cpu docker-bb-test-cpu

docker-test-gpu: docker-build-gpu docker-bb-test-gpu



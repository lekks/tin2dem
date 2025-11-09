#!/bin/bash

#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 [--gpu] [--mount-vendors] <docker_tag> <input_file> <output_file> [extra_args...]"
    echo ""
    echo "  --gpu            Add NVIDIA GPU flags (equiv to: --gpus all)."
    echo "  --mount-vendors  Bind-mount host /etc/OpenCL/vendors to /host-ocl-vendors and include in OCL_ICD_VENDORS."
    echo "  <docker_tag>     The Docker image tag to use (e.g., tin2dem-gpu:latest)."
    echo "  <input_file>     Path to the input XML file."
    echo "  <output_file>    Name of the output file to be created in the current directory."
    echo "  [extra_args...]  Optional additional arguments to pass to the tin2dem tool."
    echo ""
    echo "Examples:"
    echo "  $0 tin2dem-cpu:latest path/to/input.xml output.dem"
    echo "  $0 --gpu --mount-vendors tin2dem-gpu:latest path/to/input.xml output.dem --verbose"
    exit 1
}

# Parse optional flags
GPU_FLAGS=""
EXTRA_ENV=()
EXTRA_VOLUMES=()

while [[ "$1" == --* ]]; do
    case "$1" in
        --gpu)
            GPU_FLAGS="--gpus all"
            shift
            ;;
        --mount-vendors)
            EXTRA_VOLUMES+=("-v" "/etc/OpenCL/vendors:/host-ocl-vendors:ro")
            # Point loader to a single directory to avoid misinterpretation
            EXTRA_ENV+=("-e" "OCL_ICD_VENDORS=/host-ocl-vendors")
            shift
            ;;
        *)
            usage
            ;;
    esac
done

# Check if the correct number of arguments is provided after flags
if [ "$#" -lt 3 ]; then
    usage
fi

# Assign arguments to variables for clarity
DOCKER_TAG=$1
INPUT_FILE=$2
OUTPUT_FILE=$3
shift 3
EXTRA_ARGS="$@"

# Check if the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found."
    exit 1
fi

set -xe

# Run Docker, using the tag from the first parameter
docker run -it --rm \
    $GPU_FLAGS \
    "${EXTRA_ENV[@]}" \
    -v "$(realpath "$INPUT_FILE")":/var/input.xml \
    -v "$(pwd)":/var/output/ \
    "${EXTRA_VOLUMES[@]}" \
    "$DOCKER_TAG" \
    /var/input.xml /var/output/"$OUTPUT_FILE" $EXTRA_ARGS
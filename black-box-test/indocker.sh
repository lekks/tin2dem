#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 <docker_tag> <input_file> <output_file>"
    echo ""
    echo "  <docker_tag>   The Docker image tag to use (e.g., tin2dem-ta:latest)."
    echo "  <input_file>   Path to the input XML file."
    echo "  <output_file>  Name of the output file to be created in the current directory."
    echo ""
    echo "Example:"
    echo "  $0 tin2dem-ta:latest path/to/input.xml output.dem"
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    usage
fi

# Assign arguments to variables for clarity
DOCKER_TAG=$1
INPUT_FILE=$2
OUTPUT_FILE=$3

# Check if the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found."
    exit 1
fi

set -xe

# Run Docker, using the tag from the first parameter
docker run -it --rm \
    -v "$(realpath $INPUT_FILE)":/var/input.xml \
    -v "$(pwd)":/var/output/ \
    --entrypoint /usr/local/bin/tin2dem \
    "$DOCKER_TAG" \
    /var/input.xml /var/output/"$OUTPUT_FILE"
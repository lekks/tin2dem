# Format Converter Test Framework
# Usage:
#   make expected CMD="tin2dem"           # Generate expected results
#   make expected CMD="docker run ..."    # Using docker
#   make test CMD="./new_tin2dem"         # Test against expected results
#   make test CMD="tin2dem" MAX_DIFF=0.01 MAX_STD=0.005  # With custom thresholds

# Default conversion command
CMD ?= tin2dem

# Comparison thresholds (0 = no limit)
MAX_DIFF ?= 0.0
MAX_STD ?= 0.0

# Directories
INPUT_DIR := input
EXPECTED_DIR := expected
OUTPUT_DIR := output

# Find all XML files in input directory
XML_FILES := $(wildcard $(INPUT_DIR)/*.xml)

# Generate corresponding TIF file paths
EXPECTED_TIFS := $(patsubst $(INPUT_DIR)/%.xml,$(EXPECTED_DIR)/%.tif,$(XML_FILES))
OUTPUT_TIFS := $(patsubst $(INPUT_DIR)/%.xml,$(OUTPUT_DIR)/%.tif,$(XML_FILES))

# Ensure directories exist
$(shell mkdir -p $(EXPECTED_DIR) $(OUTPUT_DIR))

# Default target - show help
.PHONY: help
help:
	@echo "Format Converter Test Framework"
	@echo ""
	@echo "Available targets:"
	@echo "  make expected CMD=<command>  - Generate expected results from input/*.xml"
	@echo "  make test CMD=<command>      - Test new converter against expected results"
	@echo "  make clean                   - Remove output directory"
	@echo "  make clean-all               - Remove both expected and output directories"
	@echo ""
	@echo "Parameters:"
	@echo "  CMD=<command>                - Conversion command (default: tin2dem)"
	@echo "  MAX_DIFF=<value>             - Max pixel difference threshold (default: 0.0)"
	@echo "  MAX_STD=<value>              - Max std deviation threshold (default: 0.0)"
	@echo ""
	@echo "Examples:"
	@echo "  make expected CMD=\"tin2dem\""
	@echo "  make test CMD=\"./new_converter\""
	@echo "  make test CMD=\"tin2dem\" MAX_DIFF=0.001 MAX_STD=0.005"

# Generate expected results
.PHONY: expected
expected: $(EXPECTED_TIFS)
	@echo "✓ Generated $(words $(EXPECTED_TIFS)) expected result(s)"

# Pattern rule for generating expected TIF files
$(EXPECTED_DIR)/%.tif: $(INPUT_DIR)/%.xml
	@echo "Generating expected: $@"
	$(CMD) $< $@

# Run tests against expected results
.PHONY: test
test: $(OUTPUT_TIFS)
	@echo "Running comparisons..."
	@$(MAKE) --no-print-directory compare-all
	@echo "✓ All tests passed!"

# Pattern rule for generating output TIF files
$(OUTPUT_DIR)/%.tif: $(INPUT_DIR)/%.xml
	@echo "Converting: $< -> $@"
	$(CMD) $< $@

# Compare all output files against expected
.PHONY: compare-all
compare-all: $(OUTPUT_TIFS)
	@for xml in $(XML_FILES); do \
		base=$$(basename "$$xml" .xml); \
		echo "Comparing $$base.tif..."; \
		python compare_tiff.py \
			"$(EXPECTED_DIR)/$$base.tif" \
			"$(OUTPUT_DIR)/$$base.tif" \
			--max-diff $(MAX_DIFF) \
			--max-std $(MAX_STD) || exit 1; \
	done

# Clean output directory
.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)
	mkdir -p $(OUTPUT_DIR)
	@echo "✓ Cleaned output directory"

# Clean everything
.PHONY: clean-all
clean-all:
	rm -rf $(EXPECTED_DIR) $(OUTPUT_DIR)
	mkdir -p $(EXPECTED_DIR) $(OUTPUT_DIR)
	@echo "✓ Cleaned all generated files"

# Show what would be processed
.PHONY: list
list:
	@echo "Input XML files:"
	@for f in $(XML_FILES); do echo "  $$f"; done
	@echo ""
	@echo "Expected TIF files:"
	@for f in $(EXPECTED_TIFS); do echo "  $$f"; done
# Format Converter Testing Framework

A simple, robust testing framework for validating format converters (e.g., XML to TIFF) using pixel-perfect comparison.

## Quick Start

```bash
# 1. Put your test XML files in the input/ directory
cp my_test_files/*.xml input/

# 2. Generate expected/baseline results
make expected CMD="tin2dem"

# 3. Test a new converter implementation
make test CMD="./new_tin2dem"
```

You can also pass extra arguments to the conversion command:

```bash
make expected CMD="tin2dem" EXTRA_ARGS="-a --pixel 0.5"
make test CMD="./new_tin2dem" EXTRA_ARGS="--surface 1"
```

## Directory Structure

```
.
├── Makefile              # Test automation
├── compare_tiff.py       # TIFF comparison tool
├── input/                # Your test XML files go here
├── expected/             # Generated baseline TIFF files
└── output/               # Generated test TIFF files
```

## Testing Workflow

### Step 1: Prepare Test Data

Place your XML test files in the `input/` directory:

```bash
mkdir -p input
cp /path/to/test/files/*.xml input/
```

### Step 2: Generate Expected Results

Clean all generated date:

```bash
make clean-all
```

Run your **known-good converter** to generate baseline results:

```bash
make expected CMD="tin2dem"
```

Or with Docker:

```bash
make expected CMD="./indocker.sh lekkks/tin2dem:0.3.1-docker1-cpu"
 ```

This will:
- Process all `*.xml` files in `input/`
- Generate corresponding `.tif` files in `expected/`
- These become your "golden" reference files

### Step 3: Test New Implementation

Test your new converter against the baseline:

```bash
make test CMD="./new_tin2dem"
```

This will:
- Convert all XML files using your new command
- Generate `.tif` files in `output/`
- Compare each output with its corresponding expected file
- Report statistics and pass/fail for each file

### Step 4: Review Results

The comparison tool reports:
- **Total pixels** processed
- **Different pixels** count and percentage
- **Max pixel difference** across all pixels
- **Mean difference** of differing pixels
- **Standard deviation** of differences

Example output:
```
Comparing: 1024x768 pixels, 1 band(s)
  Band 1/1... done

Comparison Results:
  Total pixels:        786,432
  Different pixels:    234 (0.03%)
  Max pixel diff:      0.001523
  Mean diff:           0.000847
  Std deviation:       0.000312

✓ PASS: Files match within tolerance
```

## Advanced Usage

### Custom Tolerance Thresholds

Set maximum allowed differences:

```bash
make test CMD="./new_converter" MAX_DIFF=0.001 MAX_STD=0.005
```

- `MAX_DIFF` - Maximum allowed pixel difference (any single pixel)
- `MAX_STD` - Maximum allowed standard deviation of all differences
- Set to `0.0` for no limit (default)

You can also edit the Makefile to set permanent defaults:

```makefile
MAX_DIFF ?= 0.001
MAX_STD ?= 0.005
```

### Extra Arguments

Pass additional arguments to the conversion command:

```bash
make expected CMD="tin2dem" EXTRA_ARGS="-a --pixel 0.5"
make test CMD="./new_converter" EXTRA_ARGS="--surface 1 --chunk 512"
```

- `EXTRA_ARGS` - Additional command-line arguments (default: empty)
- Useful for testing different options or configurations

### Docker Example

```bash
# Generate expected
make expected CMD="docker run --rm -v \$(pwd):/data my-converter:v1.0 process"

# Test new version
make test CMD="docker run --rm -v \$(pwd):/data my-converter:v2.0 process" \
          MAX_DIFF=0.01
```

### Testing Specific Files

The framework automatically processes all `*.xml` files in `input/`. To test specific files:

```bash
# Move unwanted files temporarily
mkdir temp
mv input/large_file.xml temp/

# Run test
make test CMD="./converter"

# Restore files
mv temp/*.xml input/
```

## Available Commands

### `make expected`

Generate baseline/expected results from input XML files.

**Parameters:**
- `CMD` - Conversion command (required for first run, default: `tin2dem`)
- `EXTRA_ARGS` - Extra arguments to pass to CMD (default: empty)

**Example:**
```bash
make expected CMD="tin2dem"
make expected CMD="tin2dem" EXTRA_ARGS="-a --pixel 0.5"
```

### `make test`

Test a converter implementation against expected results.

**Parameters:**
- `CMD` - Conversion command (default: `tin2dem`)
- `EXTRA_ARGS` - Extra arguments to pass to CMD (default: empty)
- `MAX_DIFF` - Max pixel difference threshold (default: `0.0`)
- `MAX_STD` - Max standard deviation threshold (default: `0.0`)

**Example:**
```bash
make test CMD="./new_converter" MAX_DIFF=0.001 MAX_STD=0.005
make test CMD="./new_converter" EXTRA_ARGS="--surface 1" MAX_DIFF=0.001
```

### `make clean`

Remove the `output/` directory to start fresh for testing.

```bash
make clean
```

### `make clean-all`

Remove both `expected/` and `output/` directories. Use this to completely reset.

```bash
make clean-all
```

### `make list`

Show all files that will be processed.

```bash
make list
```

### `make help`

Display help information with available commands and examples.

```bash
make help
```

## Comparison Tool Details

The `compare_tiff.py` script can also be used standalone:

```bash
python compare_tiff.py expected/file.tif output/file.tif --max-diff 0.001
```

### Features

- **Memory efficient** - Reads files line-by-line, not all at once
- **Multi-band support** - Handles single or multi-band TIFF files
- **Detailed statistics** - Reports comprehensive comparison metrics
- **Configurable thresholds** - Set pass/fail criteria
- **Validates dimensions** - Ensures files are same size before comparing

### Error Handling

The comparison fails if:
- Files don't exist
- Dimensions don't match
- Band counts don't match
- Max pixel difference exceeds `--max-diff` threshold
- Standard deviation exceeds `--max-std` threshold

## Tips and Best Practices

### 1. Version Control Your Baselines

Keep `expected/` in version control to track changes:

```bash
git add expected/
git commit -m "Update baseline results for v2.0"
```

### 2. Test Incrementally

Start with a few simple test cases, then add more complex ones:

```bash
# Start small
cp simple_test.xml input/
make expected CMD="tin2dem"
make test CMD="./new_converter"

# Add more tests
cp complex_*.xml input/
make expected CMD="tin2dem"
make test CMD="./new_converter"
```

### 3. Adjust Thresholds Based on Use Case

- **Exact match required**: Keep defaults (`MAX_DIFF=0.0`)
- **Floating-point tolerance**: Use small thresholds (e.g., `MAX_DIFF=0.0001`)
- **Lossy conversions**: Use larger thresholds (e.g., `MAX_DIFF=0.01`)

### 4. Investigate Failures

When tests fail, examine the statistics:

- **High max diff, low std dev** - Likely a few outlier pixels
- **Low max diff, high std dev** - Systematic difference across many pixels
- **High mean diff** - Overall brightness/offset difference

### 5. Keep Test Data Manageable

- Use representative samples, not your entire dataset
- Include edge cases (empty files, maximum sizes, special features)
- Document what each test file is testing


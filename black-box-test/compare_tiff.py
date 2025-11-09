#!/usr/bin/env python3
"""
TIFF comparison tool - compares two TIFF files pixel by pixel.
Uses line-by-line reading for memory efficiency.
"""

import sys
import argparse
import numpy as np
from osgeo import gdal


def compare_tiffs(expected_path, actual_path, max_diff=0.0, max_std=0.0):
    """
    Compare two TIFF files pixel by pixel.
    
    Args:
        expected_path: Path to expected TIFF file
        actual_path: Path to actual TIFF file
        max_diff: Maximum allowed pixel difference (fails if exceeded)
        max_std: Maximum allowed standard deviation (fails if exceeded)
    
    Returns:
        Dictionary with comparison statistics
    """
    # Open both files
    expected_ds = gdal.Open(expected_path, gdal.GA_ReadOnly)
    actual_ds = gdal.Open(actual_path, gdal.GA_ReadOnly)
    
    if expected_ds is None:
        raise FileNotFoundError(f"Cannot open expected file: {expected_path}")
    if actual_ds is None:
        raise FileNotFoundError(f"Cannot open actual file: {actual_path}")
    
    # Check dimensions match
    if expected_ds.RasterXSize != actual_ds.RasterXSize or \
       expected_ds.RasterYSize != actual_ds.RasterYSize:
        raise ValueError(
            f"Dimension mismatch: expected {expected_ds.RasterXSize}x{expected_ds.RasterYSize}, "
            f"got {actual_ds.RasterXSize}x{actual_ds.RasterYSize}"
        )
    
    # Check band count matches
    if expected_ds.RasterCount != actual_ds.RasterCount:
        raise ValueError(
            f"Band count mismatch: expected {expected_ds.RasterCount}, "
            f"got {actual_ds.RasterCount}"
        )
    
    width = expected_ds.RasterXSize
    height = expected_ds.RasterYSize
    num_bands = expected_ds.RasterCount
    
    print(f"Comparing: {width}x{height} pixels, {num_bands} band(s)")
    
    # Statistics accumulators
    all_diffs = []
    max_pixel_diff = 0.0
    
    # Process band by band
    for band_idx in range(1, num_bands + 1):
        expected_band = expected_ds.GetRasterBand(band_idx)
        actual_band = actual_ds.GetRasterBand(band_idx)
        
        print(f"  Band {band_idx}/{num_bands}...", end=" ", flush=True)
        
        # Read line by line for memory efficiency
        for row in range(height):
            # Read one row from each file
            expected_line = expected_band.ReadAsArray(0, row, width, 1).flatten()
            actual_line = actual_band.ReadAsArray(0, row, width, 1).flatten()
            
            # Calculate differences for this line
            diff = np.abs(expected_line.astype(float) - actual_line.astype(float))
            
            # Update statistics
            line_max = np.max(diff)
            if line_max > max_pixel_diff:
                max_pixel_diff = line_max
            
            # Store differences for std calculation (only non-zero for efficiency)
            non_zero_diffs = diff[diff > 0]
            if len(non_zero_diffs) > 0:
                all_diffs.extend(non_zero_diffs)
        
        print("done")
    
    # Calculate final statistics
    if len(all_diffs) > 0:
        std_dev = np.std(all_diffs)
        mean_diff = np.mean(all_diffs)
        num_different = len(all_diffs)
    else:
        std_dev = 0.0
        mean_diff = 0.0
        num_different = 0
    
    total_pixels = width * height * num_bands
    
    # Print statistics
    print("\nComparison Results:")
    print(f"  Total pixels:        {total_pixels:,}")
    print(f"  Different pixels:    {num_different:,} ({100.0 * num_different / total_pixels:.2f}%)")
    print(f"  Max pixel diff:      {max_pixel_diff:.6f}")
    print(f"  Mean diff:           {mean_diff:.6f}")
    print(f"  Std deviation:       {std_dev:.6f}")
    
    # Check against thresholds
    failed = False
    
    if max_diff > 0 and max_pixel_diff > max_diff:
        print(f"\n✗ FAIL: Max pixel difference {max_pixel_diff:.6f} exceeds threshold {max_diff:.6f}")
        failed = True
    
    if max_std > 0 and std_dev > max_std:
        print(f"\n✗ FAIL: Standard deviation {std_dev:.6f} exceeds threshold {max_std:.6f}")
        failed = True
    
    if not failed:
        print("\n✓ PASS: Files match within tolerance")
    
    # Cleanup
    expected_ds = None
    actual_ds = None
    
    return {
        'max_diff': max_pixel_diff,
        'std_dev': std_dev,
        'mean_diff': mean_diff,
        'num_different': num_different,
        'total_pixels': total_pixels,
        'passed': not failed
    }


def main():
    parser = argparse.ArgumentParser(
        description='Compare two TIFF files pixel by pixel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s expected.tif output.tif
  %(prog)s expected.tif output.tif --max-diff 0.001
  %(prog)s expected.tif output.tif --max-diff 0.01 --max-std 0.005
        """
    )
    
    parser.add_argument('expected', help='Path to expected TIFF file')
    parser.add_argument('actual', help='Path to actual TIFF file')
    parser.add_argument('--max-diff', type=float, default=0.0,
                        help='Maximum allowed pixel difference (0 = no limit)')
    parser.add_argument('--max-std', type=float, default=0.0,
                        help='Maximum allowed standard deviation (0 = no limit)')
    
    args = parser.parse_args()
    
    try:
        result = compare_tiffs(args.expected, args.actual, args.max_diff, args.max_std)
        
        if not result['passed']:
            sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
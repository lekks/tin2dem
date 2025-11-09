# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1]

### Added
- Black box testing suite for comprehensive validation
- Versioned Docker support with separate CPU and GPU images for better efficiency
- Root level Makefile
- Add flake8 linker

### Changed
- Updated pyopencl version

### Fixed
- Added missing ENTRYPOINT in Dockerfile
- Cached OpenCL kernels to avoid repeated retrieval overhead and warnings
- Fixed flake8 warnings

## [0.3.0]
- Initial release
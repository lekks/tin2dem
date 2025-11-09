# Contributing to tin2dem

## Docker Image Versioning and Release Process

### Versioning System

The project uses a dual versioning system:
- **App version**: Extracted from `setup.py` (e.g., `0.3.1`)
- **Dockerfile version**: Stored in `docker/VERSION.cpu` and `docker/VERSION.gpu` (e.g., `1`)

### Image Tag Naming Convention

Images are tagged with the format: `{repo}:{app-version}-docker{dockerfile-version}-{variant}`

**Examples:**
- `lekkks/tin2dem:0.3.1-docker1-cpu` - Full version tag (app + Dockerfile)
- `lekkks/tin2dem:0.3.1-docker1-gpu` - Full version tag (app + Dockerfile)
- `lekkks/tin2dem:latest-cpu` - Latest tag (points to latest app + latest Dockerfile)
- `lekkks/tin2dem:latest-gpu` - Latest tag (points to latest app + latest Dockerfile)

### Building Images

Build images with all version tags:

```bash
make docker-build-cpu   # Builds CPU image with all tags
make docker-build-gpu   # Builds GPU image with all tags
```

The build process automatically:
1. Extracts app version from `setup.py`
2. Reads Dockerfile versions from `docker/VERSION.cpu` and `docker/VERSION.gpu`
3. Creates all appropriate tags

To see current versions and tags:
```bash
make help
```

### When to Increment Versions

**App Version (in `setup.py`):**
- Increment when the tin2dem tool itself changes (new features, bug fixes, etc.)
- Follow semantic versioning (MAJOR.MINOR.PATCH)

**Dockerfile Version (in `docker/VERSION.cpu` or `docker/VERSION.gpu`):**
- Increment when the Dockerfile changes (base image updates, dependency changes, build process changes)
- Increment independently for CPU and GPU if only one changes
- Start at `1` for new Dockerfiles

**Example scenarios:**
- New tin2dem feature → increment app version, keep Dockerfile version
- Update Debian base image → keep app version, increment Dockerfile version
- Both change → increment both

### Pushing to Docker Hub

**Prerequisites:**
- Logged into Docker Hub: `docker login`
- Set `DOCKERHUB_REPO` if using a different repository name (default: `lekkks/tin2dem`)

**Push images:**

```bash
# Push CPU image (pushes all CPU tags)
make docker-push-cpu

# Push GPU image (pushes all GPU tags)
make docker-push-gpu

# Push both images
make docker-push
```

This will push:
- Full version tags (e.g., `lekkks/tin2dem:0.3.1-docker1-cpu`)
- Latest tags (e.g., `lekkks/tin2dem:latest-cpu`)

### Release Workflow

1. **Update app version** (if needed):
   ```bash
   # Edit setup.py and update version = "X.Y.Z"
   ```

2. **Update Dockerfile versions** (if Dockerfiles changed):
   ```bash
   # Edit docker/VERSION.cpu and/or docker/VERSION.gpu
   ```

3. **Build and test**:
   ```bash
   make docker-test-cpu    # Build and test CPU image
   make docker-test-gpu    # Build and test GPU image
   ```

4. **Push to Docker Hub**:
   ```bash
   make docker-push        # Push both images
   ```

### Local Development

For local development and testing, images are also tagged with simple names:
- `tin2dem-cpu` - Local CPU image
- `tin2dem-gpu` - Local GPU image

These tags are used by the test suite and don't get pushed to Docker Hub.

### Custom Docker Hub Repository

The default repository is `lekkks/tin2dem`. To use a different Docker Hub repository:

```bash
make docker-build-cpu DOCKERHUB_REPO=yourusername/tin2dem
make docker-push-cpu DOCKERHUB_REPO=yourusername/tin2dem
```


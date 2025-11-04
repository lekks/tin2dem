FROM ubuntu:24.04 as production

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    PATH=$PATH:/root/.local/bin \
    TERM=dumb \
    PYOPENCL_CTX=0 \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

ARG GIT_COMMIT=v6.0
ARG GH_PR
ARG GH_SLUG=pocl/pocl
ARG LLVM_VERSION=18

LABEL git-commit=$GIT_COMMIT vendor=pocl distro=Ubuntu version=1.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        software-properties-common \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        gdal-bin \
        python3-gdal \
        libgdal-dev \
        pipx \
        tzdata \
        cmake \
        git \
        pkg-config \
        libclang-${LLVM_VERSION}-dev \
        clang-${LLVM_VERSION} \
        libclang-cpp${LLVM_VERSION}-dev \
        llvm-${LLVM_VERSION}-dev \
        make \
        ninja-build \
        ocl-icd-libopencl1 \
        ocl-icd-dev \
        ocl-icd-opencl-dev \
        libhwloc-dev \
        zlib1g \
        zlib1g-dev \
        dialog \
        apt-utils \
    && rm -rf /var/lib/apt/lists/*

RUN cd /home && git clone https://github.com/${GH_SLUG}.git \
    && cd /home/pocl && git checkout ${GIT_COMMIT} \
    && if [ -n "${GH_PR}" ]; then git fetch origin +refs/pull/${GH_PR}/merge && git checkout -qf FETCH_HEAD; fi \
    && mkdir b && cd b \
    && cmake -G Ninja -DWITH_LLVM_CONFIG=/usr/bin/llvm-config-${LLVM_VERSION} -DCMAKE_INSTALL_PREFIX=/usr .. \
    && ninja install \
    && rm -f CTestCustom.cmake

WORKDIR /opt/tin2dem
COPY . /opt/tin2dem
RUN pip3 install --break-system-packages /opt/tin2dem

FROM production as testing

WORKDIR /tin2dem-tests

RUN pip3 install --break-system-packages pytest
COPY tests/ tests/
RUN python3 -m pytest tests -vv -s --tb=short --durations=10 --junit-xml=/tmp/test-results.xml

FROM production
# Copy test report from testing stage to ensure tests ran and passed
COPY --from=testing /tmp/test-results.xml /tmp/test-results.xml

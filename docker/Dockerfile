FROM debian:bookworm-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    PATH=$PATH:/root/.local/bin \
    TERM=dumb

LABEL vendor=tin2dem base=debian variant=builder version=1.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/tin2dem
COPY . /opt/tin2dem
# Build a wheel for tin2dem without resolving deps (installed later in runtime)
RUN pip3 wheel --no-deps --no-cache-dir -w /opt/wheels /opt/tin2dem

FROM debian:bookworm-slim AS testing

WORKDIR /tin2dem-tests

ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC
# gdal-bin is optional but small and can be useful for debug
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-gdal \
        gdal-bin \
        ocl-icd-libopencl1 \
        pocl-opencl-icd \
        tzdata \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/wheels /opt/wheels
RUN pip3 install --break-system-packages --no-cache-dir /opt/wheels/*.whl pytest
COPY tests/ tests/
ENV PYOPENCL_CTX=0
RUN python3 -m pytest tests -vv -s --tb=short --durations=10 --junit-xml=/tmp/test-results.xml

FROM debian:bookworm-slim AS production

ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC PYOPENCL_CTX=0
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-gdal \
        ocl-icd-libopencl1 \
        pocl-opencl-icd \
        tzdata \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/wheels /opt/wheels
RUN pip3 install --break-system-packages --no-cache-dir /opt/wheels/*.whl
COPY --from=testing /tmp/test-results.xml /tmp/test-results.xml
ENTRYPOINT ["/usr/local/bin/tin2dem"]

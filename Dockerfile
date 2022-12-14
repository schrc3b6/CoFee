# syntax=docker/dockerfile:1
FROM debian:bullseye-backports as llvm-build
RUN apt update && apt upgrade -y
RUN apt install -y \
	build-essential \
	gcc \
	python3-dev \
	make \
	cmake \
    ninja-build \
	z3 \
	libz3-dev \
	git 
RUN git clone --depth 1 --branch llvmorg-15.0.4 https://github.com/llvm/llvm-project.git
WORKDIR /llvm-project
COPY ./llvm-patch/def-in-header.patch ./
RUN git apply def-in-header.patch 
RUN mkdir build
WORKDIR /llvm-project/build
RUN cmake -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra;compiler-rt;cross-project-tests;openmp" -DLLVM_ENABLE_Z3_SOLVER=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/tmp/llvm -DLLVM_PARALLEL_LINK_JOBS=3 -DCMAKE_EXE_LINKER_FLAGS="-Wl,--reduce-memory-overheads -Wl,--hash-size=1021" -G "Ninja" ../llvm
RUN ninja install

FROM debian:bullseye-backports as cofe-up-base
RUN apt update && apt upgrade -y && apt install -y \
	build-essential \
	gcc \
	make \
	git \
	z3 \
	libz3-dev \
	cmake
COPY --from=llvm-build /tmp/llvm /usr/local/
COPY ./llvm-static-analyzers /root/llvm-static-analyzers
RUN mkdir -p /root/llvm-static-analyzers/build
RUN cd /root/llvm-static-analyzers/build \
	&& cmake .. \
	&& make
WORKDIR /root/
RUN git clone --depth 1 --branch llvmorg-15.0.4 https://github.com/llvm/llvm-project.git
COPY ./gbr-clang-tidy-module /root/gbr-clang-tidy-module
RUN mkdir -p /root/gbr-clang-tidy-module/build
RUN cd /root/gbr-clang-tidy-module/build \
	&& cmake -DCLANG_TIDY_SOURCE_DIR=/root/llvm-project/clang-tools-extra/clang-tidy .. \
	&& make
RUN git clone https://gitlab.com/cmocka/cmocka.git
WORKDIR /root/cmocka
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Debug -B build/
WORKDIR /root/cmocka/build
RUN make install

FROM cofe-up-base
RUN apt update && apt upgrade -y
RUN apt install -y \
	valgrind \
	python3-dev \
	python3-venv \
	python3-pip \
    python3-lxml \
	curl \
	jq \
	cppcheck \
	bear \
	zlib1g
RUN pip3 install --upgrade python-gitlab cppcheck-junit junitparser codechecker
COPY ./parser /opt/parser
COPY ./templates /opt/templates
COPY ./exercises /opt/exercises
RUN ls /opt/parser
RUN pip3 install -r /opt/parser/requirements.txt
WORKDIR /root/

# GBR CLANG TIDY Module #

Clang Tidy checks for Cofee UP - Gbr

## Building Analyzer ##

Building as Plugin

```bash
cmake -DCLANG_TIDY_SOURCE_DIR=/home/mschroetter/project/llvm-project/clang-tools-extra/clang-tidy -B build
cd build 
make
```

## Running ##

change the path for the -load argument :)

```bash
clang-tidy -checks=-*,misc-definitions-in-headers,bugprone-suspicious-include,cert-err34-c,cert-flp30-c,cert-dcl16-c,cert-con36-c,cert-dcl37-c,cert-sig30-c,modernize-netdb,modernize-signal,bugprone-netio -load /home/mschroetter/project/cofee_up-tidy-module/build/GBRTidyModule.so -header-filter=.* client.c
```

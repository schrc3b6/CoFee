# CoFee_UP #

Parser for several analyzers common in C development like:
    - Valgrind XML
    - Clang Static Analyzer Plist Files
    - Clang-Tidy Output
    - GCC Json

## Usage ##

CoFee_UP-Parser.py --help

## Testing ##

There is a Test script that itterates over all TestCases and Calls the Parser.
For that the Tests need to follow the following Directory Structure.

### Test Directory ###

    - Tests/
    |- TestCase#1/ 
     |- code/
      |- ringbuf.c
      |- ringbuf.h
      |- prog.c
     |- results/
      |- output.valgrind 
     |- message_global.xml
     |- message_local.xml
     |- output.xml
    |- TestCase#2
     ...
    
    One Folder for each test case containing a code directory, that contains the tested source code.
    The reslult directory contains the output of the analyzers or Unit-Test Results
    message_local.xml and message_global.xml are the files containing error message annotations.
    The output.xml is the expected junit report.
    
    

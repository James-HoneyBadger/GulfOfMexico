cmake_minimum_required(VERSION 3.15)
project(gomcc VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler flags
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -pedantic)
endif()

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/main.cpp
    src/lexer.cpp
    src/parser.cpp
    src/ast.cpp
    src/codegen.cpp
    src/runtime.cpp
)

# Executable
add_executable(gomcc ${SOURCES})

# Install
install(TARGETS gomcc DESTINATION bin)

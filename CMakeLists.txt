cmake_minimum_required(VERSION 3.13)
project(argon2
    LANGUAGES C
    HOMEPAGE_URL "https://github.com/P-H-C/phc-winner-argon2/"
    VERSION "0.1"
)

# Detect whether src/opt.c can be compiled
set(CMAKE_TRY_COMPILE_TARGET_TYPE "STATIC_LIBRARY")
try_compile(ARGON2_OPT_OK "${PROJECT_BINARY_DIR}/try_compile_opt"
    SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/opt.c"
    CMAKE_FLAGS "-DINCLUDE_DIRECTORIES=${PROJECT_SOURCE_DIR}/src;${PROJECT_SOURCE_DIR}/include"
    C_STANDARD 90)
if(ARGON2_OPT_OK)
    message(STATUS "Can compile optimized library")
else()
    message(STATUS "Cannot compile optimized library")
endif()

set(ARGON2_ARCH "native" CACHE STRING "Target architecture, used as target for -march. Set to empty string to disable.")
option(ARGON2_THREADS "Enable argon2 threads" ON)
option(ARGON2_EXECUTABLE "Build argon2 executable(s)" ON)
option(ARGON2_OPTIMIZATIONS "Enable argon2 optimizations" "${ARGON2_OPT_OK}")
option(ARGON2_COVERAGE "Enable argon2 coverage" OFF)
option(ARGON2_TESTS "Enable argon2 tests" ON)
option(ARGON2_MAN "Build argon2 manual" OFF)
option(ARGON2_SPEC "Build argon2 specification" OFF)
option(ARGON2_SANITIZE "Enable argon2 sanitizers" OFF)

option(ARGON2_INSTALL "Enable installation of argon2 (development) files" ON)
include(GNUInstallDirs)
set(ARGON2_PKGCONFIG_LIBS)

set(CMAKE_C_STANDARD 90)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_C_VISIBILITY_PRESET hidden)

if(CMAKE_C_COMPILER_ID MATCHES "MSVC")
    add_definitions(/D_CRT_SECURE_NO_WARNINGS)
    add_compile_options(/sdl /Oi /Gy)
    add_link_options(/OPT:ICF /INCREMENTAL:NO)
else()
    add_compile_options(-Wall)
endif()
if(ARGON2_COVERAGE)
    if(NOT CMAKE_C_COMPILER_ID MATCHES "MSVC")
        add_compile_options(-Werror=declaration-after-statement -Wextra -Wno-type-limits -Werror -coverage)
        add_link_options(-coverage)
        if(NOT CMAKE_BUILD_TYPE STREQUAL "Debug")
            add_definitions(-D_FORTIFY_SOURCE=2)
        endif()
    endif()
endif()

if(ARGON2_SANITIZE)
    if(NOT CMAKE_C_COMPILER_ID MATCHES "MSVC")
        add_compile_options(-fsanitize=address -fsanitize=undefined)
        add_link_options(-fsanitize=address -fsanitize=undefined)
    endif()
endif()

if(ARGON2_ARCH)
    if(NOT CMAKE_C_COMPILER_ID MATCHES "MSVC")
        add_compile_options("-march=${ARGON2_ARCH}")
        add_link_options("-march=${ARGON2_ARCH}")
    endif()
endif()

set(ARGON2_SOURCES
    src/argon2.c
    src/argon2.c
    src/core.c
    src/blake2/blake2b.c
    src/thread.c
    src/encoding.c
)
if(ARGON2_OPTIMIZATIONS)
    list(APPEND ARGON2_SOURCES src/opt.c)
else()
    list(APPEND ARGON2_SOURCES src/ref.c)
endif()

add_library(argon2_interface INTERFACE)
target_include_directories(argon2_interface INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_compile_definitions(argon2_interface INTERFACE A2_BUILDING)
if(ARGON2_THREADS)
    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        target_compile_options(argon2_interface INTERFACE "-pthread")
        target_link_options(argon2_interface INTERFACE "-pthread")
        list(APPEND ARGON2_PKGCONFIG_LIBS "-pthread")
    endif()
else()
    target_compile_definitions(argon2_interface INTERFACE ARGON2_NO_THREADS)
endif()

add_library(argon2 ${ARGON2_SOURCES})
target_link_libraries(argon2 PUBLIC argon2_interface)
set_target_properties(argon2 PROPERTIES
    SOVERSION ${argon2_VERSION_MAJOR}
    VERSION ${argon2_VERSION}
)
if(NOT BUILD_SHARED_LIBS)
    target_compile_definitions(argon2 PUBLIC A2_STATIC)
endif()

if(ARGON2_EXECUTABLE)
    add_executable(argon2_exe src/run.c)
    set_target_properties(argon2_exe PROPERTIES OUTPUT_NAME "argon2")
    target_link_libraries(argon2_exe PRIVATE argon2)
endif()

if(ARGON2_TESTS)
    enable_testing()
    add_executable(bench src/bench.c)
    target_link_libraries(bench PRIVATE argon2)

    add_executable(genkat src/genkat.c ${ARGON2_SOURCES})
    target_link_libraries(genkat PUBLIC argon2_interface)
    target_compile_definitions(genkat PRIVATE GENKAT)

    add_executable(tests src/test.c)
    target_link_libraries(tests PRIVATE argon2)
    add_test(NAME tests COMMAND tests)

    find_package(Python3 COMPONENTS Interpreter)
    add_test(NAME kats_test COMMAND "${Python3_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/kats/test.py" "$<TARGET_FILE:genkat>")
endif()

if(ARGON2_SPEC)
    add_subdirectory(latex)
endif()

if(ARGON2_MAN)
    add_subdirectory(man)
endif()

if(ARGON2_INSTALL)
    string(REPLACE ARGON2_PKGCONFIG_LIBS "${ARGON2_PKGCONFIG_LIBS}" ";" " ")
    configure_file(libargon2.pc.in libargon2.pc @ONLY)
    install(TARGETS argon2)
    install(FILES "${CMAKE_CURRENT_BINARY_DIR}/libargon2.pc"
        DESTINATION "${CMAKE_INSTALL_LIBDIR}/pkgconfig")
    install(FILES "include/argon2.h"
        DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
    if(ARGON2_EXECUTABLE)
        install(TARGETS argon2_exe)
    endif()
endif()

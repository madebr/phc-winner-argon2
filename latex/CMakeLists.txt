set(SPEC_NAME argon2-specs)
find_package(LATEX COMPONENTS PDFLATEX BIBTEX REQUIRED)

message(STATUS "PDFLATEX_COMPILER: ${PDFLATEX_COMPILER}")
message(STATUS "BIBTEX_COMPILER: ${BIBTEX_COMPILER}")

add_custom_command(OUTPUT "${SPEC_NAME}.aux"
    COMMAND "${PDFLATEX_COMPILER}" -interaction=nonstopmode -output-directory="${CMAKE_CURRENT_BINARY_DIR}" "${SPEC_NAME}.tex"
    DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/${SPEC_NAME}.tex"
        "${CMAKE_CURRENT_SOURCE_DIR}/IEEEtran.cls"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}")

add_custom_command(OUTPUT "${SPEC_NAME}.bbl" "${SPEC_NAME}.blg"
    COMMAND "${CMAKE_COMMAND}" -E copy
        "${CMAKE_CURRENT_SOURCE_DIR}/tradeoff.bib"
        "${CMAKE_CURRENT_BINARY_DIR}/tradeoff.bib"
    COMMAND "${BIBTEX_COMPILER}" "${SPEC_NAME}.aux"
    MAIN_DEPENDENCY "${CMAKE_CURRENT_SOURCE_DIR}/tradeoff.bib"
    DEPENDS "${SPEC_NAME}.aux"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}")

add_custom_command(OUTPUT "${SPEC_NAME}.pdf"
    COMMAND "${PDFLATEX_COMPILER}" -interaction=nonstopmode "-output-directory=${CMAKE_CURRENT_BINARY_DIR}" "${SPEC_NAME}.tex"
    COMMAND "${PDFLATEX_COMPILER}" -interaction=nonstopmode "-output-directory=${CMAKE_CURRENT_BINARY_DIR}" "${SPEC_NAME}.tex"
    DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/${SPEC_NAME}.tex"
        "${CMAKE_CURRENT_BINARY_DIR}/${SPEC_NAME}.bbl"
        "${CMAKE_CURRENT_BINARY_DIR}/${SPEC_NAME}.blg"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}")

add_custom_target("${SPEC_NAME}" ALL
    COMMAND "${CMAKE_COMMAND}" -E copy
        "${CMAKE_CURRENT_BINARY_DIR}/${SPEC_NAME}.pdf"
        "${PROJECT_SOURCE_DIR}/${SPEC_NAME}.pdf"
    DEPENDS "${SPEC_NAME}.pdf")

if(ARGON2_INSTALL)
    install(FILES "${CMAKE_CURRENT_BINARY_DIR}/${SPEC_NAME}.pdf"
        DESTINATION "${CMAKE_INSTALL_DOCDIR}/${PROJECT_NAME}")
endif()

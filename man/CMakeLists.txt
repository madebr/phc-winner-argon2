find_program(GZIP_BIN gzip)

if(GZIP_BIN)
    set(MAN_FILE "${CMAKE_CURRENT_BINARY_DIR}/argon2.1.gz")
    add_custom_command(OUTPUT argon2.1.gz
        COMMAND "${GZIP_BIN}" -c "${CMAKE_CURRENT_SOURCE_DIR}/argon2.1" ">argon2.1.gz"
        DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/argon2.1")

    add_custom_target(man ALL
        DEPENDS "${MAN_FILE}")
else()
    set(MAN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/argon2.1")
endif()

if(ARGON2_INSTALL)
    install (FILES "${MAN_FILE}"
        DESTINATION "${CMAKE_INSTALL_MANDIR}/man1")
endif()
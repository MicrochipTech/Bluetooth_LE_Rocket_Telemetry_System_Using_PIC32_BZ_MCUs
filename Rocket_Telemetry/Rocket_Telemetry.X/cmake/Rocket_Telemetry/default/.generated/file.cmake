# The following variables contains the files used by the different stages of the build process.
set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_assemble)
set_source_files_properties(${Rocket_Telemetry_default_default_XC32_FILE_TYPE_assemble} PROPERTIES LANGUAGE ASM)

# For assembly files, add "." to the include path for each file so that .include with a relative path works
foreach(source_file ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_assemble})
        set_source_files_properties(${source_file} PROPERTIES INCLUDE_DIRECTORIES "$<PATH:NORMAL_PATH,$<PATH:REMOVE_FILENAME,${source_file}>>")
endforeach()

set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_assembleWithPreprocess)
set_source_files_properties(${Rocket_Telemetry_default_default_XC32_FILE_TYPE_assembleWithPreprocess} PROPERTIES LANGUAGE ASM)

# For assembly files, add "." to the include path for each file so that .include with a relative path works
foreach(source_file ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_assembleWithPreprocess})
        set_source_files_properties(${source_file} PROPERTIES INCLUDE_DIRECTORIES "$<PATH:NORMAL_PATH,$<PATH:REMOVE_FILENAME,${source_file}>>")
endforeach()

set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_compile
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_ble/app_ble.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_ble/app_ble_handler.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_ble/app_ble_log_handler.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_ble/app_ble_utility.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_ble/app_trsps_handler.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_idle_task.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_user_edits.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble/ble_dm/ble_dm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble/ble_dm/ble_dm_conn.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble/ble_dm/ble_dm_dds.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble/ble_dm/ble_dm_info.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble/ble_dm/ble_dm_sm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble/ble_gcm/ble_dd.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble/ble_log/ble_log.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble/ble_util/mw_aes.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/profile_ble/ble_trsps/ble_trsps.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/service_ble/ble_trs/ble_trs.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/crypto/src/crypto.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/exceptions.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/freertos_hooks.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/initialization.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/interrupts.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/libc_syscalls.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/osal/osal_freertos.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/osal/osal_freertos_extend.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/peripheral/clk/plib_clk.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/peripheral/cmcc/plib_cmcc.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/peripheral/evsys/plib_evsys.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/peripheral/gpio/plib_gpio.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/peripheral/nvic/plib_nvic.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/peripheral/nvm/plib_nvm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/peripheral/sercom/usart/plib_sercom0_usart.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/startup_xc32.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/system/cache/sys_cache.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/system/console/src/sys_console.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/system/console/src/sys_console_uart.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/system/int/src/sys_int.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/tasks.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/main.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/FreeRTOS_tasks.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/croutine.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/event_groups.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/list.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/portable/GCC/SAM/ARM_CM4F/port.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/portable/MemMang/heap_4.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/queue.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/stream_buffer.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/timers.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/aes.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/arc4.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/asm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/asn.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/blake2b.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/blake2s.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/camellia.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/chacha.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/chacha20_poly1305.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/cmac.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/coding.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/compress.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/cpuid.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/cryptocb.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/curve25519.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/curve448.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/des3.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/dh.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/dsa.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/ecc.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/ecc_fp.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/eccsi.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/ed25519.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/ed448.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/error.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/evp.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/fe_448.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/fe_low_mem.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/fe_operations.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/ge_448.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/ge_low_mem.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/ge_operations.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/hash.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/hc128.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/hmac.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/idea.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/integer.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/logging.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/md2.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/md4.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/md5.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/memory.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/misc.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/pkcs12.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/pkcs7.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/poly1305.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_aes_sam6149.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_aes_u2238.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_ecc_ba414e.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_ecc_pukcl.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_pukcl_functions.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_rng_sam6334.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_rng_u2242.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_rsa_pukcl.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sam_u2803.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sha1_sam11105.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sha1_sam6156.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sha224_sam11105.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sha224_sam6156.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sha256_sam11105.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sha256_sam6156.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sha384_sam6156.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_sha512_sam6156.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_tdes_sam6150.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/crypt_wolfcryptcb.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/port/pic32/pic32mz-crypt.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/pwdbased.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/rabbit.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/random.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/rc2.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/ripemd.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/rsa.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sakke.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sha.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sha256.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sha3.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sha512.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/signature.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_arm32.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_arm64.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_armthumb.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_c32.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_c64.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_cortexm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_dsp32.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_int.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/sp_x86_64.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/srp.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/tfm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/wc_dsp.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/wc_encrypt.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/wc_pkcs11.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/wc_port.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/wolfevent.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl/wolfcrypt/src/wolfmath.c")
set_source_files_properties(${Rocket_Telemetry_default_default_XC32_FILE_TYPE_compile} PROPERTIES LANGUAGE C)
set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_compile_cpp)
set_source_files_properties(${Rocket_Telemetry_default_default_XC32_FILE_TYPE_compile_cpp} PROPERTIES LANGUAGE CXX)
set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_link
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/lib/ble_stack_bz2_lib.a"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/driver/device_support/pic32cx_bz2_device_support.a"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/driver/pds/pds.a")
set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_ihex)
set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_eep)
set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_lss)
set(Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_srec)

# The linker script used for the build.
set(Rocket_Telemetry_default_LINKER_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/WBZ451.ld")
set(Rocket_Telemetry_default_image_name "default.elf")
set(Rocket_Telemetry_default_image_base_name "default")

# The output directory of the final image.
set(Rocket_Telemetry_default_output_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../../out/Rocket_Telemetry")

# The full path to the final image.
set(Rocket_Telemetry_default_full_path_to_image ${Rocket_Telemetry_default_output_dir}/${Rocket_Telemetry_default_image_name})

# Potential output file extensions
set(output_extensions
    .hex
    .lss
    .eep
    .bin
    .srec)
list(TRANSFORM output_extensions PREPEND "${Rocket_Telemetry_default_output_dir}/${Rocket_Telemetry_default_image_base_name}")

# The following functions contains all the flags passed to the different build stages.

set(PACK_REPO_PATH "C:/Users/I63736/.mchp_packs" CACHE PATH "Path to the root of a pack repository.")

function(Rocket_Telemetry_default_default_XC32_assemble_rule target)
    set(options
        "-g"
        "${ASSEMBLER_PRE}"
        "-gdwarf-2"
        "-mcpu=cortex-m4"
        "-mfpu=fpv4-sp-d16"
        "-mthumb"
        "-Wa,--defsym=__MPLAB_BUILD=1${MP_EXTRA_AS_POST},--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1,--gdwarf-2")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG=1"
        PRIVATE "__WBZ451__")
endfunction()
function(Rocket_Telemetry_default_default_XC32_assembleWithPreprocess_rule target)
    set(options
        "-x"
        "assembler-with-cpp"
        "-g"
        "-gdwarf-2"
        "-mcpu=cortex-m4"
        "-mfpu=fpv4-sp-d16"
        "-mthumb"
        "-Wa,--defsym=__MPLAB_BUILD=1${MP_EXTRA_AS_POST},--defsym=__MPLAB_DEBUG=1,--gdwarf-2,-g,--defsym=__DEBUG=1")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG=1"
        PRIVATE "__WBZ451__"
        PRIVATE "default=default")
endfunction()
function(Rocket_Telemetry_default_default_XC32_compile_rule target)
    set(options
        "-g"
        "-gdwarf-2"
        "-mcpu=cortex-m4"
        "-mfpu=fpv4-sp-d16"
        "-x"
        "c"
        "-mthumb"
        "-O1"
        "-ffunction-sections"
        "-mlong-calls"
        "-Wall"
        "-Werror")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "__WBZ451__"
        PRIVATE "HAVE_CONFIG_H"
        PRIVATE "WOLFSSL_IGNORE_FILE_WARN"
        PRIVATE "default=default")
    target_include_directories(${target}
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/lib/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/profile_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/service_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/driver/pds/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/packs/CMSIS"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/packs/CMSIS/CMSIS/Core/Include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/packs/WBZ451_DFP"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/portable/GCC/SAM/ARM_CM4F"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/wolfssl/wolfssl"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/app_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/lib/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/middleware_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/profile_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/ble/service_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default/driver/pds/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
endfunction()
function(Rocket_Telemetry_default_default_XC32_compile_cpp_rule target)
    set(options
        "-g"
        "-gdwarf-2"
        "-x"
        "c++"
        "-mcpu=cortex-m4"
        "-mfpu=fpv4-sp-d16"
        "-mthumb"
        "-O1"
        "-ffunction-sections"
        "-fno-rtti"
        "-fno-exceptions"
        "-mlong-calls")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "__WBZ451__"
        PRIVATE "default=default")
    target_include_directories(${target}
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/config/default"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/packs/CMSIS"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/packs/CMSIS/CMSIS/Core/Include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/packs/WBZ451_DFP"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../src/third_party/rtos/FreeRTOS/Source/portable/GCC/SAM/ARM_CM4F"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
endfunction()
function(Rocket_Telemetry_default_link_rule target)
    set(options
        "-gdwarf-2"
        "${MP_EXTRA_LD_PRE}"
        "-Td:/Bluetooth-LE-Rocket-Telemetry-System-Using-PIC32-BZ-MCUs/Rocket_Telemetry/src/config/default/WBZ451.ld"
        "-mthumb"
        "-Wl,-Map=mem.map"
        "--specs=nosys.specs"
        "-Wl,--defsym=__MPLAB_BUILD=1${MP_EXTRA_LD_POST},--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1"
        "-L${CMAKE_CURRENT_SOURCE_DIR}/../../.."
        "-Wl,--gc-sections")
    list(REMOVE_ITEM options "")
    target_link_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__WBZ451__"
        PRIVATE "default=default")
endfunction()
function(Rocket_Telemetry_default_objcopy_ihex_rule target)
    add_custom_command(
        TARGET ${target}
        POST_BUILD
        COMMAND ${OBJCOPY}
        ARGS --output-target=ihex --remove-section=.eeprom --remove-section=.fuse --remove-section=.lock --remove-section=.signature ${Rocket_Telemetry_default_image_name} ${Rocket_Telemetry_default_image_base_name}.hex
        WORKING_DIRECTORY ${Rocket_Telemetry_default_output_dir})
endfunction()
function(Rocket_Telemetry_default_objcopy_eep_rule target)
    add_custom_command(
        TARGET ${target}
        POST_BUILD
        COMMAND ${OBJCOPY}
        ARGS --only-section=.eeprom --set-section-flags=.eeprom=alloc,load --change-section-lma .eeprom=0 --no-change-warnings --output-target=binary ${Rocket_Telemetry_default_image_name} ${Rocket_Telemetry_default_image_base_name}.eep
        WORKING_DIRECTORY ${Rocket_Telemetry_default_output_dir})
endfunction()
function(Rocket_Telemetry_default_objcopy_lss_rule target)
    add_custom_command(
        TARGET ${target}
        POST_BUILD
        COMMAND ${OBJDUMP}
        ARGS --disassemble --wide --demangle --line-numbers --section-headers --source ${Rocket_Telemetry_default_image_name} > ${Rocket_Telemetry_default_image_base_name}.lss
        WORKING_DIRECTORY ${Rocket_Telemetry_default_output_dir})
endfunction()
function(Rocket_Telemetry_default_objcopy_srec_rule target)
    add_custom_command(
        TARGET ${target}
        POST_BUILD
        COMMAND ${OBJCOPY}
        ARGS --output-target=srec --remove-section=.eeprom --remove-section=.fuse --remove-section=.lock --remove-section=.signature ${Rocket_Telemetry_default_image_name} ${Rocket_Telemetry_default_image_base_name}.srec
        WORKING_DIRECTORY ${Rocket_Telemetry_default_output_dir})
endfunction()

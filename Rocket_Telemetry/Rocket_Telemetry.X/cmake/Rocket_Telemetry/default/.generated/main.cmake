include("${CMAKE_CURRENT_LIST_DIR}/rule.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/file.cmake")

set(Rocket_Telemetry_default_library_list )

# Handle files with suffix s, for group default-XC32
if(Rocket_Telemetry_default_default_XC32_FILE_TYPE_assemble)
add_library(Rocket_Telemetry_default_default_XC32_assemble OBJECT ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_assemble})
    Rocket_Telemetry_default_default_XC32_assemble_rule(Rocket_Telemetry_default_default_XC32_assemble)
    list(APPEND Rocket_Telemetry_default_library_list "$<TARGET_OBJECTS:Rocket_Telemetry_default_default_XC32_assemble>")

endif()

# Handle files with suffix S, for group default-XC32
if(Rocket_Telemetry_default_default_XC32_FILE_TYPE_assembleWithPreprocess)
add_library(Rocket_Telemetry_default_default_XC32_assembleWithPreprocess OBJECT ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_assembleWithPreprocess})
    Rocket_Telemetry_default_default_XC32_assembleWithPreprocess_rule(Rocket_Telemetry_default_default_XC32_assembleWithPreprocess)
    list(APPEND Rocket_Telemetry_default_library_list "$<TARGET_OBJECTS:Rocket_Telemetry_default_default_XC32_assembleWithPreprocess>")

endif()

# Handle files with suffix [cC], for group default-XC32
if(Rocket_Telemetry_default_default_XC32_FILE_TYPE_compile)
add_library(Rocket_Telemetry_default_default_XC32_compile OBJECT ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_compile})
    Rocket_Telemetry_default_default_XC32_compile_rule(Rocket_Telemetry_default_default_XC32_compile)
    list(APPEND Rocket_Telemetry_default_library_list "$<TARGET_OBJECTS:Rocket_Telemetry_default_default_XC32_compile>")

endif()

# Handle files with suffix cpp, for group default-XC32
if(Rocket_Telemetry_default_default_XC32_FILE_TYPE_compile_cpp)
add_library(Rocket_Telemetry_default_default_XC32_compile_cpp OBJECT ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_compile_cpp})
    Rocket_Telemetry_default_default_XC32_compile_cpp_rule(Rocket_Telemetry_default_default_XC32_compile_cpp)
    list(APPEND Rocket_Telemetry_default_library_list "$<TARGET_OBJECTS:Rocket_Telemetry_default_default_XC32_compile_cpp>")

endif()

# Handle files with suffix elf, for group default-XC32
if(Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_ihex)
add_library(Rocket_Telemetry_default_default_XC32_objcopy_ihex OBJECT ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_ihex})
    Rocket_Telemetry_default_default_XC32_objcopy_ihex_rule(Rocket_Telemetry_default_default_XC32_objcopy_ihex)
    list(APPEND Rocket_Telemetry_default_library_list "$<TARGET_OBJECTS:Rocket_Telemetry_default_default_XC32_objcopy_ihex>")

endif()

# Handle files with suffix elf, for group default-XC32
if(Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_eep)
add_library(Rocket_Telemetry_default_default_XC32_objcopy_eep OBJECT ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_eep})
    Rocket_Telemetry_default_default_XC32_objcopy_eep_rule(Rocket_Telemetry_default_default_XC32_objcopy_eep)
    list(APPEND Rocket_Telemetry_default_library_list "$<TARGET_OBJECTS:Rocket_Telemetry_default_default_XC32_objcopy_eep>")

endif()

# Handle files with suffix elf, for group default-XC32
if(Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_lss)
add_library(Rocket_Telemetry_default_default_XC32_objcopy_lss OBJECT ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_lss})
    Rocket_Telemetry_default_default_XC32_objcopy_lss_rule(Rocket_Telemetry_default_default_XC32_objcopy_lss)
    list(APPEND Rocket_Telemetry_default_library_list "$<TARGET_OBJECTS:Rocket_Telemetry_default_default_XC32_objcopy_lss>")

endif()

# Handle files with suffix elf, for group default-XC32
if(Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_srec)
add_library(Rocket_Telemetry_default_default_XC32_objcopy_srec OBJECT ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_objcopy_srec})
    Rocket_Telemetry_default_default_XC32_objcopy_srec_rule(Rocket_Telemetry_default_default_XC32_objcopy_srec)
    list(APPEND Rocket_Telemetry_default_library_list "$<TARGET_OBJECTS:Rocket_Telemetry_default_default_XC32_objcopy_srec>")

endif()


# Main target for this project
add_executable(Rocket_Telemetry_default_image_6J8mD2xZ ${Rocket_Telemetry_default_library_list})

set_target_properties(Rocket_Telemetry_default_image_6J8mD2xZ PROPERTIES
    OUTPUT_NAME "default"
    SUFFIX ".elf"
    ADDITIONAL_CLEAN_FILES "${output_extensions}"
    RUNTIME_OUTPUT_DIRECTORY "${Rocket_Telemetry_default_output_dir}")
target_link_libraries(Rocket_Telemetry_default_image_6J8mD2xZ PRIVATE ${Rocket_Telemetry_default_default_XC32_FILE_TYPE_link})
# Add the link options from the rule file.
Rocket_Telemetry_default_link_rule( Rocket_Telemetry_default_image_6J8mD2xZ)


#Add objcopy steps
Rocket_Telemetry_default_objcopy_ihex_rule(Rocket_Telemetry_default_image_6J8mD2xZ)
Rocket_Telemetry_default_objcopy_eep_rule(Rocket_Telemetry_default_image_6J8mD2xZ)
Rocket_Telemetry_default_objcopy_lss_rule(Rocket_Telemetry_default_image_6J8mD2xZ)
Rocket_Telemetry_default_objcopy_srec_rule(Rocket_Telemetry_default_image_6J8mD2xZ)


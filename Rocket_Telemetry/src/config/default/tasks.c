/*******************************************************************************
 System Tasks File

  File Name:
    tasks.c

  Summary:
    This file contains source code necessary to maintain system's polled tasks.

  Description:
    This file contains source code necessary to maintain system's polled tasks.
    It implements the "SYS_Tasks" function that calls the individual "Tasks"
    functions for all polled MPLAB Harmony modules in the system.

  Remarks:
    This file requires access to the systemObjects global data structure that
    contains the object handles to all MPLAB Harmony module objects executing
    polled in the system.  These handles are passed into the individual module
    "Tasks" functions to identify the instance of the module to maintain.
 *******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2018 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
 *******************************************************************************/
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

#include "configuration.h"
#include "definitions.h"
#include "sys_tasks.h"
#include "app.h"
#include "app_trsps_handler.h"
#include <stdio.h>
#include <stdlib.h>


// *****************************************************************************
// *****************************************************************************
// Section: RTOS "Tasks" Routine
// *****************************************************************************
// *****************************************************************************
#define TASK_BLE_STACK_SIZE (2 *1024 / sizeof(portSTACK_TYPE))
#define TASK_BLE_PRIORITY (tskIDLE_PRIORITY + 3)
#define TASK_SENSORS_STACK_SIZE (1024 / sizeof(portSTACK_TYPE))
#define TASK_SENSORS_PRIORITY (tskIDLE_PRIORITY + 1)

static void APP_FormatTelemetryField(char *p_dst, size_t dstSize, float value)
{
  int32_t scaled = (int32_t)(value * 100.0f);

  if (scaled < 0)
  {
    scaled = -scaled;
    (void)snprintf(p_dst, dstSize, "-%03ld.%02ld",
      (long)(scaled / 100), (long)(scaled % 100));
  }
  else
  {
    (void)snprintf(p_dst, dstSize, "%03ld.%02ld",
      (long)(scaled / 100), (long)(scaled % 100));
  }
}

/* Handle for the APP_Tasks. */
TaskHandle_t xAPP_Tasks;

static void lAPP_Tasks(  void *pvParameters  )
{   
    while(true)
    {
        APP_Tasks();
    }
}

static void lSENSORS_Tasks(void *pvParameters)
{
  SENSORS_Data_T sensorsData;
  TickType_t lastWakeTick;
  uint16_t connHandle;
  char bleTxBuf[96];
  char pField[12];
  char tField[12];
  char xField[12];
  char yField[12];
  char zField[12];
  int bleTxLen;

  (void)pvParameters;

  if (!SENSORS_Init())
  {
    SYS_CONSOLE_PRINT("Sensors init failed\r\n");
  }

  lastWakeTick = xTaskGetTickCount();

  while (true)
  {
    bool bleConnected = APP_TrspsGetActiveConnHandle(&connHandle);

    if (bleConnected)
    {
      RED_LED_Clear();
      BLUE_LED_Toggle();
    }
    else
    {
      BLUE_LED_Clear();
      RED_LED_Toggle();
    }

    if (SENSORS_ReadAll(&sensorsData))
    {
      APP_FormatTelemetryField(pField, sizeof(pField), sensorsData.pressure_kpa);
      APP_FormatTelemetryField(tField, sizeof(tField), sensorsData.temperature_c);
      APP_FormatTelemetryField(xField, sizeof(xField), sensorsData.accel_x_g);
      APP_FormatTelemetryField(yField, sizeof(yField), sensorsData.accel_y_g);
      APP_FormatTelemetryField(zField, sizeof(zField), sensorsData.accel_z_g);

      bleTxLen = snprintf(bleTxBuf, sizeof(bleTxBuf),
        "< %s, %s, %s, %s, %s \n\r",
        pField, tField, xField, yField, zField);

      SYS_CONSOLE_PRINT("%s", bleTxBuf);

      if (bleConnected && (bleTxLen > 0))
      {
        (void)BLE_TRSPS_SendData(connHandle, (uint16_t)bleTxLen, (uint8_t *)bleTxBuf);
      }
    }
    else
    {
      SYS_CONSOLE_PRINT("Sensor read failed\r\n");
    }

    vTaskDelayUntil(&lastWakeTick, pdMS_TO_TICKS(100U));
  }
}




// *****************************************************************************
// *****************************************************************************
// Section: System "Tasks" Routine
// *****************************************************************************
// *****************************************************************************

/*******************************************************************************
  Function:
    void SYS_Tasks ( void )

  Remarks:
    See prototype in system/common/sys_module.h.
*/
void SYS_Tasks ( void )
{
    /* Maintain system services */
    


    /* Maintain Device Drivers */
    

    /* Maintain Middleware & Other Libraries */
    
    if (xTaskCreate(BM_Task,     "BLE", TASK_BLE_STACK_SIZE, NULL  , TASK_BLE_PRIORITY, NULL) != pdPASS)
        while (1);



    /* Maintain the application's state machine. */
        /* Create OS Thread for APP_Tasks. */
    (void) xTaskCreate((TaskFunction_t) lAPP_Tasks,
                "APP_Tasks",
                1024,
                NULL,
                1,
                &xAPP_Tasks);

    (void) xTaskCreate((TaskFunction_t) lSENSORS_Tasks,
          "SENSORS",
          TASK_SENSORS_STACK_SIZE,
          NULL,
          TASK_SENSORS_PRIORITY,
          NULL);




    /* Start RTOS Scheduler. */
    
     /**********************************************************************
     * Create all Threads for APP Tasks before starting FreeRTOS Scheduler *
     ***********************************************************************/
    vTaskStartScheduler(); /* This function never returns. */

}

/*******************************************************************************
 End of File
 */


// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2022 Microchip Technology Inc. and its subsidiaries.
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

/*******************************************************************************
  MPLAB Harmony Application Source File

  Company:
    Microchip Technology Inc.

  File Name:
    app.c

  Summary:
    This file contains the source code for the MPLAB Harmony application.

  Description:
    This file contains the source code for the MPLAB Harmony application.  It
    implements the logic of the application's state machine and it may call
    API routines of other MPLAB Harmony modules in the system, such as drivers,
    system services, and middleware.  However, it does not call any of the
    system interfaces (such as the "Initialize" and "Tasks" functions) of any of
    the modules in the system or make any assumptions about when those functions
    are called.  That is the responsibility of the configuration-specific system
    files.
 *******************************************************************************/

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************
#include "app.h"
#include "definitions.h"
#include "app_ble.h"
#include "app_trsps_handler.h"

#define MPL3115A2_ADDR_0                    (0x60U)
#define MPL3115A2_WHO_AM_I_REG              (0x0CU)
#define MPL3115A2_WHO_AM_I_VAL              (0xC4U)
#define MPL3115A2_CTRL_REG1                 (0x26U)
#define MPL3115A2_PT_DATA_CFG               (0x13U)
#define MPL3115A2_OUT_P_MSB                 (0x01U)
#define MPL3115A2_CTRL_REG1_OSR_128         (0x38U)
#define MPL3115A2_CTRL_REG1_ACTIVE          (0x01U)

#define FXLS8974_ADDR_0                     (0x18U)
#define FXLS8974_WHO_AM_I_REG               (0x13U)
#define FXLS8974_WHO_AM_I_VAL               (0x86U)
#define FXLS8974_WHO_AM_I_ALT               (0x84U)
#define FXLS8974_CTRL_REG1                  (0x15U)
#define FXLS8974_CTRL_REG3                  (0x17U)
#define FXLS8974_OUT_X_LSB                  (0x04U)
#define FXLS8974_CTRL_REG1_ACTIVE           (0x01U)
#define FXLS8974_CTRL_REG1_FSR_2G           (0x00U)
#define FXLS8974_CTRL_REG3_WAKE_ODR_12P5HZ  (0x80U)

#define SENSORS_I2C_WAIT_MAX_LOOPS          (1000000U)



// *****************************************************************************
// *****************************************************************************
// Section: Global Data Definitions
// *****************************************************************************
// *****************************************************************************





// *****************************************************************************
/* Application Data

  Summary:
    Holds application data

  Description:
    This structure holds the application's data.

  Remarks:
    This structure should be initialized by the APP_Initialize function.

    Application strings and buffers are be defined outside this structure.
*/

APP_DATA appData;

static uint8_t s_pressAddr = 0U;
static uint8_t s_accelAddr = 0U;
static bool s_initDone = false;

// *****************************************************************************
// *****************************************************************************
// Section: Application Callback Functions
// *****************************************************************************
// *****************************************************************************

/* TODO:  Add any necessary callback functions.
*/

// *****************************************************************************
// *****************************************************************************
// Section: Application Local Functions
// *****************************************************************************
// *****************************************************************************


/* TODO:  Add any necessary local functions.
*/
static void APP_ConsoleToTrspsBridge(void)
{
  uint16_t connHandle;
  uint8_t consoleRxBuf[64];
  ssize_t readCount;

  readCount = SYS_CONSOLE_Read(SYS_CONSOLE_DEFAULT_INSTANCE, consoleRxBuf, sizeof(consoleRxBuf));
  if (readCount <= 0)
  {
    return;
  }

  if (APP_TrspsGetActiveConnHandle(&connHandle))
  {
    (void)BLE_TRSPS_SendData(connHandle, (uint16_t)readCount, consoleRxBuf);
  }
}

  static bool SENSORS_I2cWaitForDone(void)
  {
    uint32_t timeout = SENSORS_I2C_WAIT_MAX_LOOPS;

    while (SERCOM2_I2C_IsBusy())
    {
      if (timeout == 0U)
      {
        SERCOM2_I2C_TransferAbort();
        return false;
      }
      timeout--;
    }

    return (SERCOM2_I2C_ErrorGet() == SERCOM_I2C_ERROR_NONE);
  }

static bool SENSORS_I2cWriteReg(uint8_t addr, uint8_t reg, uint8_t value)
{
    uint8_t wr[2];

    wr[0] = reg;
    wr[1] = value;

    if (!SENSORS_I2cWaitForDone())
    {
      return false;
    }

    if (!SERCOM2_I2C_Write(addr, wr, 2U))
    {
      return false;
    }

    return SENSORS_I2cWaitForDone();
}

static bool SENSORS_I2cReadRegs(uint8_t addr, uint8_t reg, uint8_t *p_data, uint32_t len)
{
    if (!SENSORS_I2cWaitForDone())
    {
      return false;
    }

    if (!SERCOM2_I2C_WriteRead(addr, &reg, 1U, p_data, len))
    {
      return false;
    }

    return SENSORS_I2cWaitForDone();
}

static bool SENSORS_DetectPressure(void)
{
    uint8_t whoAmI;
    s_pressAddr = MPL3115A2_ADDR_0;

    if (!SENSORS_I2cReadRegs(s_pressAddr, MPL3115A2_WHO_AM_I_REG, &whoAmI, 1U))
    {
      return false;
    }

    if (whoAmI != MPL3115A2_WHO_AM_I_VAL)
    {
      return false;
    }

    if (!SENSORS_I2cWriteReg(s_pressAddr, MPL3115A2_CTRL_REG1, 0x00U))
    {
      return false;
    }

    if (!SENSORS_I2cWriteReg(s_pressAddr, MPL3115A2_PT_DATA_CFG, 0x07U))
    {
      return false;
    }

    return SENSORS_I2cWriteReg(s_pressAddr, MPL3115A2_CTRL_REG1,
      (uint8_t)(MPL3115A2_CTRL_REG1_OSR_128 | MPL3115A2_CTRL_REG1_ACTIVE));
}

static bool SENSORS_DetectAccel(void)
{
    uint8_t whoAmI;
    uint8_t ctrlReg1;
    s_accelAddr = FXLS8974_ADDR_0;

    if (!SENSORS_I2cReadRegs(s_accelAddr, FXLS8974_WHO_AM_I_REG, &whoAmI, 1U))
    {
      return false;
    }

    if ((whoAmI != FXLS8974_WHO_AM_I_VAL) && (whoAmI != FXLS8974_WHO_AM_I_ALT))
    {
      return false;
    }

    /* Put sensor in standby before changing ODR/range settings. */
    if (!SENSORS_I2cWriteReg(s_accelAddr, FXLS8974_CTRL_REG1, FXLS8974_CTRL_REG1_FSR_2G))
    {
      return false;
    }

    /* Configure wake ODR for polling mode (12.5 Hz). */
    if (!SENSORS_I2cWriteReg(s_accelAddr, FXLS8974_CTRL_REG3, FXLS8974_CTRL_REG3_WAKE_ODR_12P5HZ))
    {
      return false;
    }

    /* Enable active mode. */
    if (!SENSORS_I2cWriteReg(s_accelAddr, FXLS8974_CTRL_REG1,
      (uint8_t)(FXLS8974_CTRL_REG1_FSR_2G | FXLS8974_CTRL_REG1_ACTIVE)))
    {
      return false;
    }

    if (!SENSORS_I2cReadRegs(s_accelAddr, FXLS8974_CTRL_REG1, &ctrlReg1, 1U))
    {
      return false;
    }

    return ((ctrlReg1 & FXLS8974_CTRL_REG1_ACTIVE) != 0U);
}

bool SENSORS_Init(void)
{
    bool pressOk;
    bool accelOk;

    pressOk = SENSORS_DetectPressure();
    accelOk = SENSORS_DetectAccel();

    s_initDone = (pressOk && accelOk);
    return s_initDone;
}

bool SENSORS_ReadPressureTemperature(float *pressure_kpa, float *temperature_c)
{
    uint8_t raw[5];
    uint32_t pressRaw20;
    int16_t tempRaw12;

    if ((!s_initDone) || (pressure_kpa == NULL) || (temperature_c == NULL) || (s_pressAddr == 0U))
    {
      return false;
    }

    if (!SENSORS_I2cReadRegs(s_pressAddr, MPL3115A2_OUT_P_MSB, raw, 5U))
    {
      return false;
    }

    pressRaw20 = ((uint32_t)raw[0] << 16) | ((uint32_t)raw[1] << 8) | (uint32_t)raw[2];
    pressRaw20 >>= 4;

    tempRaw12 = (int16_t)((((uint16_t)raw[3] << 8) | (uint16_t)raw[4]) >> 4);
    if ((tempRaw12 & 0x0800) != 0)
    {
      tempRaw12 |= (int16_t)0xF000;
    }

    /* MPL3115A2 pressure output in barometer mode is Q18.2 Pa. */
    *pressure_kpa = ((float)pressRaw20 / 4.0f) / 1000.0f;
    *temperature_c = (float)tempRaw12 / 16.0f;

    if ((*temperature_c > 127.0f) || (*temperature_c < -128.0f))
    {
      return false;
    }

    return true;
}

bool SENSORS_ReadAccel(float *x_g, float *y_g, float *z_g)
{
    uint8_t raw[6];
    int16_t xRaw;
    int16_t yRaw;
    int16_t zRaw;

    if ((!s_initDone) || (x_g == NULL) || (y_g == NULL) || (z_g == NULL) || (s_accelAddr == 0U))
    {
      return false;
    }

    if (!SENSORS_I2cReadRegs(s_accelAddr, FXLS8974_OUT_X_LSB, raw, 6U))
    {
      return false;
    }

    xRaw = (int16_t)(((uint16_t)raw[1] << 8) | raw[0]);
    yRaw = (int16_t)(((uint16_t)raw[3] << 8) | raw[2]);
    zRaw = (int16_t)(((uint16_t)raw[5] << 8) | raw[4]);

    *x_g = (float)xRaw / 1024.0f;
    *y_g = (float)yRaw / 1024.0f;
    *z_g = (float)zRaw / 1024.0f;

    return true;
}

bool SENSORS_ReadAll(SENSORS_Data_T *p_data)
{
    if ((p_data == NULL) || (!s_initDone))
    {
      return false;
    }

    if (!SENSORS_ReadPressureTemperature(&p_data->pressure_kpa, &p_data->temperature_c))
    {
      return false;
    }

    if (!SENSORS_ReadAccel(&p_data->accel_x_g, &p_data->accel_y_g, &p_data->accel_z_g))
    {
      return false;
    }

    return true;
}


// *****************************************************************************
// *****************************************************************************
// Section: Application Initialization and State Machine Functions
// *****************************************************************************
// *****************************************************************************

/*******************************************************************************
  Function:
    void APP_Initialize ( void )

  Remarks:
    See prototype in app.h.
 */

void APP_Initialize ( void )
{
    /* Place the App state machine in its initial state. */
    appData.state = APP_STATE_INIT;


    appData.appQueue = xQueueCreate( 64, sizeof(APP_Msg_T) );
    /* TODO: Initialize your application's state machine and other
     * parameters.
     */
}


/******************************************************************************
  Function:
    void APP_Tasks ( void )

  Remarks:
    See prototype in app.h.
 */

void APP_Tasks ( void )
{
    APP_Msg_T    appMsg[1];
    APP_Msg_T   *p_appMsg;
    p_appMsg=appMsg;

    /* Check the application's current state. */
    switch ( appData.state )
    {
        /* Application's initial state. */
        case APP_STATE_INIT:
        {
            bool appInitialized = true;
            //appData.appQueue = xQueueCreate( 10, sizeof(APP_Msg_T) );

            APP_BleStackInit();




            if (appInitialized)
            {

                appData.state = APP_STATE_SERVICE_TASKS;
            }
            break;
        }

        case APP_STATE_SERVICE_TASKS:
        {
          APP_ConsoleToTrspsBridge();

          if (OSAL_QUEUE_Receive(&appData.appQueue, &appMsg, 10))
            {

                if(p_appMsg->msgId==APP_MSG_BLE_STACK_EVT)
                {
                    // Pass BLE Stack Event Message to User Application for handling
                    APP_BleStackEvtHandler((STACK_Event_T *)p_appMsg->msgData);
                }
                else if(p_appMsg->msgId==APP_MSG_BLE_STACK_LOG)
                {
                    // Pass BLE LOG Event Message to User Application for handling
                    APP_BleStackLogHandler((BT_SYS_LogEvent_T *)p_appMsg->msgData);
                }



            }
            break;
        }

        /* TODO: implement your application state machine.*/


        /* The default state should never be executed. */
        default:
        {
            /* TODO: Handle error in application's state machine. */
            break;
        }
    }
}


/*******************************************************************************
 End of File
 */

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

/*******************************************************************************
  Application BLE Profile Source File

  Company:
    Microchip Technology Inc.

  File Name:
    app_trsps_handler.c

  Summary:
    This file contains the Application BLE functions for this project.

  Description:
    This file contains the Application BLE functions for this project.
 *******************************************************************************/


// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************
#include "app_trsps_handler.h"
#include <stdlib.h>
#include "system/console/sys_console.h"
#include "mba_error_defs.h"


// *****************************************************************************
// *****************************************************************************
// Section: Global Variables
// *****************************************************************************
// *****************************************************************************
static bool s_trspsTxOpened = false;
static uint16_t s_trspsConnHandle = 0U;


// *****************************************************************************
// *****************************************************************************
// Section: Functions
// *****************************************************************************
// *****************************************************************************

void APP_TrspsEvtHandler(BLE_TRSPS_Event_T *p_event)
{
    switch(p_event->eventId)
    {
        case BLE_TRSPS_EVT_CTRL_STATUS:
        {
            /* No console output for control status updates. */
        }
        break;
        
        case BLE_TRSPS_EVT_TX_STATUS:
        {
            if (p_event->eventField.onTxStatus.status == BLE_TRSPS_STATUS_TX_OPENED)
            {
                s_trspsTxOpened = true;
                s_trspsConnHandle = p_event->eventField.onTxStatus.connHandle;
            }
            else if (s_trspsConnHandle == p_event->eventField.onTxStatus.connHandle)
            {
                s_trspsTxOpened = false;
                s_trspsConnHandle = 0U;
            }
        }
        break;

        case BLE_TRSPS_EVT_CBFC_ENABLED:
        {
            /* TODO: implement your application code.*/
        }
        break;
        
        case BLE_TRSPS_EVT_CBFC_CREDIT:
        {
            /* TODO: implement your application code.*/
        }
        break;
        
        case BLE_TRSPS_EVT_RECEIVE_DATA:
        {
            uint16_t dataLen = 0;
            uint16_t getDataStatus;
            uint8_t *p_data;
            uint16_t connHandle = p_event->eventField.onReceiveData.connHandle;

            BLE_TRSPS_GetDataLength(connHandle, &dataLen);

            if (dataLen == 0U)
            {
                break;
            }

            p_data = (uint8_t *)malloc(dataLen);
            if (p_data == NULL)
            {
                break;
            }

            getDataStatus = BLE_TRSPS_GetData(connHandle, p_data);
            if (getDataStatus != MBA_RES_SUCCESS)
            {
                free(p_data);
                break;
            }

            (void)SYS_CONSOLE_Write(SYS_CONSOLE_DEFAULT_INSTANCE, p_data, (size_t)dataLen);

            free(p_data);
        }
        break;
        
        case BLE_TRSPS_EVT_VENDOR_CMD:
        {
            /* TODO: implement your application code.*/
        }
        break;

        case BLE_TRSPS_EVT_ERR_UNSPECIFIED:
        {
            /* TODO: implement your application code.*/
        }
        break;

        case BLE_TRSPS_EVT_ERR_NO_MEM:
        {
            /* TODO: implement your application code.*/
        }
        break;

        default:
        break;
    }
}

bool APP_TrspsGetActiveConnHandle(uint16_t *p_connHandle)
{
    if ((p_connHandle == NULL) || (s_trspsTxOpened == false))
    {
        return false;
    }

    *p_connHandle = s_trspsConnHandle;
    return true;
}

void APP_TrspsHandleDisconnect(void)
{
    s_trspsTxOpened = false;
    s_trspsConnHandle = 0U;
}
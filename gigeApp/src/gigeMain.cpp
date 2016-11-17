/* gigeMain.cpp */
/* Author:  Marty Kraimer Date:    17MAR2000 */

#include <stddef.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

#include "epicsExit.h"
#include "epicsThread.h"
#ifdef USE_EVR_IRQ_HANDLER
#include "evrIrqHandler.h"
#endif
#include "iocsh.h"

int main(int argc,char *argv[])
{

#ifdef USE_EVR_IRQ_HANDLER
	// EVR module must block SIGIO from the main process
	evrIrqHandlerInit();
#endif

    if(argc>=2) {    
        iocsh(argv[1]);
        epicsThreadSleep(.2);
    }
    iocsh(NULL);
    epicsExit(0);
    return(0);
}

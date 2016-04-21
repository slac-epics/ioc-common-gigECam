#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <subRecord.h>            /* for struct subRecord         */
#include <registryFunction.h>     /* for epics register function  */
#include <epicsExport.h>          /* for epicsExport              */
#include <epicsTime.h>            /* epics timestamp and proto    */
#include <evrTime.h>              /* for EVR APIs                 */
#include <epicsMutex.h>

#define MAX_NICS 16

#define NIC_ID_SIZE 10

typedef struct
{
  char nic[NIC_ID_SIZE];
  double tx_rate; /* in MBps */
  double rx_rate; /* in MBps */
} nic_stats_t;

static int num_nics = 0;

static nic_stats_t nic_stats[MAX_NICS];

static epicsMutexId     netstatMutex    = 0;

static void * netstatThread( void * pUnused )
{
  FILE *fp;
  char line[1400];
  char interface[20];
  /* This is the sar command: */
  char *cmd="/usr/bin/sar -n DEV 1 1 | grep Average | tr -s \" \" | cut -d\" \" -f 2,5,6";
  double rx_rate;
  double tx_rate;

  while (1) {
    fp=popen(cmd, "r");

    if (fp==NULL) {
      printf("ERROR: fail on popen\n");
    }
    else {
      epicsMutexLock(netstatMutex);
      double rateDiv    = 1e3;
      int if_counter = 0;
      while (fgets(line, sizeof(line)-1, fp) != NULL) {
/*      printf("%s", line); */
        if ( strstr( line, "rxbyt/s" ) ) {
            rateDiv = 1e6;
            continue;
        }
        if ( strstr( line, "rxkB/s" ) ) {
            rateDiv = 1e3;
            continue;
        }
        if ( sscanf(line, "%s %lf %lf", interface, &rx_rate, &tx_rate) != 3 )
            continue;
        if (if_counter < MAX_NICS) {
          strcpy(nic_stats[if_counter].nic, interface);
          nic_stats[if_counter].tx_rate = tx_rate / rateDiv;
          nic_stats[if_counter].rx_rate = rx_rate / rateDiv;
          /*
          printf("%s %lf %lf\n", nic_stats[if_counter].nic, 
                 nic_stats[if_counter].tx_rate,
                 nic_stats[if_counter].rx_rate);
          */
          if_counter++;
        }
      }
      num_nics = if_counter;
      epicsMutexUnlock(netstatMutex);
      pclose(fp);
    }

    sleep(3);
  }
  return NULL;
}

static pthread_t netstatThreadId;

static long subNetstatInit(subRecord *prec)
{
        if ( netstatMutex == 0 )
        {
                netstatMutex = epicsMutexMustCreate();
                if ( netstatMutex == 0 )
                {
                        printf( "Error creating netstatMutex!" );
                        return -1;
                }
                pthread_create(&netstatThreadId, NULL, netstatThread, NULL);
        }

  return 0;
}

static long subNetstat(subRecord *prec)
{
  evrTimeGet(&(prec->time), 0);
  prec->val = 0;

  // If NIC exists, provide the current rate
  unsigned int nic_index = prec->a;
  unsigned int function = prec->b;

  epicsMutexLock(netstatMutex);
  if ( nic_index < MAX_NICS && nic_index < num_nics ) {
    // B == 0 -> TX
    if (function == 0) {
      prec->val = nic_stats[nic_index].tx_rate;
    }
    else {
      prec->val = nic_stats[nic_index].rx_rate;
    }
  }
  /*
  printf("%d %d %s %lf %lf\n", nic_index, function, nic_stats[nic_index].nic, 
         nic_stats[nic_index].tx_rate,
         nic_stats[nic_index].rx_rate);
  */

  epicsMutexUnlock(netstatMutex);
  return 0;  
}

epicsRegisterFunction(subNetstat);
epicsRegisterFunction(subNetstatInit);

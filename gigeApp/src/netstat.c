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

static int NET_COUNT = 0;

#define MAX_NICS 16

static FILE *tx_fp[MAX_NICS];
static FILE *rx_fp[MAX_NICS];
static time_t last_time;
static unsigned long tx_bytes[MAX_NICS];
static unsigned long rx_bytes[MAX_NICS];
static unsigned long tx_rate[MAX_NICS];
static unsigned long rx_rate[MAX_NICS];

#define NIC_ID_SIZE 10

typedef struct {
  char nic[NIC_ID_SIZE];
  double tx_rate; /* in Mbps */
  double rx_rate; /* in Mbps */
} nic_stats_t;

static int num_nics = 0;

static nic_stats_t nic_stats[MAX_NICS];

static epicsMutexId mutex;

static void netstatThread() {
  FILE *fp;
  char line[1400];
  char interface[20];
  /* This is the RHEL5 command: */
  /*  char *cmd="/usr/bin/sar -n DEV 1 | grep Average | grep -v IFACE | tr -s \" \" | cut -d\" \" -f 2,5,6"; */
  /* This is the RHEL6 command: */
  char *cmd="/usr/bin/sar -n DEV 1 1 | grep Average | grep -v IFACE | tr -s \" \" | cut -d\" \" -f 2,5,6";
  double rx_rate;
  double tx_rate;

  while (1) {
    fp=popen(cmd, "r");

    if (fp==NULL) {
      printf("ERROR: fail on popen\n");
    }
    else {
      epicsMutexLock(mutex);
      int if_counter = 0;
      while (fgets(line, sizeof(line)-1, fp) != NULL) {
/* 	printf("%s", line); */
	if (if_counter < MAX_NICS) {
	  sscanf(line, "%s %lf %lf", interface, &rx_rate, &tx_rate);
	  strcpy(nic_stats[if_counter].nic, interface);
	  nic_stats[if_counter].tx_rate = tx_rate * 8 / 1024;
	  nic_stats[if_counter].rx_rate = rx_rate * 8 / 1024;
	  /*
	  printf("%s %lf %lf\n", nic_stats[if_counter].nic, 
		 nic_stats[if_counter].tx_rate,
		 nic_stats[if_counter].rx_rate);
	  */
	}
	if_counter++;
      }
      num_nics = if_counter;
      epicsMutexUnlock(mutex);
      pclose(fp);
    }

    sleep(3);
  }
}

pthread_t netstatThreadId;

static long subNetstatInit(subRecord *prec) {
  mutex = epicsMutexMustCreate();

  pthread_create(&netstatThreadId, NULL, netstatThread, NULL);

  return 0;
}

static long subNetstat(subRecord *prec) {
  evrTimeGet(&(prec->time), 0);
  prec->val = 0;

  time_t now = time(0);
  unsigned long bytes_now;

  // If NIC exists, provide the current rate
  unsigned int nic_index = prec->a;
  unsigned int function = prec->b;

  epicsMutexLock(mutex);
  if (nic_index < MAX_NICS && nic_index < num_nics != NULL) {
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

  epicsMutexUnlock(mutex);
  return 0;  
}

epicsRegisterFunction(subNetstat);
epicsRegisterFunction(subNetstatInit);

/*
Compile it with: gcc -o smap_parser smap_parser.c -lm -O3

Usage: ./smap_parser -n qemu-system-x86_64 -m 8 -d /tmp/data.csv
  -n: name of the process
  -m: memory in MB
  -d: datapath
*/

#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <getopt.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define SIZE 512
#define NB_PROCESS 1024

static char VERBOSE = 0;
static int index_process = 0;

struct maps {
  unsigned long addr_start;
  unsigned long addr_end;
  unsigned long length;
  unsigned char perms;
  int offset;
  int major;
  int minor;
  unsigned long inode;
  char *pathname;
} typedef struct_maps;

struct process {
  int *pid;
  int memory;
  char process_name[SIZE];
  char datapath[SIZE];
  unsigned long total_pss;

} typedef struct_process;

static unsigned long round_to_n(double x) {
  unsigned long base = 0x1000;
  // printf("-- 0x%lx * math.ceil(%f/0x%lx) = %f\n", base, x, base, x / base);
  return base * ceil(x / base);
}

static FILE *open_file(struct_process *process, int index, const char *proc) {
  char filename[SIZE];
  if (process->pid[index] <= 0) {
    fprintf(stderr, "Pid cannot be 0");
    exit(EXIT_FAILURE);
  } else {
    sprintf(filename, "/proc/%d/%s", process->pid[index], proc);
  }
  FILE *file = fopen(filename, "r");
  if (!file) {
    perror(filename);
    exit(EXIT_FAILURE);
  }

  return file;
}

static int parse_smaps(struct_process *process, int index, struct_maps *sm) {

  char found_map = 0;
  char line[BUFSIZ];

  char sbuffer[SIZE];
  FILE *file = open_file(process, index, "smaps");

  sprintf(sbuffer, "%lx-%lx", sm->addr_start, sm->addr_end);

  int n;

  while (fgets(line, sizeof(line), file)) {
    if (strstr(line, sbuffer) != NULL) {
      found_map = 1;
    }
    if (found_map) {
      if (VERBOSE) {
        printf("[DEBUG] %s", line);
      }
      sscanf(line, "%31[^:]: %d", sbuffer, &n);
      if (strcmp(sbuffer, "Pss") == 0) {
        process->total_pss = n;
        found_map = 0;
        break;
      }
    }
  }
  fclose(file);

  return 0;
}


static int parse_maps(struct_process *process, int index) {

  char line[BUFSIZ];
  char filename[SIZE];

  int shm_array[SIZE];
  char lpathname[SIZE];
  int nb_shm = 0;
  size_t len;
  int index_same_memory = 0;

  struct_maps *sm = malloc(sizeof(*sm));
  if (sm == NULL) {
    printf("Failed to malloc struct_maps array\n");
    exit(1);
  }
  memset(sm, '\0', sizeof(*sm));

  FILE *file = open_file(process, index, "maps");

  int k = 0, max_value=0, value=0;
  while (fgets(line, sizeof(line), file)) {
    memset(lpathname, '\0', SIZE);

    sscanf(line, "%lx-%lx %4c %x %x:%x %lu %s", &sm->addr_start,
           &sm->addr_end, &sm->perms, &sm->offset, &sm->major,
           &sm->minor, &sm->inode, lpathname);
    sm->length = sm->addr_end - sm->addr_start;

    if (sm->length == process->memory) {
        if (VERBOSE)
            printf("[DEBUG] Start: %lx, End: %lx, Length: %lx\n", sm->addr_start, sm->addr_end, sm->length);
            parse_smaps(process, index, sm);
            if (process->total_pss > max_value){
                max_value = process->total_pss;
            }
    }
    k++;
  }

  process->total_pss = max_value;

  free(sm);

  fclose(file);

  return 1;
}

int execute_pgrep(struct_process *process) {

  FILE *fp;
  char path[SIZE];
  int nb_process = NB_PROCESS;

  strcpy(path, "/usr/bin/pgrep ");
  strncat(path, process->process_name, 15);

  /* Open the command for reading. */
  fp = popen(path, "r");
  if (fp == NULL) {
    printf("Failed to run command\n");
    exit(1);
  }

  process->pid = malloc(sizeof(int) * NB_PROCESS);
  if (process->pid == NULL) {
    printf("Failed to malloc pid array\n");
    exit(1);
  }

  /* Read the output a line at a time - output it. */
  while (fgets(path, sizeof(path), fp) != NULL) {
    if (index_process != 0 && index_process % nb_process == 0) {
      nb_process = (index_process * 2);
      if (VERBOSE)
        printf("[INFO] REALLOCATION pids array (%d -> %d)\n", index_process,
               nb_process);
      process->pid = realloc(process->pid, sizeof(int) * nb_process);
      if (process->pid == NULL) {
        printf("Failed to realloc pid array\n");
        exit(1);
      }
    }
    process->pid[index_process++] = atoi(path);
  }

  /* close */
  pclose(fp);

  return 0;
}

static int write_to_file(struct_process *process) {

  char buffer[SIZE];
  time_t timestamp = time(NULL);
  struct tm *pTime = localtime(&timestamp);

  strftime(buffer, SIZE, "%Y-%m-%dT%H:%M:%S.0Z", pTime);

  if (VERBOSE)
    printf("total_pss: %ld\n", process->total_pss);

  FILE *file = fopen(process->datapath, "a");
  if (!file) {
    perror(process->datapath);
    exit(EXIT_FAILURE);
  }

  fprintf(file, "%s,%ld\n", buffer, process->total_pss);

  fclose(file);

  return 1;
}

int main(int argc, char *argv[]) {

  struct_process process;
  process.total_pss = 0;

  strcpy(process.process_name, "qemu-system-x86_64");
  strcpy(process.datapath, "/tmp/data.csv");
  process.memory = 8;

  int opt;
  while ((opt = getopt(argc, argv, "vm:n:d:")) != -1) {
    switch (opt) {
    case 'v':
      VERBOSE = 1;
      break;
    case 'n':
      strncpy(process.process_name, optarg, SIZE);
      break;
    case 'd':
      strncpy(process.datapath, optarg, SIZE);
      break;
    case 'm':
      process.memory = atoi(optarg);
      if (process.memory <= 0) {
        fprintf(stderr, "Memory must be > 0\n");
        exit(EXIT_FAILURE);
      }
      break;
    default:
      fprintf(stderr, "Usage: %s [-v ] [-d datapath] [-n name of the process] [-m memory_in_mb]\n",
              argv[0]);
      exit(EXIT_FAILURE);
    }
  }

  process.memory = process.memory * 1024 * 1024;

  if (execute_pgrep(&process) < 0) {
    exit(EXIT_FAILURE);
  }

  for (int i = 0; i < index_process; i++) {
    parse_maps(&process, i);
  }

  if (index_process == 0) {
    fprintf(stderr, "[ERROR] %s process was not found\n", process.process_name);
    exit(EXIT_FAILURE);
  }

  if (write_to_file(&process) < 0) {
    exit(EXIT_FAILURE);
  }

  free(process.pid);

  return 1;
}

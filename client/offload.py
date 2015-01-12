#! /bin/env python  
import socket             
import numpy as np
#from interruptible_pool import InterruptiblePool
import multiprocessing
import os

port = 5001                
mics = [("mic0", 24), ("mic1", 24)]
#cpus = [("localhost", 4)]
cpus = []

files_upload = ["../../megno_grid/nbody"]

jobs = []
for a in np.linspace(2.,3.,10):
    for e in np.linspace(0.,.1,10):
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

for w,worker in enumerate(workers):
    wref[w].join()

np.save("results",np.array(map(float, results)))


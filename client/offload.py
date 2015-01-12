#! /bin/env python  
import socket             
import numpy as np
#from interruptible_pool import InterruptiblePool
import multiprocessing

port = 5001                
mics = [("mic0", 24), ("mic1", 24)]
cpus = [("localhost", 4)]
l = multiprocessing.Lock()

workers = []

def generate_workers(resource):
    hostname, numthreads = resource
    i = 0
    for i in xrange(numthreads):
        workers.append((hostname, i))

for mic in mics:
    generate_workers(mic)
for cpu in cpus:
    generate_workers(cpu)


jobs = []
j = 0 
for a in np.linspace(2.,3.,10):
    for e in np.linspace(0.,1.,10):
        workstring = "./nbody --a=%.8e --e=%.8e" % (a,e)
        jobs.append(workstring)
        j+=1
status = multiprocessing.Array("d",len(jobs), lock=l)
for i in xrange(len(jobs)):
    status[i] = 0
results = [None]*len(jobs)

def worker_master(worker,l):
    hostname, i  = worker
    for j in xrange(len(jobs)):
        if status[j]>0:
            continue
        else:
            status[j] = 1
        workstring = jobs[j]
        print "Sending \"%s\" (%d) to %s (%d)" % (workstring, j, hostname, i)
        s = socket.socket()    
        s.connect((hostname, port))
        s.send(workstring)
        print s.recv(1024)
        s.close


print "Workers: %d" %len(workers)
print "Jobs:    %d" %len(jobs)

# Local pool, no work done here, only for communication
wref = len(workers)*[None]
for w,worker in enumerate(workers):
    wref[w] = multiprocessing.Process(target=worker_master, args=(worker,l))
    wref[w].start()

for w,worker in enumerate(workers):
    wref[w].join()


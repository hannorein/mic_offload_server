#! /bin/env python  
import socket             
import numpy as np
from interruptible_pool import InterruptiblePool
from multiprocessing import Lock

port = 5001                
mics = [("mic0", 24), ("mic1", 24)]
cpus = [("localhost", 4)]
l = Lock()

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
        jobs.append((j,workstring))
results = []*len(jobs)

def worker_master(worker):
    hostname, i = worker
    l.acquire()
    while len(jobs)>0:
        j, workstring = jobs.pop()
        l.release()
        print "Sending \"%s\" to %s (%d)" % (workstring, hostname, i)

        l.acquire()
        #results[j] = workstring
    l.release()
   # s = socket.socket()    
   # s.connect((mic, port))
   # s.send(w)
   # print s.recv(1024)
   # s.close
    

# Local pool, no work done here, only for communication
pool = InterruptiblePool(len(workers))
pool.map(worker_master, workers)


#!/usr/bin/python
# Import other modules
import numpy as np
import math
import os
import matplotlib; matplotlib.use("pdf")
import matplotlib.pyplot as pl

#extent = [a.min(), e.max(), e.min(), e.max()]
res = np.load("results.npy")
N = int(np.sqrt(len(res)))
pl.imshow(np.array(res).reshape((N,N)), vmin=1.8, vmax=4., aspect='auto', origin="lower", interpolation='nearest', cmap="RdYlGn_r" )
cb1 = pl.colorbar()
cb1.solids.set_rasterized(True)
cb1.set_label("MEGNO stability indicator $\\langle Y \\rangle$")
#pl.xlim(extent[0],extent[1])
#pl.ylim(extent[2],extent[3])
pl.xlabel("$a$")
pl.ylabel("$e$")

pl.savefig("megno.pdf")

### Show plot (OSX only)
os.system("open megno.pdf")

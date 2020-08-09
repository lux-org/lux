from scipy.stats import kurtosis
from typing import List
import pandas as pd
import math
import matplotlib as plot
def peakScore(data, interestVar:str = "", filterVar:str = "", filterVal:str = ""):
    if type(data) == pd.core.series.Series:
        q75, q25 = np.percentile(data, [75 ,25])
        iqr = q75 - q25
        bin_width = 2*iqr/math.pow(len(data),1/3)
        dataRange = max(data)-min(data)
        
        numBins = int(dataRange/bin_width)
        (binnedData, bins, patches) = plot.hist(data, bins=numBins, label='hst')

        return len(get_persistent_homology(binnedData))

class Peak:
    def __init__(self, startidx):
        self.born = self.left = self.right = startidx
        self.died = None

    def get_persistence(self, seq):
        return float("inf") if self.died is None else seq[self.born] - seq[self.died]

#given a list of binned values, find the peaks based on persistent homology
def get_persistent_homology(seq):
    peaks = []
    # Maps indices to peaks
    idxtopeak = [None for s in seq]
    # Sequence indices sorted by values
    indices = range(len(seq))
    indices = sorted(indices, key = lambda i: seq[i], reverse=True)

    # Process each sample in descending order
    for idx in indices:
        lftdone = (idx > 0 and idxtopeak[idx-1] is not None)
        rgtdone = (idx < len(seq)-1 and idxtopeak[idx+1] is not None)
        il = idxtopeak[idx-1] if lftdone else None
        ir = idxtopeak[idx+1] if rgtdone else None

        # New peak born
        if not lftdone and not rgtdone:
            peaks.append(Peak(idx))
            idxtopeak[idx] = len(peaks)-1

        # Directly merge to next peak left
        if lftdone and not rgtdone:
            peaks[il].right += 1
            idxtopeak[idx] = il

        # Directly merge to next peak right
        if not lftdone and rgtdone:
            peaks[ir].left -= 1
            idxtopeak[idx] = ir

        # Merge left and right peaks
        if lftdone and rgtdone:
            # Left was born earlier: merge right to left
            if seq[peaks[il].born] > seq[peaks[ir].born]:
                peaks[ir].died = idx
                peaks[il].right = peaks[ir].right
                idxtopeak[peaks[il].right] = idxtopeak[idx] = il
            else:
                peaks[il].died = idx
                peaks[ir].left = peaks[il].left
                idxtopeak[peaks[ir].left] = idxtopeak[idx] = ir

    # This is optional convenience
    sorted_peaks = sorted(peaks, key=lambda p: p.get_persistence(seq), reverse=True)
    output = {}
    for p in range(0, len(peaks)):
        output[p] = peaks[p].get_persistence(seq)
    #return sorted(peaks, key=lambda p: p.get_persistence(seq), reverse=True)
    return(output)

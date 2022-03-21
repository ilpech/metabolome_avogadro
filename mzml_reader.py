# use https://github.com/OpenMS/OpenMS cpp code to find headers of pyopenms
import os
import pyopenms as ms
import numpy as np

from varname.helpers import debug

if __name__ == '__main__':
    exp = ms.MSExperiment()
    ms.MzMLFile().load(
        os.path.join('testdata', '02_PM_30102018_1.mzML'), 
        exp
    )
    debug(exp.getMSLevels())
    debug(exp.getNrSpectra())
    debug(exp.getNrChromatograms())
    for i in range(exp.getNrSpectra()):
        spectrum = exp.getSpectrum(i)
        peaks = spectrum.get_peaks()
        print('spectr', i, peaks[0].shape, peaks[1].shape)
        debug(peaks[0].min())
        debug(peaks[0].max())
        debug(peaks[1].min())
        debug(peaks[1].max())
    for i in range(exp.getNrChromatograms()):
        chrom = exp.getChromatogram(i)
        peaks = chrom.get_peaks()
        print(peaks)
        print('chr', i, peaks[0].shape, peaks[1].shape)
        debug(peaks[0].min())
        debug(peaks[0].max())
        debug(peaks[1].min())
        debug(peaks[1].max())

    
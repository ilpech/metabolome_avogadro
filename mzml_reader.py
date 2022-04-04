# use https://github.com/OpenMS/OpenMS cpp code to find headers of pyopenms
import os
import pyopenms as ms
import numpy as np

from varname.helpers import debug

if __name__ == '__main__':
    seq = ms.AASequence.fromString("FPIANGDER") # create AASequence object from string representation
    prefix = seq.getPrefix(4) # extract prefix of length 4
    suffix = seq.getSuffix(5) # extract suffix of length 5
    concat = seq + seq # concatenate two sequences
    print(seq.getMonoWeight())

    # print string representation of sequences
    print("Sequence:", seq)
    print("Prefix:", prefix)
    print("Suffix:", suffix)
    print("Concatenated:", concat)
    print(concat.getMonoWeight())
    print(seq.getMZ(2))
    for aa in seq:
        # print(aa)
        print(aa.getName(), aa.getFormula())
    print(seq.getFormula())
    # exit()
    exp = ms.MSExperiment()
    ms.MzMLFile().load(
        os.path.join('testdata', '02_PM_30102018_1.mzML'), 
        exp
    )
    gf = ms.GaussFilter()
    param = gf.getParameters()
    param.setValue("gaussian_width", 1.0) # needs wider width
    gf.setParameters(param)
    exp.updateRanges()
    ff = ms.FeatureFinder()
    ff.setLogType(ms.LogType.CMD)
    name = "centroided"
    features = ms.FeatureMap()
    seeds = ms.FeatureMap()
    params = ms.FeatureFinder().getParameters(name)
    ff.run(name, exp, features, params, seeds)

    features.setUniqueIds()
    fh = ms.FeatureXMLFile()
    fh.store("output.featureXML", features)
    print("Found", features.size(), "features")
    exit()
    # gf.filterExperiment(exp) 
    # exit(0)
    # ms.PeakPickerHiRes().pickExperiment(exp, exp) # pick all spectra
    debug(exp.getMSLevels())
    debug(exp.getNrSpectra())
    debug(exp.getNrChromatograms())
    for i in range(exp.getNrSpectra()):
        spectrum = exp.getSpectrum(i)
        mz, intensity = spectrum.get_peaks()
        # for j in range(len(mz)):
        #     debug(mz[j])
        #     debug(intensity[j])
        # exit()

        print('spectr', i, mz.shape, intensity.shape)
        debug(mz.min())
        debug(mz.max())
        debug(intensity.min())
        debug(intensity.max())
    for i in range(exp.getNrChromatograms()):
        chrom = exp.getChromatogram(i)
        peaks = chrom.get_peaks()
        for j in range(len(peaks[0])):
            debug(peaks[0][j])
            debug(peaks[1][j])
        print(peaks)
        print('chr', i, peaks[0].shape, peaks[1].shape)
        debug(peaks[0].min())
        debug(peaks[0].max())
        debug(peaks[1].min())
        debug(peaks[1].max())

    
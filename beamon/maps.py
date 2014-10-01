import epics
import ipdb
import xraydb

xdb = xraydb.xrayDB()

maps_settings = """
This file will set some MAPS settings mostly do do with fitting
VERSION: 0
DETECTOR_ELEMENTS: 4
MAX_NUMBER_OF_PROCESSORS_TO_USE: 3
QUICK_DIRTY: 1
XRF_BIN: 0.000000
NNLS: 0
XANES_SCAN: 0
DETECTOR_TO_START_WITH: 0
"""

maps_fit_parameters_override = """
This file will override default fit settings for the maps program for a 3 element detector remove: removeme_*elementdetector_to make it work.
NOTE: the filename MUST be maps_fit_parameters_override.txt
VERSION:      5.00000
DATE: Wed Sep 17 18:20:25 2014
   put below the number of detectors that were used to acquire spectra. IMPORTANT:
   this MUST come after VERSION, and before all other options!
DETECTOR_ELEMENTS:       1
   give this file an internal name, whatever you like
IDENTIFYING_NAME_[WHATEVERE_YOU_LIKE]:automatic
   list the elements that you want to be fit. For K lines, just use the element
   name, for L lines add _L, e.g., Au_L, for M lines add _M
ELEMENTS_TO_FIT: {elements_to_fit:s}
   list the element combinations you want to fit for pileup, e.g., Si_Si, Si_Si_Si, Si_Cl, etc
ELEMENTS_WITH_PILEUP: K_K
   offset of energy calibration, in kev
CAL_OFFSET_[E_OFFSET]:   -0.0041840752
CAL_OFFSET_[E_OFFSET]_MAX:      0.50000000
CAL_OFFSET_[E_OFFSET]_MIN:     -0.50000000
   slope of energy calibration, in leV / channel
CAL_SLOPE_[E_LINEAR]:    0.0095216077
CAL_SLOPE_[E_LINEAR]_MAX:     0.015000000
CAL_SLOPE_[E_LINEAR]_MIN:    0.0079999994
   quadratic correction for energy calibration, unless you know exactly what you are doing, please leave it at 0.
CAL_QUAD_[E_QUADRATIC]:      0.00000000
CAL_QUAD_[E_QUADRATIC]_MAX:  9.9999997e-005
CAL_QUAD_[E_QUADRATIC]_MIN: -9.9999997e-005
    energy_resolution at 0keV
FWHM_OFFSET:     0.097217640
    energy dependence of the energy resolution
FWHM_FANOPRIME:   0.00022440446
    incident energy
COHERENT_SCT_ENERGY:       {energy:f}
    upper contstraint for the incident energy
COHERENT_SCT_ENERGY_MAX:       {coherent_energy_max:f}
    lower contstraint for the incident energy
COHERENT_SCT_ENERGY_MIN:       {coherent_energy_min:f}
    angle for the compton scatter (in degrees)
COMPTON_ANGLE:       87.274598
COMPTON_ANGLE_MAX:       170.00000
COMPTON_ANGLE_MIN:       70.000000
    additional width of the compton
COMPTON_FWHM_CORR:       1.5730172
COMPTON_STEP:      0.00000000
COMPTON_F_TAIL:      0.13308163
COMPTON_GAMMA:       3.0000000
COMPTON_HI_F_TAIL:    0.0039171793
COMPTON_HI_GAMMA:       3.0000000
    tailing parameters, see also Grieken, Markowicz, Handbook of X-ray spectrometry
    2nd ed, van Espen spectrum evaluation page 287.  _A corresponds to f_S, _B to
    f_T and _C to gamma
STEP_OFFSET:      0.00000000
STEP_LINEAR:      0.00000000
STEP_QUADRATIC:      0.00000000
F_TAIL_OFFSET:     0.003
F_TAIL_LINEAR:  1.6940659e-021
F_TAIL_QUADRATIC:      0.00000000
KB_F_TAIL_OFFSET:      0.05
KB_F_TAIL_LINEAR:      0.00000000
KB_F_TAIL_QUADRATIC:      0.00000000
GAMMA_OFFSET:       2.2101209
GAMMA_LINEAR:      0.00000000
GAMMA_QUADRATIC:      0.00000000
    snip width is the width used for estimating background. 0.5 is typically a good start
SNIP_WIDTH:      0.50000000
    set FIT_SNIP_WIDTH to 1 to fit the width of the snipping for background estimate, set to 0 not to. Only use if you know what it is doing!
FIT_SNIP_WIDTH:       0
    detector material: 0= Germanium, 1 = Si
DETECTOR_MATERIAL:   1
    beryllium window thickness, in micrometers, typically 8 or 24
BE_WINDOW_THICKNESS:       24.000000
thickness of the detector chip, e.g., 350 microns for an SDD
DET_CHIP_THICKNESS:       350.00000
thickness of the Germanium detector dead layer, in microns, for the purposes of the NBS calibration
GE_DEAD_LAYER:      0.00000000
    maximum energy value to fit up to [keV]
MAX_ENERGY_TO_FIT:       {max_energy:f}
    minimum energy value [keV]
MIN_ENERGY_TO_FIT:       {min_energy:f}
    this allows manual adjustment of the branhcing ratios between the different lines of L1, L2, and L3.
    note, the numbers that are put in should be RELATIVE modifications, i.e., a 1 will correspond to exactly the literature value,
    0.8 will correspond to to 80% of that, etc.
BRANCHING_FAMILY_ADJUSTMENT_L: Pt_L, 0., 1., 1.
BRANCHING_FAMILY_ADJUSTMENT_L: Gd_L, 1., 1., 1.
BRANCHING_FAMILY_ADJUSTMENT_L: Sn_L, 0., 0., 1.
BRANCHING_FAMILY_ADJUSTMENT_L: I_L, 1., 1., 1.
    this allows manual adjustment of the branhcing ratios between the different L lines, such as La 1, la2, etc.
    Please note, these are all RELATIVE RELATIVE modifications, i.e., a 1 will correspond to exactly the literature value, etc.
    all will be normalized to the La1 line, and the values need to be in the following order:
    La1, La2, Lb1, Lb2, Lb3, Lb4, Lg1, Lg2, Lg3, Lg4, Ll, Ln
    please note, the first value (la1) MUST BE A 1. !!!
BRANCHING_RATIO_ADJUSTMENT_L: Pb_L, 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.
BRANCHING_RATIO_ADJUSTMENT_L: I_L, 1., 1., 0.45, 1.0, 0.45, 0.45, 0.6, 1., 0.3, 1., 1., 1.
BRANCHING_RATIO_ADJUSTMENT_L: Gd_L, 1., 0.48, 0.59, 0.98, 0.31, 0.08, 0.636, 1., 0.3, 1., 1., 1.
BRANCHING_RATIO_ADJUSTMENT_L: Sn_L, 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.
    this allows manual adjustment of the branhcing ratios between the different K lines, such as Ka1, Ka2, Kb1, Kb2
    Please note, these are all RELATIVE RELATIVE modifications, i.e., a 1 will correspond to exactly the literature value, etc.
    all will be normalized to the Ka1 line, and the values need to be in the following order:
    Ka1, Ka2, Kb1(+3), Kb2
    please note, the first value (Ka1) MUST BE A 1. !!!
BRANCHING_RATIO_ADJUSTMENT_K: Na, 1., 1., 4.0, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Mg, 1., 1., 3.6, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Al, 1., 1., 3.3, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Si, 1., 1., 2.9, 1.
BRANCHING_RATIO_ADJUSTMENT_K: P, 1., 1., 2.75, 1.
BRANCHING_RATIO_ADJUSTMENT_K: S, 1., 1., 2.6, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Cl, 1., 1., 2.5, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Ar, 1., 1., 2.2, 1.
BRANCHING_RATIO_ADJUSTMENT_K: K, 1., 1., 1.9, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Ca, 1., 1., 1.7, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Ti, 1., 1., 1.6, 1.
BRANCHING_RATIO_ADJUSTMENT_K: V, 1., 1., 1.4, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Cr, 1., 1., 1.35, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Mn, 1., 1., 1.3, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Fe, 1., 1., 1.2, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Co, 1., 1., 1.1, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Ni, 1., 1., 1.05, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Cu, 1., 1., 1.0, 1.
BRANCHING_RATIO_ADJUSTMENT_K: Zn, 1., 1., 1.0, 1.
    the parameter adds the escape peaks (offset) to the fit if larger than 0. You should not enable Si and Ge at the same time, ie, one of these two values should be zero
SI_ESCAPE_FACTOR:      0.00000000
GE_ESCAPE_FACTOR:      0.00000000
    this parameter adds a component to the escape peak that depends linear on energy
LINEAR_ESCAPE_FACTOR:      0.00000000
    the parameter enables fitting of the escape peak strengths. set 1 to enable, set to 0 to disable. (in matrix fitting always disabled)
SI_ESCAPE_ENABLE:       0
GE_ESCAPE_ENABLE:       0
    the lines (if any) below will override the detector names built in to maps. please modify only if you are sure you understand the effect
SRCURRENT:S:SRcurrentAI
US_IC:2xfm:scaler3_cts1.B
DS_IC:2xfm:scaler3_cts1.C
DPC1_IC:2xfm:scaler3_cts2.A
DPC2_IC:2xfm:scaler3_cts2.B
CFG_1:2xfm:scaler3_cts3.B
CFG_2:2xfm:scaler3_cts3.C
CFG_3:2xfm:scaler3_cts3.D
CFG_4:2xfm:scaler3_cts4.A
CFG_5:2xfm:scaler3_cts4.B
CFG_6:2xfm:scaler3_cts4.C
CFG_7:2xfm:scaler3_cts4.D
CFG_8:2xfm:scaler3_cts5.A
CFG_9:2xfm:scaler3_cts5.A
ELT1:dxpXMAP2xfm3:mca4.ELTM
ERT1:dxpXMAP2xfm3:mca4.ERTM
    the lines below (if any) give backup description of IC amplifier sensitivity, in case it cannot be found in the mda file
      for the amps, the _NUM value should be between 0 and 8 where 0=1, 1=2, 2=5, 3=10, 4=20, 5=50, 6=100, 7=200, 8=500
      for the amps, the _UNIT value should be between 0 and 3 where 0=pa/v, 1=na/v, 2=ua/v 3=ma/v
US_AMP_SENS_NUM:5
US_AMP_SENS_UNIT:1
DS_AMP_SENS_NUM:1
DS_AMP_SENS_UNIT:1%
"""



def generate_maps_settings():
    return maps_settings

def generate_maps_override(debug=False, debug_energy_33=11.0, debug_energy_55=2.5):
    if not debug:
        energy_33 = epics.caget('ID02ud:EnergySet.VAL')
        energy_55 = epics.caget('ID02ds:EnergySet.VAL')
    else:
        energy_33 = debug_energy_33
        energy_55 = debug_energy_55
    d = {}
    if energy_55 < 4.5: # Beamsharing
        d['energy'] = energy_33
    elif energy_33 > 17.0:
        d['energy'] = energy_55
    else:
        d['energy'] = energy_33

    d['max_energy'] = d['energy']+1.0
    d['min_energy'] = 1.5
    # Get elements to fit from "maps_admin" medm screen
    d['elements_to_fit'] = ''
    for i in range(1,81):
        if debug:
            if i not in [5, 16, 26, 30]:
                continue
        else:
            if epics.caget('2xfmS1:element_{:d}.VAL'.format(i))==0:
                continue

        print('Adding {:s}.'.format(xdb.symbol(i)))

        emission_lines = xdb.xray_lines(i)
        for line in emission_lines:
            emission_energy = 1e-3*emission_lines[line][0]
            if emission_energy<=d['energy'] and emission_energy>d['min_energy']:
                emission_line = xdb.symbol(i)+'_'+line[0]
                if emission_line not in d['elements_to_fit']:
                    if len(d['elements_to_fit']) == 0:
                        d['elements_to_fit'] = emission_line
                    else:
                        d['elements_to_fit'] += ', '+emission_line

    d['coherent_energy_max'] = d['energy']+0.3
    d['coherent_energy_min'] = d['energy']-0.3

    return maps_fit_parameters_override.format(**d)

if __name__ == '__main__':
    print('Generating maps settings...\n\n\n')
    print(generate_maps_settings())
    print('Generating maps override...\n\n\n')
    print(generate_maps_override(debug=True))



#! /usr/bin/env python
# -*- coding: utf-8 -*-


""" Module associated to standard stars used for calibration """

import pyifu
import inspect, os

import numpy as np

from glob import glob
from astropy.io import fits

__all__ = ["std_radec", "std_spectrum", "download_calspec"]

_DATASOURCE = os.getenv('CALSPECPATH', default=os.path.dirname(os.path.realpath(__file__))+"/data/")

_name = [0,12]
_ra   = [12,25]
_dec  = [25,38]
_pm_x = [38, 45]
_pm_y = [45, 52]
_SimName = [53,-1]

# Source
CALSPEC_SERVER = "ftp.stsci.edu"
CALSPEC_DIR    = "cdbs/current_calspec/"
# ===================== #
#   Main Tools          #
# ===================== #
def std_radec(stdname):
    """ get the ra and dec of the standard star

    Parameters
    ----------
    stdname: string
        name of the standard star.
        Caution: case sensitive. 

    Returns
    -------
    Target (astrobject's)
    """
    caldata = calspec_data()
    if stdname not in caldata.keys():
        print('known targets', ", ".join(caldata.keys()))
        raise ValueError("Unknown standard '%s' [be careful. Case sensitive]"%stdname)
    
    return caldata[stdname]["ra"],caldata[stdname]["dec"]

def std_spectrum(stdname):
    """ """
    from pyifu.spectroscopy import get_spectrum
    std_  = fits.open(calspec_file(stdname))
    # - the arrays
    lbda = std_[1].data["WAVELENGTH"]
    flux = std_[1].data["FLUX"]
    var  = std_[1].data["STATERROR"]**2 + std_[1].data["SYSERROR"]**2
    return get_spectrum(lbda, flux, variance=var)


    
# ===================== #
#   Internal Tools      #
# ===================== #
def calspec_data():
    """ dictionary containing the CalSpec stellar names and coordinates.
    Source: Table 2 of http://www.stsci.edu/hst/observatory/crds/calspec.html
    
    Returns
    -------
    dict
    """
    calfile = open(_DATASOURCE+"calspec_sources.dat").read().splitlines()
    
    return { str(l[_name[0]:_name[1]]).replace(" ",""): {
        "ra": ":".join(str(l[_ra[0]:_ra[1]]).replace("\t","").split()),
        "dec": ":".join(str(l[_dec[0]:_dec[1]]).replace("\t","").split())
        }
          for l in calfile[1:] }
        
def calspec_file(stdname, download=True):
    """ get the fullpath of file containing the standard star spectrum.

    Parameters
    ----------
    stdname: string
        name of the standard star.
        Caution: case sensitive. 

    Returns
    -------
    string (FULLPATH)
    """
    specfile = glob(_DATASOURCE+"%s_*.fits"%stdname.lower())
    if len(specfile)==0:
        if download:
            download_calspec(stdname)
            return calspec_file(stdname, download=False)
        else:
            raise IOError("Currently no spectra for %s. \n"%stdname+\
                            "Look for it from http://www.stsci.edu/ftp/cdbs/current_calspec/ and save in at %s"%(_DATASOURCE))
    return specfile[-1]
                        
    
def download_calspec(stdname, outdir=None):
    """ look at the calspec spectra under ftp.stsci.edu/cdbs/current_calspec/ 
    (see get_list_of_calspec_files()) and download the one corresponding to stdname
    The files are saved under the ./data/calspec/ directory except if said otherwise.
    
    Parameters
    ----------
    stdname: [string]
        name of the standard star.
        Caution: case sensitive. 
        
    outdir: [string/None] -optional-
        Path to the directory where the file should be downloaded.
        By default it will be the data directory of the package.

    Returns
    -------
    Void
    """
    
    from astropy.utils.data import download_file
    list_of_calspec_files = get_list_of_calspec_files()
    if outdir is None:
        outdir = _DATASOURCE
        
    for file_to_dl in [f_ for f_ in list_of_calspec_files
                           if stdname.lower()+"_" in f_.lower()]:
        filedl = download_file("ftp://"+CALSPEC_SERVER+"/"+CALSPEC_DIR+file_to_dl)
        os.rename(filedl, outdir+file_to_dl.lower())
        

def get_list_of_calspec_files():
    """ get the list of all the CalSpec files that exist under 
    ftp.stsci.edu/cdbs/current_calspec/ 
    
    Returns
    -------
    list 
    """
    from ftplib import FTP
    ftp = FTP(CALSPEC_SERVER)
    ftp.login()
    ftp.cwd(CALSPEC_DIR)
    list_of_files = ftp.nlst()
    ftp.close()
    return list_of_files

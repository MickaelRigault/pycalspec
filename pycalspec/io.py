#! /usr/bin/env python
# -*- coding: utf-8 -*-


""" Module associated to standard stars used for calibration """

import inspect, os
import shutil
import warnings
import numpy as np

from glob import glob
from astropy.io import fits

__all__ = ["std_radec", "std_spectrum", "download_calspec"]

_DATASOURCE = os.getenv('CALSPECPATH', None)

_name = [0,12]
_ra   = [12,25]
_dec  = [25,38]
_pm_x = [38, 45]
_pm_y = [45, 52]
_SimName = [53,-1]

# Source
CALSPEC_SERVER = "ftp.stsci.edu"
CALSPEC_DIR    = "cdbs/current_calspec/"

LOCAL_CURRENT_CALSPEC = os.path.join(_DATASOURCE, "current_calspec_list.txt")
LOCAL_CALSPEC = os.path.join(_DATASOURCE, "calspec_list.txt")
CURRENT_CALSPEC_ARCHIVE_URL = "https://archive.stsci.edu/hlsps/reference-atlases/cdbs/current_calspec"
CALSPEC_ARCHIVE_URL = "https://archive.stsci.edu/hlsps/reference-atlases/cdbs/calspec"
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
    stdname = _calspec_data_parse_name_(stdname).upper()
    if stdname not in caldata.keys():
        print('known targets', ", ".join(list(caldata.keys())))
        raise ValueError("Unknown standard '%s' [be careful. Case sensitive]"%stdname)
    
    return caldata[stdname]["ra"],caldata[stdname]["dec"]

def std_spectrum(stdname):
    """ """
    std_  = fits.open(calspec_file(stdname))
    # - the arrays
    lbda = std_[1].data["WAVELENGTH"]
    flux = std_[1].data["FLUX"]
    
    if "STATERROR" in std_[1].data.names and "SYSERROR" in std_[1].data.names:
        var  = std_[1].data["STATERROR"]**2 + std_[1].data["SYSERROR"]**2
        
    elif "SYSERROR" in std_[1].data.names:
        var  = std_[1].data["SYSERROR"]**2
        
    elif "STATERROR" in std_[1].data.names:
        var  = std_[1].data["STATERROR"]**2
        
    else:
        var = None
        
    return lbda, flux, variance=var


def _calspec_data_parse_name_(stdname):
    """ """
    if "BD+" in stdname:
        return stdname.replace("d","")
    return stdname

def _calspec_file_parse_name_(stdname):
    """ """
    return stdname.replace("+","_").lower()
    

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
    calfile = os.path.join(_DATASOURCE, "calspec_sources.dat").read().splitlines()
    
    return { str(l[_name[0]:_name[1]]).replace(" ","").upper(): {
        "ra": ":".join(str(l[_ra[0]:_ra[1]]).replace("\t","").split()),
        "dec": ":".join(str(l[_dec[0]:_dec[1]]).replace("\t","").split())
        }
          for l in calfile[1:] }
        
def calspec_file(stdname, use_current=True, download=True):
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
    stdname = _calspec_file_parse_name_(stdname)
    specfile = glob( os.path.join(_DATASOURCE,f"{stdname}_*.fits") )
    if len(specfile)==0:
        if download:
            download_calspec(stdname)
            return calspec_file(stdname, download=False)
        else:
            raise IOError("Currently no spectra for %s. \n"%stdname+\
                            "Look for it from http://www.stsci.edu/ftp/cdbs/current_calspec/ and save in at %s"%(_DATASOURCE))
    return np.sort(specfile)[-1]
                        
    
def download_calspec(stdname, outdir=None, warn=True):
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
    if outdir is None:
        outdir = _DATASOURCE

    if not os.path.isdir(outdir):
        os.makedirs(outdir, exist_ok=True)

    
    list_of_calspec_files = get_list_of_calspec_files(use_current=True)
    files_to_dl = [f_ for f_ in list_of_calspec_files if stdname.lower()+"_" in f_.lower()]
    source = CURRENT_CALSPEC_ARCHIVE_URL
    if len(files_to_dl) ==0:
        list_of_calspec_files = get_list_of_calspec_files(use_current=False)
        files_to_dl = [f_ for f_ in list_of_calspec_files if stdname.lower()+"_" in f_.lower()]
        source = CALSPEC_ARCHIVE_URL
    if len(files_to_dl) ==0:
        raise ValueError(f"no calspec file corresponding to {stdname} found in calspec_current or calspec.")
    
        
    for file_to_dl in files_to_dl:
        filedl = download_file( os.path.join(source,file_to_dl) )
        fileout = os.path.join(outdir,file_to_dl.lower())
        if warn:
            warnings.warn(f"Storing {file_to_dl} here {fileout}")
        shutil.move(filedl, fileout)
        

def get_list_of_calspec_files(use_current=True, force_dl=False):
    """ """
    datafile = LOCAL_CALSPEC if not use_current else LOCAL_CURRENT_CALSPEC
    if not os.path.isfile(datafile) or force_dl:
        return download_list_of_calspec_files(use_current,store=True)
    return open(datafile).read().splitlines()
        
def download_list_of_calspec_files(use_current=True, store=True):
    """ get the list of all the CalSpec files that exist under 
    ftp.stsci.edu/cdbs/current_calspec/ 
    
    Returns
    -------
    list 
    """
    import requests
    calspeclit = requests.get(CALSPEC_ARCHIVE_URL if not use_current else \
                                  CURRENT_CALSPEC_ARCHIVE_URL)
    list_of_files = [l.split("</a>")[0].split(">")[-1]
                         for l in calspeclit.text.splitlines() if ".fits" in l]
    if store:
        fileout = LOCAL_CALSPEC if not use_current else LOCAL_CURRENT_CALSPEC
        dirout = os.path.dirname(fileout)
        if not os.path.isdir( dirout):
            os.makedirs(dirout, exist_ok=True)
            
        with open(fileout, "w") as fileout_:
            for l in list_of_files:
                fileout_.write(l+"\n")
    return list_of_files

**[简体中文](https://github.com/tgraphite/EEM-Scattering-Remover/README.md) | English**

## EEM Scattering Remover (ESR) 

1、Recognize Rayleigh、Raman、2nd order Rayleigh scattering stripes automatically, regardless of instruments or wavelength ranges.
2、Employ relaxation algorithm to correct the edges of scattering areas removed.
3、Easy to use and easy to tune, quick preview, Support **FULL-AUTO** silent batch mode.


----


## Usage
0) Prepare .txt or .xlsx data file(s).   

The .txt data file mentioned here should in the format like below, seperated by [Space] or [Tab]：  

    [space or 0.0]	200	205	210	... (excitations)
    250		1.823	1.785	1.13	...
    252		1.823	1.785	1.13	...
    254		1.823	1.785	1.13	...	
    ...		...	...	...	(absorptions)
    (emissions)
    (end of file)

The .xlsx data file mentioned here should in the format like below:

| (any content) | | | | | | 
| ---- | ---- | ---- | ---- | --- | --- |
| ... | |
| **Data points** | |
| [space or 0.0] | 200 | 205 | 210 | ... | (excitations) |
| 250 | 1.823 | 1.785 | 1.13 | ... | 
| 252 | 1.823 | 1.785 | 1.13 | ... | 
| 254 | 1.823 | 1.785 | 1.13 | ... | 
| ... | ... | ... | ... | (absorptions)
| (emissions)
| (end of file)

1) Double click and run esr.exe  
2) Wait for seconds, drag a data file or a directory including multiple data files (full-auto silent batch mode) into the command line view directly, or input the full path instead. Press Enter to continue.   
3) The program will open a preview picture. Close the preview directly after checked. In full-auto mode, the preview will be saved directly without showing up.
4) The data and preview picture will be saved automatically. Press any key to exit.  
5) Chage the parameters in esr-params.txt to tune the algorithm. If the parameter file is missing or wrong, default values will be taken.  

Most of the errors are caused by **wrong data format**, copying and pasting plain text data from excel directly into a new blank txt file is suggested.   

**Mention**: No NON-ASCII characters in esr-params.txt, No [space] and NON-ASCII characters in any file path.


----

## Parameters setting

  
|  Parameter  |  Default  |  Comment |
| ---- | ---- | ---- |
| ray-remove-rad | 10.0 | Radius for Rayleigh scattering stripe removals.
| secray-remove-rad | 12.0 | Like above, for 2nd order Rayleigh.
| ram-remove-rad | 10.0 | Like above, for Raman.
| ram-wavenumber | 3600.0 | Wavenumber of Raman scattering in the solvent. For water it is about 3600.
| relaxation-disp | 3.0 |  Displacement for relaxation applied on points removed. **Integer**. When a data point is removed (set to zero), the program will try to look for four neighbouring data points and use their mean value to fill the zero, the relaxation-disp decides where (how far) to find those neighbouring points. **The greater the relaxation-disp is, the more 'vague' the final figure will be, and vice versa.**

----

## Example
A simple and quick preview for a random sample.
![](./example.png)
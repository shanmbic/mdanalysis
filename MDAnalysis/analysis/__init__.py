# analysis module
# Part of MDAnalysis http://mdanalysis.googlecode.com
# Copyright (c) 2006-2010 Naveen Michaud-Agrawal, Elizabeth J. Denning, Oliver Beckstein
# Released under the GNU Public Licence, v2

"""
:mod:`MDAnalysis.analysis` --- Analysis code based on MDAnalysis
================================================================

The :mod:`MDAnalysis.analysis` sub-package contains various recipes and
algorithms that can be used to analyze MD trajectories.

If you use them please check if the documentation mentions any specifi caveats
and also if there are any published papers associated with these algorithms.

Available analysis modules
--------------------------

:mod:`~MDAnalysis.analysis.leaflet`
    Find lipids in the upper and lower (or inner and outer) leaflet of
    a bilayer; the algorithm can deal with any deformations as long as
    the two leaflets are topologically distinct.
  
:mod:`~MDAnalysis.analysis.contacts`
    Analyse the number of native contacts (relative to a reference state).
"""


# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDAnalysis --- http://www.MDAnalysis.org
# Copyright (c) 2006-2015 Naveen Michaud-Agrawal, Elizabeth J. Denning, Oliver
# Beckstein and contributors (see AUTHORS for the full list)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#
from __future__ import division
from six.moves import range

import numpy as np

from numpy.testing import (
    assert_, dec, raises, assert_raises, assert_equal, assert_array_equal
)

import MDAnalysis as mda
from MDAnalysis.analysis import base

from MDAnalysisTests.datafiles import PSF, DCD
from MDAnalysisTests import parser_not_found


class FrameAnalysis(base.AnalysisBase):
    """Just grabs frame numbers of frames it goes over"""
    def __init__(self, reader, **kwargs):
        super(FrameAnalysis, self).__init__(reader, **kwargs)
        self.traj = reader
        self.frames = []

    def _single_frame(self):
        self.frames.append(self._ts.frame)


class IncompleteAnalysis(base.AnalysisBase):
    def __init__(self, reader, **kwargs):
        super(IncompleteAnalysis, self).__init__(reader, **kwargs)


class OldAPIAnalysis(base.AnalysisBase):
    """for version 0.15.0"""
    def __init__(self, reader, **kwargs):
        self._setup_frames(reader, **kwargs)

    def _single_frame(self):
        pass


class TestAnalysisBase(object):
    @dec.skipif(parser_not_found('DCD'),
                'DCD parser not available. Are you using python 3?')
    def setUp(self):
        # has 98 frames
        self.u = mda.Universe(PSF, DCD)

    def tearDown(self):
        del self.u

    def test_default(self):
        an = FrameAnalysis(self.u.trajectory).run()
        assert_equal(an.n_frames, len(self.u.trajectory))
        assert_equal(an.frames, list(range(len(self.u.trajectory))))

    def test_start(self):
        an = FrameAnalysis(self.u.trajectory, start=20).run()
        assert_equal(an.n_frames, len(self.u.trajectory) - 20)
        assert_equal(an.frames, list(range(20, len(self.u.trajectory))))

    def test_stop(self):
        an = FrameAnalysis(self.u.trajectory, stop=20).run()
        assert_equal(an.n_frames, 20)
        assert_equal(an.frames, list(range(20)))

    def test_step(self):
        an = FrameAnalysis(self.u.trajectory, step=20).run()
        assert_equal(an.n_frames, 5)
        assert_equal(an.frames, list(range(98))[::20])

    def test_quiet(self):
        a = FrameAnalysis(self.u.trajectory, quiet=False)
        assert_(not a._quiet)

    @raises(NotImplementedError)
    def test_incomplete_defined_analysis(self):
        IncompleteAnalysis(self.u.trajectory).run()

    def test_old_api(self):
        OldAPIAnalysis(self.u.trajectory).run()


def test_filter_baseanalysis_kwargs():
    def bad_f(mobile, step=2):
        pass

    def good_f(mobile, ref):
        pass

    kwargs = {'step': 3, 'foo': None}

    assert_raises(ValueError, base._filter_baseanalysis_kwargs, bad_f, kwargs)

    base_kwargs, kwargs = base._filter_baseanalysis_kwargs(good_f, kwargs)

    assert_equal(1, len(kwargs))
    assert_equal(kwargs['foo'], None)

    assert_equal(4, len(base_kwargs))
    assert_equal(base_kwargs['start'], None)
    assert_equal(base_kwargs['step'], 3)
    assert_equal(base_kwargs['stop'], None)
    assert_equal(base_kwargs['quiet'], True)


def simple_function(mobile):
    return mobile.center_of_geometry()


def test_AnalysisFromFunction():
    u = mda.Universe(PSF, DCD)
    step = 2
    ana1 = base.AnalysisFromFunction(simple_function, mobile=u.atoms,
                                     step=step).run()
    ana2 = base.AnalysisFromFunction(simple_function, u.atoms,
                                     step=step).run()
    ana3 = base.AnalysisFromFunction(simple_function, u.trajectory, u.atoms,
                                     step=step).run()

    results = []
    for ts in u.trajectory[::step]:
        results.append(simple_function(u.atoms))
    results = np.asarray(results)

    for ana in (ana1, ana2, ana3):
        assert_array_equal(results, ana.results)


def test_analysis_class():
    ana_class = base.analysis_class(simple_function)
    assert_(issubclass(ana_class, base.AnalysisBase))
    assert_(issubclass(ana_class, base.AnalysisFromFunction))

    u = mda.Universe(PSF, DCD)
    step = 2
    ana = ana_class(u.atoms, step=step).run()

    results = []
    for ts in u.trajectory[::step]:
        results.append(simple_function(u.atoms))
    results = np.asarray(results)

    assert_array_equal(results, ana.results)

    assert_raises(ValueError, ana_class, 2)

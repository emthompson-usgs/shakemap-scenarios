# stdlib imports
import os
import sys
import filecmp
import shutil

# third party
import tempfile

from impactutils.io.cmd import get_command_output
from impactutils.testing.grd import grdcmp

from scenarios.utils import set_shakehome, set_vs30file, set_gmpe

homedir = os.path.dirname(os.path.abspath(__file__))  # where is this script?
shakedir = os.path.abspath(os.path.join(homedir, '..'))
sys.path.insert(0, shakedir)


def test_charlevoix_0(tmpdir):
    # make a temporary directory; read in rupture file
    p = os.path.join(str(tmpdir), "sub")
    if not os.path.exists(p):
        os.makedirs(p)
    old_shakedir = set_shakehome(p)
    v = os.path.join(shakedir, 'tests/data/CharlevoixVs30.grd')
    old_vs30file = set_vs30file(v)
    old_gmpe = set_gmpe('stable_continental_nshmp2014_rlme')
    jsonfile = os.path.join(
        shakedir, 'rupture_sets/BSSC2014/bssc2014_ceus.json')

    # directory holding test and target data for this event
    testinput = os.path.join(p, 'data/charlevoix_0_m7p_se/input')
    targetinput = os.path.join(
        shakedir, 'tests/output/charlevoix_0_m7p_se/input')

    #---------------------------------------------------------------------------
    # First test mkinputdir
    #---------------------------------------------------------------------------

    # Run mkinputdir
    cmd = 'mkinputdir -f %s -i 0 ' % jsonfile
    rc, so, se = get_command_output(cmd)
    if se != b'':
        print(so.decode())
        print(se.decode())

    # Check output files

    # Note: Not checking event.xml because the timestamp breaks cmp comparison.
    #       Would need to parse and to tag comaprisons. Not worth it.

    target = os.path.join(targetinput, 'charlevoix_0_m7p_se_for-map_fault.txt')
    test = os.path.join(testinput, 'charlevoix_0_m7p_se_for-map_fault.txt')
    assert filecmp.cmp(test, target) is True

    #---------------------------------------------------------------------------
    # Test mkscenariogrids
    #---------------------------------------------------------------------------
    datadir = os.path.join(p, 'data')
    cmd = 'mkscenariogrids -e charlevoix_0_m7p_se -r 0.1 '
    rc, so, se = get_command_output(cmd)

    # Check output files
    target = os.path.join(targetinput, 'mi_estimates.grd')
    test = os.path.join(testinput, 'mi_estimates.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'mi_sd.grd')
    test = os.path.join(testinput, 'mi_sd.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'pga_estimates.grd')
    test = os.path.join(testinput, 'pga_estimates.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'pga_sd.grd')
    test = os.path.join(testinput, 'pga_sd.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'pgv_estimates.grd')
    test = os.path.join(testinput, 'pgv_estimates.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'pgv_sd.grd')
    test = os.path.join(testinput, 'pgv_sd.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'psa03_estimates.grd')
    test = os.path.join(testinput, 'psa03_estimates.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'psa03_sd.grd')
    test = os.path.join(testinput, 'psa03_sd.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'psa10_estimates.grd')
    test = os.path.join(testinput, 'psa10_estimates.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'psa10_sd.grd')
    test = os.path.join(testinput, 'psa10_sd.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'psa30_estimates.grd')
    test = os.path.join(testinput, 'psa30_estimates.grd')
    grdcmp(test, target)

    target = os.path.join(targetinput, 'psa30_sd.grd')
    test = os.path.join(testinput, 'psa30_sd.grd')
    grdcmp(test, target)

    # Clean up
    set_shakehome(old_shakedir)
    set_vs30file(old_vs30file)
    set_gmpe(old_gmpe)
    shutil.rmtree(p)


if __name__ == "__main__":
    td1 = tempfile.TemporaryDirectory()
    test_charlevoix_0(td1.name)

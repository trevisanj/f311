import f311.physics as ph
import a99
import os
import f311.filetypes as ft


def test_adds_to_one0(tmpdir):
    os.chdir(str(tmpdir))
    db = ft.FileMolDB()
    db.init_default()

    consts = ft.MolConsts()
    consts.populate_all_using_str(db, "OH [A 2 sigma - X 2 pi]")
    consts.None_to_zero()


    mtools = ph.multiplicity_toolbox(consts)

    for J2l in range(30):
        try:
            mtools = ph.multiplicity_toolbox(consts)

            k = 2./ ((2*consts["s"]+1) * (2*J2l+1) * (2-consts["cro"]))

            mtools[(0, 0, J2l, "P1")]  # to induce populating for J2l
            sum_ = sum([x*k for x in mtools.values()])

            print("J2l={:2}: sum={}".format(J2l, sum_))
        except ZeroDivisionError:
            print("Failed for J2l={}".format(J2l))


test_adds_to_one0("/tmp")
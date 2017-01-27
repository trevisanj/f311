import os
import f311.filetypes as ft


def test_FileAbXFwhm(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileAbXFwhm()
    obj.init_default()
    obj.save_as()


def test_FileAbonds(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileAbonds()
    obj.init_default()
    obj.save_as()


def test_FileDissoc(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileDissoc()
    obj.init_default()
    obj.save_as()


def test_FileHitranDB(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileHitranDB()
    obj.init_default()
    obj.save_as("another")


def test_FileHmap(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileHmap()
    obj.init_default()
    obj.save_as()


def test_FileMain(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileMain()
    obj.init_default()
    obj.save_as()


def test_FileMolDB(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileMolDB()
    obj.init_default()
    obj.save_as("another")


def test_FileOptions(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileOptions()
    obj.init_default()
    obj.save_as()


def test_FileSparseCube(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileSparseCube()
    obj.init_default()
    obj.save_as()


def test_FileSpectrumList(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileSpectrumList()
    obj.init_default()
    obj.save_as()



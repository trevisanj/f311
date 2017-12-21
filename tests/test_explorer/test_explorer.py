import a99
import f311.explorer as ex

def test_create_window():
    app = a99.get_QApplication()
    form = ex.XExplorer(_flag_set_dir=False)
"""Lists different subsets of DataFile subclasses"""
import f311

titles = ("text", "binary", "1D spectrum")
allclasses = (f311.classes_txt(), f311.classes_bin(), f311.classes_sp())

for title, classes in zip(titles, allclasses):
    print("\n*** Classes that can handle {} files***".format(title))
    for cls in classes:
        print("{:25}: {}".format(cls.__name__, cls.__doc__.strip().split("\n")[0]))

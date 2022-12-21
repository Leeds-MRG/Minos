# -*- coding: utf-8 -*-
# """ HR 13/12/22 To modify vivarium/framework/randomness.py in Windows environment """
import os
from distutils.sysconfig import get_python_lib


def run():
    """
    HR 13/12/22
    To replace line in Vivarium script to allow key errors;
    this emulates command "@sed -i 's/except (IndexError, TypeError)/except ..." etc.
    in makefile -> make install
    """
    sitepackages = get_python_lib()
    print(sitepackages)
    vivarium_file_full = os.path.join(sitepackages, r"vivarium\framework\randomness.py")
    print(vivarium_file_full)

    replacements = {"(IndexError, TypeError)": "(IndexError, TypeError, KeyError)"}

    lines = []
    found = False
    with open(vivarium_file_full) as infile:
        for line in infile:
            for src, target in replacements.items():
                if src in line:
                    found = True
                    line = line.replace(src, target)
            lines.append(line)

    if found:
        print('Saving modified Vivarium script')
        with open(vivarium_file_full, 'w') as outfile:
            for line in lines:
                outfile.write(line)
    else:
        print('No changes made to Vivarium script')


if __name__ == "__main__":
    run()

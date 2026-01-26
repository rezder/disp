import os
from os.path import join
import subprocess as sub


def getTestFiles(dirName: str) -> [str]:
    testsfiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        if dirpath.find(".git") == -1 and dirpath.find(".venv") == -1:
            for f in filenames:
                if f.endswith(".py") and f.startswith("test"):
                    testsfiles.append(join(os.path.abspath(dirpath), f))
    return testsfiles


def runTest(fileName) -> tuple[str, bool]:
    isOk = True
    txt = "############# {} ##############:\n".format(fileName)
    args = ["python", fileName, "-t"]
    cp = sub.run(args, text=True, capture_output=True)
    txt = txt + cp.stdout
    if len(cp.stderr):
        txt = txt + "\n From stdErr: " + cp.stderr

    if cp.returncode != 0:
        isOk = False
    return txt, isOk

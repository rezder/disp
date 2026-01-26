
import runtests as rt


def main():
    files = rt.getTestFiles("..")
    print("Numbers of files: {}".format(len(files)))
    errTxt = ""
    for f in files:
        print("Testing: {} ".format(f), end="")
        txt, isOk = rt.runTest(f)
        if not isOk:
            print(" crashed.")
        elif txt.find("Error") != -1:
            eno = txt.find("Error")
            pathNo = txt.find("navigation.courseRhumbline.crossTrackError")
            if eno-pathNo != 37:
                print("contain error")
            else:
                print()
        else:
            print()

        errTxt = errTxt + "\n" + txt

    fileName = "./data/testtxt.txt"
    with open(fileName, "r") as f:
        oldErrTxt = f.read()
    if len(errTxt) != len(oldErrTxt):
        print("Test output changed from {} to {}".format(len(oldErrTxt),
                                                         (len(errTxt))))
        print("save errtxt in {}".format(fileName+".new"))
        with open(fileName+".new", "w") as f:
            f.write(errTxt)


if __name__ == "__main__":
    main()

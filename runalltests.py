
import runtests as rt


def main(txtLen):
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
    if len(errTxt) != txtLen:
        print("Test output changed from {} to {}".format(txtLen,
                                                         (len(errTxt))))
        # print(errTxt)


if __name__ == "__main__":
    main(9255)

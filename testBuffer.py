from skdata import Buffer


def main():

    b = Buffer(3, 3)
    isUpdate, value = b.add(1.5, 1)
    print(1.5)
    print(b)
    if isUpdate:
        print("expexted false")
    isUpdate, value = b.add(None, 1)
    print(None)
    print(b)
    if isUpdate:
        print("expexted false")
    isUpdate, value = b.add(2.5, 1)
    print(2.5)
    print(b)
    if not isUpdate:
        print("expexted true")
    else:
        if value != 2:
            print("expect 2 got {}".format(value))
    if b.fregIx != 0 or b.ix != 0 or b.sum != 4 or b.no != 2:
        print("Failed add")

    isUpdate, value = b.add(3, 1)
    print(3)
    print(b)
    isUpdate, value = b.add(4, 1)
    print(4)
    print(b)
    isUpdate, value = b.add(5, 1)
    print(5)
    print(b)
    if not isUpdate:
        print("expexted true")
    else:
        if value != 4:
            print("expect 4 got {}".format(value))
    if b.fregIx != 0 or b.ix != 0 or b.sum != 12 or b.no != 3:
        print("Failed add")
        print(b)


if __name__ == "__main__":
    main()

original = open("CLDI_LAC_bib_file_fixed.mrc", "rb")
uploaded = open("lastoutput.mrc", "r")


for line in original:
    print(line[:11912].decode("latin1"))


print("--"*50)


for line in uploaded:
    print(line[:11912])
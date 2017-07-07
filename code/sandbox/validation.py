import pymarc
from pymarc import MARCReader
f = MARCReader(open("files/validation_testing.mrc", "rb"), force_utf8=True)
count = 1

try:
	for record in f:
		print(record)

except ValueError:
	print("Aborted - Error in record #" + str(1) + " - Check record length and encoding")


# getNext = False

# for line in f:
# 	for char in line:
# 		if getNext:
# 			print(chr(char), char)		# all the different x for format $x
# 			# do validation for the identifier after $ here



# 			getNext = False
# 		elif char == 31:
# 			getNext = True

# 		#print(chr(char), char)





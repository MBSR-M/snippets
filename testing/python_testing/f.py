number = "1738184538173810023596032"

# Extract first 10 digits
part1 = number[:10]

# Extract next 10 digits
part2 = number[10:20]

# Extract the remaining digits
part3 = number[20:]

# Resulting parts
result = [part1, part2, part3]

print(result)

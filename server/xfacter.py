def cleanSpaces(input):
    while input.find("%_%") != -1:
        print(input, input.find("%_%"))
        input = input[ : input.find("%_%")] + " " + input[input.find("%_%") + 3 : ]
    return input


print(cleanSpaces("test%_%test"))
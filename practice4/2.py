def even_numbers(n):
    for i in range(0, n + 1,2):
        yield i

n = int(input()) 

print(",".join(str(x) for x in even_numbers(n)))
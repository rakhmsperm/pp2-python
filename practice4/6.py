def jo(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

n = int(input()) 

print(",".join(str(x) for x in jo(n)))
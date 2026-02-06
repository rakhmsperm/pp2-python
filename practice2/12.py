n = int(input()) 
a = list(map(int, input().split())) 

for i in range (n):
    a[i] = a[i] * a[i]

print(*a)
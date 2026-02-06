n = int(input()) 
a = list(map(int, input().split())) 

mx = max(a)
mn = min(a)

for i in range(n):
    if a[i] == mx:
        a[i] = mn

print(*a)
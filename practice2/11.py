n, l, r = map(int, input().split()) 
a = list(map(int,input().split())) 

l -= 1 
r -= 1 

a[l:r+1] = reversed(a[l:r+1]) 

print(*a)
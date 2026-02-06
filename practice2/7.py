n = int(input()) 

numbers = list(map(int, input().split()))

mx = numbers[0] 
pos = 1

for i in range(1, n):
    if numbers[i] > mx:
        mx = numbers[i]
        pos = i + 1

print(pos)
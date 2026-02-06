n = int(input()) 
a = list(map(int, input().split())) 

freq = {} 

for x in a:
    freq[x] = freq.get(x, 0) + 1

max_count = max(freq.values())
answer = min(x for x in freq if freq[x] == max_count)

print(answer)
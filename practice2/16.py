n = int(input()) 
a = list(map(int, input().split())) 

seen = set() 

for x in a:
    if x not in seen:
        print("YES") 
        seen.add(x) 
    else:
        print("NO")
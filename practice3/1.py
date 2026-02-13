n = input().strip() 

if all(int(d) % 2 == 0 for d in n):
    print("Valid") 
else:
    print("Not valid")
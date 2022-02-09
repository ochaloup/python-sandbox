
with open("/tmp/c") as file:
    lines = [line.strip() for line in file]

prior = None
for line in lines:
    thisline = int(line)
    if prior != None:
        print(f'{thisline} - {thisline-prior}')
    prior = thisline


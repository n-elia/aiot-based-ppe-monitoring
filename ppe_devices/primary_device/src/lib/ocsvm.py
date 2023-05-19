from lib.svm import score 

def predict(input):
    #print(input)
    ch, avg_h, vh, dh, cs, avg_s, vs, ds = input
    
    if avg_h == None:
        avg_h = 0
    if avg_s == None:
        avg_s = 0
    
    if vh == None:
        vh = 100000
    if vs == None:
        vs = 100000
        
    if dh == None:
        dh = 100000
    if ds == None:
        ds = 100000
        
    i = [ ch, avg_h, vh, dh, cs, avg_s, vs, ds ]
    pred = score(i)
    if pred < 0: 
        return 1
    else :
        return 0
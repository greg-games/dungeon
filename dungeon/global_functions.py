import sys
def iscolliding(object1,object2,distance = 0):
    return (object1.right + distance > object2.left and 
            object1.left - distance < object2.right and 
            object1.top - distance < object2.bottom and 
            object1.bottom + distance > object2.top)

def is_in_browser():
    return sys.platform == "emscripten"
    #return True #for debug purposes
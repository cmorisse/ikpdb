import time

def processing():
    a_var = 1
    b_var = "a_string"
    print("Line 3")
    a_var = 50
    print("line 6")
    print("line 7")



if __name__ == '__main__':
    # we must wait a litle to bit to ensure we will receive runScript 
    # confirmation before programBreak. This is required since
    # ikpdb_client (debugging) is synchronous.
    time.sleep(0.2) 
    processing()
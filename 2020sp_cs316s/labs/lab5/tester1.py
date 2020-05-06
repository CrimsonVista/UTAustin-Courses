import os

score = 0
max_score = 0

def test_assert(condition, msg):
    global score, max_score
    if condition:
        score += 1
        print(msg,": PASSED")
    else:
        print(msg,": FAILED")
    max_score += 1

def cmp_dir(dir1, dir2):
    test_assert(
        (dir1 == dir2) or (dir1+"/" == dir2) or (dir1 == dir2+"/"),
        "Compared {} to {}".format(dir1, dir2)
    )

def test_chdir():

    cmp_dir("/tmp", os.getcwd())
    os.chdir("..")
    cmp_dir("/", os.getcwd())
    try:
        os.chdir("..")
    except:
        pass
    cmp_dir("/", os.getcwd())
    os.chdir("/tmp/test")
    cmp_dir("/tmp/test", os.getcwd())
    bad_dir_failed = False
    try:
        os.chdir("/tmp/tester1.py")
    except:
        bad_dir_failed = True
    test_assert(bad_dir_failed, "Chdir to /tmp/tester1.py")
    os.chdir("/tmp/..")
    cmp_dir("/", os.getcwd())
    os.chdir("/bin")
    cmp_dir("/bin", os.getcwd())
    bad_dir_failed = False
    try:
        os.chdir("/bad")
    except:
        bad_dir_failed = True
    test_assert(bad_dir_failed, "Chdir to /bad")
    os.chdir("../tmp")
    cmp_dir("/tmp", os.getcwd())

def test_open():

    f = open("/tmp/file_tmp1.txt","wb+")
    f.write(b"This is a test\n")
    f.close()
    f = open("/tmp/file_tmp1.txt", "rb")
    test_assert(f.read() == b"This is a test\n", "file 1 test")
    f.close()
    f = open("/tmp/file_tmp2.txt","wb+")
    f.write(b"A"*4096)
    f.write(b"B"*1024)
    f.close()
    f = open("/tmp/file_tmp2.txt","rb")
    test2_data = f.read()
    test_assert(test2_data[:4096] == b"A"*4096, "file 2 test pt 1")
    test_assert(test2_data[4096:] == b"B"*1024, "file 2 test pt 2")
    f.close()

def test_tcp():

    fd = os.open("tcp://example.com:80",0)
    os.write(fd,b"GET / HTTP/1.1\r\nHOST: example.com\r\n\r\n")
    response = os.read(fd, 4096)
    test_assert(b"example domain" in response.lower(), "Connect to origin example.com")
    os.close(fd)
    non_origin_failed = False
    try:
        os.open("tcp://google.com:80",0)
    except Exception as e:
        print("Failed", e)
        non_origin_failed = True
    test_assert(non_origin_failed, "connect to non orgin google.com")

try:
    test_chdir()
except Exception as e:
    print("Chdir Test failed", e)
try:
    test_open()
except Exception as e:
    raise e
    print("Open Test failed", e)
try:
    test_tcp()
except Exception as e:
    print("TCP Test failed", e)
print("Score: {}/{}".format(score, max_score))

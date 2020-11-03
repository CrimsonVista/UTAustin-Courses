import time, sys
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

import gmpy2
from collections import namedtuple

Interval = namedtuple('Interval', ['a','b']) 

#### DANGER ####
# The following RSA encryption and decryption is 
# completely unsafe and terribly broken. DO NOT USE
# for anything other than the practice exercise
################  
def simple_rsa_encrypt(m, publickey):
    numbers = publickey.public_numbers()
    return gmpy2.powmod(m, numbers.e, numbers.n)

def simple_rsa_decrypt(c, privatekey):
    numbers = privatekey.private_numbers()
    return gmpy2.powmod(c, numbers.d, numbers.public_numbers.n)
#### DANGER ####
    
# RSA Oracle Attack Component 
def int_to_bytes(i, min_size=None):
    # i might be a gmpy2 big integer; convert back to a Python int
    i = int(i)
    b = i.to_bytes((i.bit_length()+7)//8, byteorder='big')
    if min_size != None and len(b) < min_size:
        b = b'\x00'*(min_size-len(b)) + b
    return b
    
def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')
    
class RSAStat:
    def __init__(self):
        self.i = 0
        self.runtime = 0.0
        self.search_count = 0

# RSA Oracle Attack Component        
class FakeOracle:
    def __init__(self, private_key):
        self.private_key = private_key
        
    def __call__(self, cipher_text):
        recovered_as_int = simple_rsa_decrypt(cipher_text, self.private_key)
        recovered = int_to_bytes(recovered_as_int, self.private_key.key_size//8)
        return recovered[0:2] == bytes([0, 2])

class RSAOracleAttacker:
    def __init__(self, public_key, oracle):
        # NOTE oracle is a callable of the following type:
        #  oracle(big_int)->boolean
        # the "big_int" is the ciphertext as a number. The
        # boolean is whether or not it is "legitimate" cipher
        # text (e.g., decrypts to something with proper padding).
        
        self.public_key = public_key
        self.oracle = oracle
        self.stats = []
    
    def _step1_blinding(self, c):
        # step1, the blinding step 
        #   i is 1
        #   s is [1]
        #    n is the public key's "n" parameter
        #    c0 is just c (Read the part in the paper about skipping
        #       the blinding step and setting s0 to 1)
        # you need to computer B and M
        # B is defined on page 4 of the paper as B = 2**(8*(k-2))
        #   but that's confusing. "k" is the key size in bytes and
        #   the multiplication by 8 is to convert to bits. You already
        #   have the key size in bits (self.public_key.key_size). You
        #   can get rid of the x8 (but make sure to distribute through)
        #  M is a set of a set of intervals. Yes, a set of sets. So
        #    M is a list ([]) that contains lists of Intervals (e.g., 
        #    [Interval1, Interval2,...]. The initial M value has a single
        #    list with a single Interval. That Interval is between 2B and
        #    3B-1. Please use the "Interval" class above (e.g., Interval(a,b))
        self.i = 1
        self.s = [1]
        self.n = self.public_key.public_numbers().n
        self.c0 = c
        
        self.B = 0
        s.M = []
        
    def _find_s(self, start_s, s_max=None):
        self.stats[-1].search_count += 1
        
        # In each of the "search" parts of step 2 (2a, 2b, etc),
        # you are supposed to search for the smallest s that
        # satisfies the oracle. Remember, from the perspective
        # of RSA, plaintexts and ciphertext are just numbers. You
        # input a number (plaintext) and it gives you another
        # number (ciphertext). We can convert these (very large)
        # numbers to bytes when necessary, but for now, we will
        # just work with (very large) numbers. So, start with
        # start_s and encrypt it. Next, you're going to **MULTIPLY**
        # the cipher text (number) by self.c0 ** MOD self.n **. You
        # check if that value is a legitimate ciphertext by
        # passing it to the oracle.
        # 
        # Why do you multiply c0 by ci? c0 is the initial ciphertext
        # and ci is just some random number (between start_s and s_max)
        # that is also encrypted. What is the connection? The
        # answer is that RSA is homomorphic with respect to multiplication
        # so when we multiply ci X c0, we end up with the RSA encryption
        # of si x p0 where p0 is the plaintext of c0. Why do we want
        # that? Well, I can't even explain it super well, but basically
        # it has to do with finding constraints that lead us closer
        # and closer to the plaintext. Don't worry about it for now.
        # just trust me that you need to search for an si between
        # start_s and s_max that, when encrypted to ci, results in
        # the oracle returning true for oracle(c0 x ci MOD n).
        
        # if s_max is none, there is no upper bound. Don't worry, 
        # it won't run forever (if you've done it right!)

        si = start_s
        ci = simple_rsa_encrypt(si, self.public_key)
        while not self.oracle((self.c0 * ci) % self.n):
            si += 1
            if s_max and (si > s_max):
                return None
            ci = simple_rsa_encrypt(si, self.public_key)
        return si

    def _step2a_start_the_searching(self):
        # this function should return a found s where s starts
        # at n/3B. Because these are big numbers, you should use
        # gmpy2.c_div to divide n and 3B.
        # return the si found.
        si = None
        return si


    def _step2b_searching_with_more_than_one_interval(self):
        # this function searches for a found s where s starts
        # at the most recent s plus one
        si = None
        return si


    def _step2c_searching_with_one_interval_left(self):
        ## this is the hardest one.
        # You need to get the most recent interval set from M,
        # and then get the first interval of that set. Unpack
        # the interval tuple to variables a, b
        
        # Next, compute ri = (2(b x s[-1] - 2B))/self.n
        #    (use gmpy2.c_div for these computations)
        # 
        # Finally, search for an s between (2B+(ri x n))/b
        #   and (3B+(ri x n))/a
        # 
        # If no si is found, increase ri by one and try again.
        si = None
        return si

    def _step3_narrowing_set_of_solutions(self, si):
        # This step reduces the number of possible solutions
        # It will start by iterating through all the Intervals in the
        #  most recent M. As you iterate through each Interval, unpack
        #  the Interval to variables a, b
        # 
        # For each interval a,b
        #    r_min is ((a x si) - 3B+1)/n (use gmpy2.c_div)
        #    r_max is ((b x si) - 2B)/n (use **gmpy2.f_div**)
        #    For r in range (r_min, r_max):
        #        new_a = (2B + (r x n))/ si (use gmpy2.c_div)
        #        new_b = ((3B-1) + (r x n))/si (use **gmpy2.f_div**)
        #        new_interval = Interval( max(a, new_a), min(b, new_b))
        #        add interval to a set of intervals
        
        # append the new intervals to M (the new last element of M will
        #   be the list of intervals discovered)
        # append si to self.s
        
        # IF the length of new intervals is 1 AND this single Interval's
        # a == b, return True, otherwise False
        
        # For explanations on why to use c_div vs f_div, look up these
        # functions in gmpy2 and then see if you can figure out why one is
        # used over the other
        return False

    def _step4_computing_the_solution(self):
        # I just included this step to follow the paper. But we
        # already have the solution.
        interval = self.M[-1][0]
        return interval.a

    def attack(self, c):
        self.stats.append(RSAStat())
        t0 = time.time()
        self._step1_blinding(c)
        
        # do this until there is one interval left
        finished = False
        while not finished:
            if self.i == 1:
                si = self._step2a_start_the_searching()
            elif len(self.M[-1]) > 1:
                si = self._step2b_searching_with_more_than_one_interval()
            elif len(self.M[-1]) == 1:
                interval = self.M[-1][0]
                si = self._step2c_searching_with_one_interval_left()

            print("Found! i={} si={}".format(self.i, si))
            finished = self._step3_narrowing_set_of_solutions(si)
            self.i += 1

        print("Found solution")
        m = self._step4_computing_the_solution()
        
        tn = time.time()
        self.stats[-1].i = self.i
        self.stats[-1].runtime = tn - t0
        return m
            
def main(args):
    key_size, messagecount = [int(arg) for arg in args]
    print("Running {} tests with key size {}".format(messagecount, key_size))
    
    private_key = rsa.generate_private_key(
              public_exponent=65537,
              key_size=key_size,
              backend=default_backend()
          )
    public_key = private_key.public_key()
    
    oracle = FakeOracle(private_key)
    attack_program = RSAOracleAttacker(public_key, oracle)
    
    for i in range(messagecount):
        message = b'test %d' % (i)
    
        ###
        # WARNING: PKCS #1 v1.5 is obsolete and has vulnerabilities
        # DO NOT USE EXCEPT WITH LEGACY PROTOCOLS
        ciphertext = public_key.encrypt(
            message,
            padding.PKCS1v15()
        )
        ciphertext_as_int = bytes_to_int(ciphertext)
    
        print("\nWe're starting our attack run on message {}.".format(i))
    
        recovered_as_int = attack_program.attack(ciphertext_as_int)
        if int_to_bytes(recovered_as_int).endswith(message):
            print("[PASS]")
        else:
            print(int_to_bytes(recovered_as_int))
            print("[FAIL]")
            return
        print("\tRecovered: ", int_to_bytes(recovered_as_int))
    
    i_total = 0
    search_total = 0
    runtime_total = 0.0
    print(     "\nSTATISTICS")
    print(     "-------------------------")
    print(     "{:6} {:10} {:10} {:10}".format(
        "Test", "Iterations", "Searches", "Runtime"))
    print(     "-------------------------")
    for test_index in range(messagecount):
        test_stat = attack_program.stats[test_index]
        print("{:4} {:10} {:10} {:10}".format(
            test_index, 
            test_stat.i, test_stat.search_count, test_stat.runtime))
        i_total += test_stat.i
        search_total += test_stat.search_count
        runtime_total += test_stat.runtime
    i_avg = i_total/messagecount
    search_avg = search_total/messagecount
    runtime_avg = runtime_total/messagecount
    print("\n")
    print(     "AVERAGE:")
    print(     "{:6} {:10} {:10} {}".format(
        "", i_avg, search_avg, runtime_avg))
    
    
if __name__=="__main__":
    main([512,1])
    sys.exit(0)
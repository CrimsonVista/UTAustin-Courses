#!/usr/bin/python3
import hashlib, time, hmac

"""
Dear Students.

This lab is designed to teach you a bit about password
cracking. It is written completely in python, but you will
need very little python knowledge to complete it. All of
the hard parts of the programming are written for you. All
you will need to do is add some parameters. Let me explain.

The basic algorithm is the same no matter how you do it. 
There are a couple of basic "runs" that are pre-configured.
Your job is to add a few lines here and there that have
it run on bigger data sets. Also, you should read the
output. That is really the interesting part, even though
I won't be grading you on it.

What you actually need to do with the code is very minimal.
Please search for STUDENT TODO:, of which there are three
or four near the very bottom.

Although those TODO's are the only requirements, you should
look through the code at the other comments. These comments
are largely written for you to see how this whole process
works.
"""


def password_cracker(hashes, algorithm, token_set, maxtokens, substitutions, callback):
    """
    This function will try to see if it can find "pre-images" for all
    of the provided hashes for a given algorithm. The parameter "hashes"
    is a dictionary of salt->set_of_hashes
    
    The generated passwords will be of size 1 through maxtokens (inclusive)
    and will be drawn from tokenset. This can be used to do all possible
    combinations of characters (by making token set a set of single characters)
    or a dictionary attack where the tokens are words.
    
    For dictionary attacks, substitutions is a function that, for any given
    input, will provide a set of possible substitutes (e.g., "password" ->
    "p@ssword"). It is useless for pure brute-force.
    
    Callback must be a function
      cb("START", args) called at the start of the function. Useful for
        time keeping.
        
      cb("SIZE", (n,m)) called each time a new password token size is started
        n is the size, m is the total number of individual passwords to attempt.
        The m value does NOT include subsitution count and is for "order of
        magntude"
        
      cb("PREIMG", preimg) called on each preimage tested
      
      cb("FOUND", (preimg, salt, image)) called each time a pre image is found
      
      cb("END", (n,m)) called when function ends with the number of solutions
        and the total number of hashes
      
    The cb can return "STOP" at any time to end the function
    """
    res = callback("START", [hashes, algorithm, token_set, maxtokens, substitutions, callback])
    if res == "STOP":
        return {}
    
    hashcount = 0
    if substitutions is None:
        substitutions = lambda x: [x]
    
    # We will store solutions in this dictionary
    solutions = {}
    
    # this will loop over all lengths between 0 and maxlen-1
    for i in range(maxtokens):
    
        # preimg_len is the length of the preimage in terms of tokens
        preimg_len = i + 1
        
        # token count is the number of tokens
        token_count = len(token_set)
        
        res = callback("SIZE", (preimg_len, token_count**preimg_len))
        if res == "STOP":
            return solutions
        
        # this will loop over all possible combinations of preimages of token size "i"
        # If token set is lowercase letters and size is 2, it will go "aa" thru "zz"
        for j in range(token_count**preimg_len):
            preimg_idxs = []
            
            # This loops converts j from a number into a specific set of tokens
            for k in range(preimg_len):
                rdigit = j%token_count
                preimg_idxs = [rdigit] + preimg_idxs
                j = int(j/token_count)
                
            # preimg is the actual text of the preimage being converted
            if type(token_set) == bytes:
                preimg = b"".join([token_set[ch_i:ch_i+1] for ch_i in preimg_idxs])
                preimg_variants = set([preimg])
            else:
            
                # This part of the code takes whole-words and plays with basic
                # capitalization rules before running it through the substitutions
                # engine.
                default_preimage  = b"".join([token_set[ch_i] for ch_i in preimg_idxs])
                preimg_variants_1 = set([])
                preimg_variants_1.add(default_preimage)
                preimg_variants_1.add(default_preimage.upper())
                preimg_variants_1.add(default_preimage.lower())
                preimg_variants_1.add(b"".join([token_set[ch_i].capitalize() for ch_i in preimg_idxs]))
                preimg_variants = []
                for basic_variant in preimg_variants_1:
                    preimg_variants += list(substitutions(basic_variant))
                preimg_variants = set(preimg_variants)
            
            # iterate over all variants of the preimage. If may just be one
            for preimg in preimg_variants:
            
                res = callback("PREIMG", preimg)
                if res == "STOP":
                    return solutions
                
                # hash the preimage to get the image (h)
                # each preimage must be tried with each salt
                for salt in hashes:
                    h = algorithm(preimg, salt)
                    hashcount += 1
                
                    # check if the hash exists in the set of hashes we're looking for
                    if h in hashes[salt]:
                        # if it matches, record it in the solutions
                        callback("FOUND", (preimg, salt, h))
                        solutions[(preimg, salt)] = h
                
    callback("END", (len(solutions), hashcount))
    return solutions 
    
def make_hash_function(algorithm):
    return lambda preimage, salt: algorithm(preimage+salt).digest()
    
def make_hmac_function(digest):
    return lambda password, message: hmac.HMAC(password, message, digest).digest()
    
def pbkdf2_fixsize(prf, iterations, password, salt):
    """
    This is the algorithm for pbkdf2, except we are fixing
    the length of the output to the length of the hmac for
    simplicity.
    """
    u = prf(password, salt+(1).to_bytes(4, "big"))
    for i in range(iterations-1):
        u = prf(password, u)
    return u

def make_pbkdf2_function(prf, iterations):
    return lambda password, salt: pbkdf2_fixsize(prf, iterations, password, salt)
    

class CrackerHelper:
    def __init__(self, timeout, debug_events=[]):
        self._timeout = timeout
        self._debug_events = debug_events
        self._reset()
        
    def _reset(self):
        self._start_time = None
        self._end_time   = None
        self._size_time  = None
        
    def runtime(self):
        if self._start_time is not None and self._end_time is not None:
            return self._end_time - self._start_time
        
    def __call__(self, event, args):
        if event == "START" or self._start_time == None:
            self._reset()
            self._start_time = time.time()
        if event == "END":
            if self._size_time is not None:
                print("Time since last size change {} seconds".format(time.time()-self._size_time))
            self._end_time = time.time()
        if event == "SIZE":
            if self._size_time is not None:
                print("Time since last size change {} seconds".format(time.time()-self._size_time))
            self._size_time = time.time()
            
            
        time_left = (self._start_time+self._timeout) - time.time()
        if time_left < 0.0:
            self._end_time = time.time()
            return "STOP"
        if event in self._debug_events:
            print(event, args)

translation_dict = {
    b'A': [b'@'],
    b'a': [b'@'],
    b's': [b'$', b'5'],
    b'S': [b'$', b'5'],
    b'i': [b'l'],
    b'I': [b'1', b'!'],
    b'T': [b'7'],
    b'E': [b'3'],
    b'o': [b'0'],
    b'O': [b'0'],
    b'B': [b'8'],
    b'l': [b'1'],
    }
        
def basic_translations(s):
    yield s
    
    # do each letter replacement
    for replaceable_letter in translation_dict:
        if replaceable_letter in s:
            for replacement_letter in translation_dict[replaceable_letter]:
                yield s.replace(replaceable_letter, replacement_letter)
    
    # do all letter replacements for all combinations
    s_rs = [s]
    for replaceable_letter in translation_dict:
        next_s = []
        for replacement_letter in translation_dict[replaceable_letter]:
            for s_r in s_rs:
                next_s.append(s_r.replace(replaceable_letter, replacement_letter))
        s_rs = next_s
    for s_r in s_rs:
        if s_r != s:
            yield s_r
        
    for i in range(10):
        yield s+str(i).encode()
        yield str(i).encode()+s
        

if __name__ == "__main__":
    
    """
    STUDENT TODO:
    A "callback" is a computer science term for a function that is
    "called back" from another function as that second function is running.
    It is useful for getting signals from a long-running function.
    
    This callback will help keep track of time and end the function if
    it runs for too long. It will also 
    print out stuff that is happening while the function is running.
    By default, it prints out when the function starts and ends,
    and when a solution is found.
    
    You can also configure it to print out EVERY SINGLE WORD that it
    tries. If you want to see this, add "PREIMG" (which stands for
    Pre-Image), into the list of debug_events below. This will make
    it run much slower, but will allow you to see it trying all
    possible combinations.
    
    The current timeout of one minutes (1 x 60 seconds), is maybe
    enough time on a fast computer to get through 4 letter combo's
    and 5 letter combo's. You can increase it to 10 minutes (10 x 60)
    or even an hour (1 x 60 x 60). See how many more passwords you
    can crack
    """
    callback = CrackerHelper(
        timeout=1*60,
        debug_events=["START", "SIZE", "FOUND", "END"]
    )
    
    
    """    
    These are the password hashes for each algorithm
    You do not need to do anything here.
    """
    md5_hashes = {b"":set([
b'\x91.\xc8\x03\xb2\xceI\xe4\xa5A\x06\x8dIZ\xb5p',
b'\x05\xee\x9fheq\xbf\x9dw\xdc\xba \xc4\x18\t\\',
b'\xd8W\x8e\xdf\x84X\xce\x06\xfb\xc5\xbbv\xa5\x8c\\\xa4',
b'\x82|\xcb\x0e\xea\x8aplL4\xa1h\x91\xf8N{',
b'%\xf9\xe7\x942;E8\x85\xf5\x18\x1f\x1bbM\x0b',
b"_M\xcc;Z\xa7e\xd6\x1d\x83'\xde\xb8\x82\xcf\x99",
b'\xdcd~\xb6^g\x11\xe1U7R\x18!+9d',
b'\xb2C\x07\x1d\x14\xcdD\n\xdb\xeeUumt}S',
b'\x15Am\x8f`fg\xeb\xe0^\xbeY\x08\xa1\xb1u',
b'\x02^\x08\xd4\xc2m\xb2\x97\xb5IZ\xd8\x1b\x13\xed}',
b'c\xdcO"\xb5\xc2\xb8wW\x82\xef\xc9\x0b\x13\xf3\xb2',
b'\x1a\x08\xd49\x9a\xa1\xcc\xa3\xc1\xe1F\x8fO\xd2\xf4\xf9',
b"^\x05\xdc\xb9Uy\xda\x18\xd4\x82'\xc8\x9d\xf6\x83\x99",
b'D\xbf\xddYS\x92\x97G\x1cw\xcavE\x80\x90q',
b'\xad,j\xa6\xc9\xc1\x00J\xd8\xe0y\x90\xcfk\x94\x16',
b'\xb5\x12A\xce#$\xbe\xea\xa2F\xc0\xd0\x9c\xdba\n',
b'\xa1\x88\xf5\xd8\xd6\x10 xH.-f\xe0\x9d?c',
])}

    sha1_hashes = {b"":set([
b"=\xa5AU\x99\x18\xa8\x08\xc2@+\xbaP\x12\xf6\xc6\x0b'f\x1c",
b'{\x0f1\xc3.\x1f\x80\x1d?\xd9\x13\xd9\x02\x87\x9fd|\x05\xf0\xd4',
b'\xb1\xb3w:\x05\xc0\xed\x01vxzO\x15t\xff\x00u\xf7R\x1e',
b'4\xbd0\xd5b\xd2V\xc9{\xc9_\x18"R\x9d\x0f\x9d\xc5&r',
b'\xc6\x05\xa0X\tx-=R\xe0\x10\xc4\xdf\xb4F\xb9\xaf\xe1\x18\xad',
b'\xeb\xf8\xd8\xb7\xa7\x8d\xd8\x9f\x84>\x80\xd0{\x98R\xce\xa0l\xa2l',
b'\xd9\x10\x10\x89\x88?\xe3\x93\x84\xab\xbb\x98q\xbe\x983\xf9 !\xc0',
b'\xe3\x90\xdf}\x1eU<\xa5\xd2\xe1]N\xc9r\xe3\x11D\x03\xc8q',
b'\xd03\xe2*\xe3H\xae\xb5f\x0f\xc2\x14\n\xec5\x85\x0cM\xa9\x97',
b'$\x9b\xa3`\x00\x02\x9b\xbe\x97I\x9c\x03\xdbZ\x90\x01\xf6\xb74\xec',
b'\x83\xfd\xd0\xf7\xfd\x1c\x05s\xb39YZBjf#\t\xfa\x88\x19',
b"\x85\xea/\x9b,<\xd5\xae\xadZ\x9f\xf0\xc6'Kj\xbe4\xe8/",
])}

    sha256_hashes = {b"":set([
b'\xf0\xe4\xc2\xf7lX\x91n\xc2X\xf2F\x85\x1b\xea\t\x1d\x14\xd4$z/\xc3\xe1\x86\x94F\x1b\x18\x16\xe1;',
b'\x19\xe3g=(i\x13\xabv\xceq\xe4\x7f\xd6\xf0*\x82w\xcc\xae\x93\x00\x14j&\x8cDT\n;_\xf1',
b'e\xe8K\xe352\xfbxLH\x12\x96u\xf9\xef\xf3\xa6\x82\xb2qh\xc0\xeatK,\xf5\x8e\xe0#7\xc5',
b'\x08\xea\xc0;\x80\xad\xc3=\xc7\xd8\xfb\xe4K|{\x05\xd3\xa2\xc5\x11\x16k\xdbC\xfc\xb7\x10\xb0;\xa9\x19\xe7',
b'\xeb\xf6\xea\t\xe1w\xabn\x87\xe0\xb9o$@o\x84F\xcdj\x81\xbc\xbb8\x0c,$\xfb\x99Q6U\x01',
b'\xa4\xc4D\xbdV\x15\xcc\xa80[&\x83\xe5\xc8\xb3\xdf\xc9\x86p\x17i\xa3\xd4\x81g\x92%\xae\x84\xd7\x01\x14',
b'\xeeg\x80\x89s\x96O\xed_\x14\x1b\x90uN\x98C\xc7\x8aT\xf8JE*\x05gw\xaa\xde\x8b\x1b\xadb',
b'\x97[\xfc$\xfa\xa0\x99X\x00\x04\x9a2XVA\x94\x19A\x95\xc3\x80e\xd6\xfc\xa9\x13\x921\x92\xeb\x98\xcc',
b'\x15@\x8b\x13\x95Lvg\xeb\xf0\xc6\x1d\xd0\xaf\x84\x10\x17\xb1W\xb8\xac\x87Ta\xac\x1f\xc3w\x92~\xc5K',
b'\x0b\x01\xd1&\xc9\xe4\xfcU\xa7\xaco\xb7\n[?\xf7\xa4<A\x80\xcc\xc1g|\xc3\xfcL&\xc9\xa2;H',
b'V\x9d\xbd{)N\x1e\xd6|\xb8P\xd5\x14\xd7\xe8\xf1~\x85\xd2\xc2]),\x96\xd1\xdf\\\xbe\x12\x0f[\x15',
b'\xca/ i\xea\x0cnFX".\x06\xf8\xddc\x96Y\xcb\xb5\xe6|\xbb\xbag4\xbc3J7\x99\xbch',
b'\xcf\xc2\xd4st\xc4\xbe\\\xc5<\x8dN\x1aW\x11K^4\x11\x93\x07\x8fn\x98\\\x8bI\x1c\x93\x0f\x05\x86',
b't\xcc8\x1bY)\xbbZ:\xc8D\xfbd\xbd\xc8\x8f\x9b\xe0|\x1a\xfa\xa6$\x8aa\x07$\xe356,V',
])}

    pbkdf2_hashes = {b'z$X\xe1;\xec\x9b\x83\xfe}\xff\xcb$\x9f9\x19': set([b'\n\x14\xe1J\x0e\xa5r\x7fS8\xf1\xdc\xacLg\xa3\x90w\x1d\x94']),
b'\xd9|\xdc\x17\xae\xb3\x80\xaf\xdf\xdfp?\x9fzK"': set([b'~\x8b\xf0|\xa2\xb8\x8e\xce{\xa1\x1d3\xa6C\x81\x0b%\x96\xe5\xe9']),
b"V\xcf\x85\xb2'\x86y\xfcD\xd80\x8fC9\xae\x96": set([b'\xfc\x9d"\xbd\x86\xfc\x89\xd4R\xfbO"&\x86\xd6$B9\'\x1a']),
b'\xe6\xfa\xbd19\xc9on\xeb\xba\xc4i\xc9\x0cl\xdd': set([b'\x88\xf6\xb9\x8f\x9e\xb15\xe6t\xb3\n\x06\t\x91\xf9\x8dS\xf1\x8c\x8d']),
b'\xf7\x94U\x94x\xe3\xa1\xe9\xdbqV\x7fv\xfb\x0c$': set([b'>\xfauF\x16\x97DPh\xe1\xad\x94\xb6\x1eQ~\xd5\xdd{\t']),
b'g\xd0\xcbm\xbf\xaeH\xd7<&jZ\x02j\xa7\xe6': set([b'\x80\xb4\x00\x83\xcc5y\xa3\x8b\x14\xc0\xd4\x95C\xa0\xc6u\xd19\xc6']),
b'\x1d~E\x19\xf0\xaf\n\xbaqf\r\x0e|\xe3\xdf\x8c': set([b'\xc3BB]\x9e+\x92\x8aG\x10\x17\xfd\xd97D\xaf\x05L\xa6\x12']),
b'\xac\xf5\x01\x0b\x1a7;\x99\xad\xba\x07\xdc\x9c\xa9V\xe9': set([b"\xc2,\x0cb\xf4?\xfc\x89\x06\xc0\xd0\xbf\x87\x10'\xacxzg\x01"]),
b'p\xf0\xa6\xa8\xc0\x85_\x88\xe2\xff\xe3Q\xc4E\x94\xeb': set([b'\xdeB\x18\xdb,3\xb8Qbs\xec\x95^6\xe1\xa3D\xfa\x87\xa2']),
b'^\xb9!\xe9T\x12\xa33\x13/\x08\x1f\t\x12Js': set([b'\x8d\xf8\xa3\x1b\x82\xac\xf4W\x98\xfa\xd0\xbc\x9b\xb8\x0f\xfa\xfd\xb5\xf4\x03']),
b'\xb6[\xc8\x8cQ\x12\x94\xd3\x861\xc9t\x95\x12\x0b\x11': set([b'\x1d\xfc.\x07\xb8\xfa\xb3\xb5\xe1E\xc6\xbe\xdc\x94\x9e\xddp"nx']),
}
    
    """
    STUDENT TODO:
    
    In the code below, there are two calls to "password_cracker". One passes in
    lower-case letters and will try all possible combinations of lower case
    letters up to 8 long. Note that this is using Md5 hashing function, which
    is very fast. 
    
    Even still, your computer almost certainly won't be able to complete the
    run before the 10 minute timeout. You could extend the timeout, but are
    you planning to leave your computer running for days?
    
    The second password cracker uses a dictionary and tries all possible two-word
    dictionary combinations, including with substitutions. The starting dictionary
    only has two words. Your job is to download some lists of words, add
    them to the dictionary file (dictionary.txt) and re-run. The goal is to
    see how many passwords you can break. This obviously requires no programming
    at all. Just drop words into the dictionary separated one line at a time.
    
    You will also need to re-run password cracker for sha1, sha256, and pbkdf2
    hashes. This does require a little programming, but very little. Repeat
    the "password_cracker" call you see below but update each of the arguments.
    
      change hashes to one of sha1_hashes, sha256_hashes, or pbkdf2_hashes.
      
      change algorithm to one of sha1_hash_function, sha256_hash_function, or
      pbkdf2_function.
      
    Everything else should stay the same. You can repeat the two lines that
    follow the password cracker for printing out the passwords that were
    found.
    
    Note that everything only gets
    slower from here. So trying every possible combination of letters won't
    be feasible. Instead, keep working on your dictionary. 
    
    Note that some passwords are repeated from one list to another. So any
    passwords you find in one set of hashes should be added to your dictionary.
    """
    
    md5_hash_function = make_hash_function(hashlib.md5)
    sha1_hash_function = make_hash_function(hashlib.sha1)
    sha256_hash_function = make_hash_function(hashlib.sha256)
    
    pbkdf2_function = make_pbkdf2_function(make_hmac_function("sha1"), 100000)
    
    with open("dictionary.txt", "rb") as f:
        dictionary_words = [word.strip() for word in f.readlines() if word.strip()]
    
    solutions = password_cracker(
        hashes=md5_hashes, 
        algorithm=md5_hash_function, 
        token_set=b"ABCDEFGHIJKLMNOP", 
        maxtokens=8, 
        substitutions=None,
        callback=callback)
    for preimage, salt in solutions:
        print("Found password: {}".format(preimage))
    
    solutions = password_cracker(
        hashes=md5_hashes, 
        algorithm=md5_hash_function, 
        token_set= dictionary_words, 
        maxtokens=2, 
        substitutions=basic_translations,
        callback=callback)
    for preimage, salt in solutions:
        print("Found password: {}".format(preimage))
        
    """
    STUDENT TODO:
    You can also experiment with different password character sets. In the
    example above, there are only letters and only lowercase letters. 
    Try adding in upper case letters (you can manually type in each letter).
    How much longer does it take to try all 5-character words? How many
    more total possible words are there? What if you add in numbers and
    special characters?
    
    Now, some of the passwords in the hashes are just numbers. So you ought
    to try a token_set of just the digits. Because there are only ten of them,
    you can try for a sligtly larger maxtokens. How high can you get within
    the timelimit?
    """
    
    
    """
    STUDENT TODO:
    What to turn in. All that needs to be turned in is your password file.
    Please put any passwords you discovered/broke (even through brute force)
    at the very top.
    
    You are not scored on how many you get right. As a reminder, you are scored
    pass/fail. I recommend that you submit early. If I think you may have
    missed some concepts, I'll reach out to see if I can help.
    
    Password files can be submitted by email. You may also include, if you wish
    observations you made on how long it took to run things, how many combinations
    you were able to try and so forth.
    """

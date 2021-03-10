from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from newslister.models import NewsListing
from newslister.models import UserXtraAuth
from newslister.views import NewsApiManager, user_account, index
from newsapp.urls import TokenLoginForm
from django.core.exceptions import ValidationError
import fake_token
import sys, os, base64, subprocess, random, sqlite3, string, time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC 
from cryptography.hazmat.backends import default_backend
backend = default_backend()
    
#sys.stderr = open('result.txt','w')
#print('If a testing header is not followed by a pass statement that test failed')

def random_word(charset, word_len):
    return "".join([random.choice(charset) for i in range(word_len)])

class CrackerTestCase(TestCase):
    TEST_PATH = "_autograder_cracker_test_"
    PASSWORDS = [
        "123456",
        "123456789",
        "qwerty",
        "password",
        "1234567",
        "12345678",
        "12345",
        "iloveyou",
        "111111",
        "123123",
        "abc123",
        "qwerty123",
        "1q2w3e4r",
        "admin",
        "qwertyuiop",
        "654321",
        "555555",
        "lovely",
        "7777777",
        "welcome",
        "888888",
        "princess",
        "dragon",
        "password1",
        "123qwe"]

    def setUp(self):
        if not os.path.exists(self.TEST_PATH):
            os.mkdir("_autograder_cracker_test_")
        if os.path.exists("cracker.py"):
            os.system("cp cracker.py {}".format(self.TEST_PATH))
        if os.path.exists("db.sqlite3"):
            os.system("cp db.sqlite3 {}".format(self.TEST_PATH))
        db = sqlite3.connect("{}/db.sqlite3".format(self.TEST_PATH))
        cursor = db.cursor()
        cursor.execute("DELETE FROM auth_user")
        self.passwords_permutation = self.PASSWORDS[:]
        random.shuffle(self.passwords_permutation)
        for i in range(len(self.PASSWORDS)):
            pw = self.passwords_permutation[i]
            salt = random_word(string.ascii_letters+string.digits, 12)
            kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt.encode(),
                    iterations=1,
                    )
            key_hash = kdf.derive(pw.encode())
            hash = "pbkdf2_sha256$1${}${}".format(salt, base64.b64encode(key_hash).decode())
            cursor.execute("INSERT INTO auth_user VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (i, hash, "2020-08-01 16:00:00.0", 0, "user"+str(i), '', '', 0, 1, "2020-08-01 15:00:00.0", ''))
        db.commit()
        os.chdir(self.TEST_PATH)
            
    def test_db_cracking(self):
        self.assertTrue(os.path.exists("cracker.py"))
        self.assertTrue(os.path.exists("db.sqlite3"))
        output = subprocess.check_output("python3 cracker.py", shell=True)
        output = output.decode()
        passwords_found = []
        for line in output.split("\n"):
            line = line.strip()
            if not line: continue
            if line.count(",") != 1: continue
            user, pw = line.split(",")
            user = user.strip()
            pw = pw.strip()
            self.assertTrue("user" in user)
            user_number = int(user.replace("user",""))
            self.assertTrue(user_number >= 0 and user_number < len(self.passwords_permutation))
            self.assertEqual(pw, self.passwords_permutation[user_number])
            passwords_found.append(pw)
        self.assertEqual(len(passwords_found), len(self.passwords_permutation))
            
    def test_db_cmdline(self):
        pw1 = random_word(string.ascii_lowercase, random.randint(2,4))
        pw2 = random_word(string.ascii_lowercase, random.randint(2,4))
        pw3 = random_word(string.ascii_lowercase, 6)
        self.assertTrue(os.path.exists("cracker.py"))
        self.assertTrue(os.path.exists("db.sqlite3"))
        
        pws = {pw1:True, pw2: True, pw3: False}
        for pw, should_pass in pws.items():
            salt = random_word(string.ascii_letters+string.digits, 12)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=1,
                )
            key_hash = kdf.derive(pw.encode())
            hash = "pbkdf2_sha256$1${}${}".format(salt, base64.b64encode(key_hash).decode())
            output = subprocess.check_output("python3 cracker.py '{}'".format(hash), shell=True)
            output = output.decode()
            output = output.lower()
            passed = False
            if "password not cracked" in output:
                passed = False
            if "password cracked" in output:
                passed = True
                self.assertTrue(output.count(":") == 1)
                password = output.split(":")[1].strip()
                self.assertTrue(password == pw or password[1:-1] == pw)
            self.assertEqual(should_pass, passed)
            
    def tearDown(self):
        if self.TEST_PATH in os.getcwd():
            os.chdir("..")
        if os.path.exists(self.TEST_PATH):
            os.system("rm -rf {}".format(self.TEST_PATH))
  
class TokenLoginTestCase(TestCase):
    def setUp(self):
        User.objects.create_user('bigshot', 'bigshot@lab1test.org', 'johnpassword', is_active=True)
        User.objects.create_user('rookie', 'rookie@lab1test.org', 'johnpassword', is_active=True)
        UserXtraAuth.objects.create(username="bigshot", secrecy=5, tokenkey = "password")
        UserXtraAuth.objects.create(username="rookie", secrecy=0, tokenkey = "")
        
    def test_zero_secrecy_login(self):
        data = {"username":"rookie", "password":"johnpassword"}
        form = TokenLoginForm(data=data)
        self.assertTrue(form.is_valid())
        
    def test_nonzero_secrecy_login(self):
        time_left, expected_token = next(fake_token.FakeToken("password".encode()))
        if time_left < 5.0:
            time.sleep(time_left+0.1)
            time_left, expected_token = next(fake_token.FakeToken("password".encode()))
        data = {"username":"bigshot", "password":"johnpassword"+str(expected_token)}
        form = TokenLoginForm(data=data)
        self.assertTrue(form.is_valid())

class ViewsTestCase(TestCase):
    def setUp(self):
        UserXtraAuth.objects.create(username="bigshot", secrecy=5, tokenkey = "")
        UserXtraAuth.objects.create(username="midlevel", secrecy=3, tokenkey = "")
        UserXtraAuth.objects.create(username="rookie", secrecy=0, tokenkey = "")
        
        User.objects.create_user('bigshot', 'bigshot@lab1test.org', 'johnpassword')
        User.objects.create_user('rookie', 'rookie@lab1test.org', 'johnpassword')
        User.objects.create_user('midlevel', 'midlevel@lab1test.org', 'johnpassword')
        authenticate(("bigshot", "johnpassword"))
        authenticate(("rookie", "johnpassword"))
        authenticate(("midlevel", 'johnpassword'))
        
        NewsListing.objects.create(queryId="abc", query="Top Secret", sources="", secrecy=5,lastuser="")
        NewsListing.objects.create(queryId="cde", query="Not Secret", sources="", secrecy=0,lastuser="")
        NewsListing.objects.create(queryId="bcd", query="Middle Secret", sources="", secrecy=3,lastuser="")
        
    def test_api_manager(self):
        
        test_api = NewsApiManager()
        
        #0 secrecy api cannot read articles of higher secrecy level
        test_api.update_secrecy(0)
        test_api.update_articles()
        
        self.assertEqual(len(test_api.data), 1)
        
        #5 secrecy api can read articles of equal or higher secrecy level
        test_api.update_secrecy(5)
        test_api.update_articles()
        
        self.assertEqual(len(test_api.data), 3)
            
    def test_nru_on_main_page(self):
        rookie = User.objects.get(username="rookie")
        bigshot = User.objects.get(username="bigshot")
        
        request_get = RequestFactory().get('/')
        request_get.user = bigshot
        render = index(request_get)
        
        self.assertTrue(str(render.content).count("Top Secret") == 1)
        self.assertTrue(str(render.content).count("Middle Secret") == 1)
        self.assertTrue(str(render.content).count("Not Secret") == 1)
        
        request_get.user = rookie
        render = user_account(request_get)
        
        self.assertTrue(str(render.content).count("Top Secret") == 0)
        self.assertTrue(str(render.content).count("Middle Secret") == 0)
        self.assertTrue(str(render.content).count("Not Secret") == 1)
        
    def test_user_account_read(self):
        """
        The test_user_account_* functions test sending data to the
        'user_account' handler and checks the output. This is separate
        from the forms validation that acutally checks data base update
        changes that happen because of these form requests.
        
        The only problem is, we didn't necessarily require the students
        to respond a certain way when the validation fails. Technically,
        they could return a blank page, or an error page, or whatever.
        
        So when false data is fed in that should fail, the only thing
        we will do is check the pages to make sure that read-up data
        isn't leaked
        """
        
        rookie = UserXtraAuth.objects.get(username="rookie")
        bigshot = UserXtraAuth.objects.get(username="bigshot")
        
        #set up requests
        request_get = RequestFactory().get('/')
        
        #test bigshot get
        request_get.user = bigshot
        render = user_account(request_get)
        
        self.assertTrue(str(render.content).count("abc") == 2)
        self.assertTrue(str(render.content).count("bcd") == 0)
        self.assertTrue(str(render.content).count("cde") == 0)
        
        request_get.user = rookie
        render = user_account(request_get)
        
        self.assertTrue(str(render.content).count("abc") == 0)
        self.assertTrue(str(render.content).count("bcd") == 0)
        self.assertTrue(str(render.content).count("cde") == 2)
        
    def test_user_account_create(self):
        """
        The test_user_account_* functions test sending data to the
        'user_account' handler and checks the output. This is separate
        from the forms validation that acutally checks data base update
        changes that happen because of these form requests.
        
        The only problem is, we didn't necessarily require the students
        to respond a certain way when the validation fails. Technically,
        they could return a blank page, or an error page, or whatever.
        
        So when false data is fed in that should fail, the only thing
        we will do is check the pages to make sure that read-up data
        isn't leaked
        """
    
        rookie = UserXtraAuth.objects.get(username="rookie")
        bigshot = UserXtraAuth.objects.get(username="bigshot")
        
        create_rookie_news_source_key = random_word(string.ascii_lowercase, 10)
        data = {'create_news': 'news', 'new_news_query': 'new', 'new_news_sources': create_rookie_news_source_key, 'new_news_secrecy': 5}
        request_post_create = RequestFactory().post('/', data)
        
        # test rookie create first
        request_post_create.user = rookie
        rookie_render = user_account(request_post_create)
        
        #test bigshot create
        create_bigshot_news_source_key = random_word(string.ascii_lowercase, 10)
        data["new_news_sources"] = create_bigshot_news_source_key
        request_post_create = RequestFactory().post('/', data)
        request_post_create.user = bigshot
        bigshot_render = user_account(request_post_create)
        
        
        # the count of "queryId" should be 2 because it shows up in the drop down
        # and in the table
        self.assertTrue(str(rookie_render.content).count("abc") == 0)
        self.assertTrue(str(rookie_render.content).count("bcd") == 0)
        self.assertTrue(str(rookie_render.content).count("cde") == 2)
        
        ## the count of these new news sources should be 0 (if not shown) or 1 in the table if shown
        self.assertTrue(str(rookie_render.content).count(create_rookie_news_source_key) == 0)
        self.assertTrue(str(rookie_render.content).count(create_bigshot_news_source_key) == 0)
        
        self.assertTrue(str(bigshot_render.content).count("abc") == 2)
        self.assertTrue(str(bigshot_render.content).count("bcd") == 0)
        self.assertTrue(str(bigshot_render.content).count("cde") == 0)
        self.assertTrue(str(bigshot_render.content).count(create_rookie_news_source_key) == 1)
        self.assertTrue(str(bigshot_render.content).count(create_bigshot_news_source_key) == 1)
        
        # test trying to have midlevel create data that is low
        # again, we will not check the database. That is a different
        # test. This just tests that data already in the database
        # doesn't leak out on error pages
        midlevel = UserXtraAuth.objects.get(username="midlevel")
        create_midlevel_news_source_key = random_word(string.ascii_lowercase, 10)
        data = {'create_news': 'news', 'new_news_query': 'new', 'new_news_sources': create_midlevel_news_source_key, 'new_news_secrecy': 0}
        request_post_create = RequestFactory().post('/', data)
        request_post_create.user = midlevel
        midlevel_render = user_account(request_post_create)
        
        # only check the data that should NOT be here. "bcd" is allowed,
        # but we don't know what the student returned.
        # don't even check the create_midlevel_news_source_key. That could
        # potentially be left on the page.
        self.assertTrue(str(midlevel_render.content).count("abc") == 0)
        self.assertTrue(str(midlevel_render.content).count("cde") == 0)
        
        
    def test_user_account_delete(self): 
        """
        The test_user_account_* functions test sending data to the
        'user_account' handler and checks the output. This is separate
        from the forms validation that acutally checks data base update
        changes that happen because of these form requests.
        
        The only problem is, we didn't necessarily require the students
        to respond a certain way when the validation fails. Technically,
        they could return a blank page, or an error page, or whatever.
        
        So when false data is fed in that should fail, the only thing
        we will do is check the pages to make sure that read-up data
        isn't leaked
        """

        rookie = UserXtraAuth.objects.get(username="rookie")
        bigshot = UserXtraAuth.objects.get(username="bigshot")
        
        
        data = {'update_delete': 'news', 'update_news_select': NewsListing.objects.get(queryId="abc").id}
        request_post_delete = RequestFactory().post('/', data)
        
        # try deleting a level 5 item with rookie first (shouldn't delete it)
        # we aren't going to check the database. That is done in the forms validation
        # this verifies that we see what we expect to see.
        # again, we don't know what the student returns, so only verify
        # that illegal data doesn't show. Don't verify that legal data shows
        request_post_delete.user = rookie
        render = user_account(request_post_delete)
        
        self.assertTrue(str(render.content).count("abc") == 0)
        self.assertTrue(str(render.content).count("bcd") == 0)
        
        # validate that bigshot still sees the level 5 item
        request_get = RequestFactory().get('/')
        request_get.user = bigshot
        render = user_account(request_get)
        
        self.assertTrue(str(render.content).count("abc") == 2)
        self.assertTrue(str(render.content).count("bcd") == 0)
        self.assertTrue(str(render.content).count("cde") == 0)
        
        # Now delete level 5 ("abc") and confirm that it doesn't show up
        request_post_delete.user = bigshot
        render = user_account(request_post_delete)
        
        self.assertTrue(str(render.content).count("abc") == 0)
        self.assertTrue(str(render.content).count("bcd") == 0)
        self.assertTrue(str(render.content).count("cde") == 0)
        
    def test_user_account_update(self): 
        """
        The test_user_account_* functions test sending data to the
        'user_account' handler and checks the output. This is separate
        from the forms validation that acutally checks data base update
        changes that happen because of these form requests.
        
        The only problem is, we didn't necessarily require the students
        to respond a certain way when the validation fails. Technically,
        they could return a blank page, or an error page, or whatever.
        
        So when false data is fed in that should fail, the only thing
        we will do is check the pages to make sure that read-up data
        isn't leaked
        """
        hi_source_key = random_word(string.ascii_letters, 10)
        data = {'update_update': 'news', 'update_news_query': 'new', 'update_news_sources': hi_source_key, 'update_news_secrecy': 5, 'update_news_select' : NewsListing.objects.get(queryId="abc").id}
        request_post_update_hi = RequestFactory().post('/', data)
        
        lo_source_key = random_word(string.ascii_letters, 10)
        data = {'update_update': 'news', 'update_news_query': 'new', 'update_news_sources': lo_source_key, 'update_news_secrecy': 0, 'update_news_select' : NewsListing.objects.get(queryId="cde").id}
        request_post_update_lo = RequestFactory().post('/', data)
        
        # have midlevel try to update low and hi. Both should fail.
        # Again, don't check the database. We'll do that in the forms validation
        # tests. But check that no sensitive data was leaked
        midlevel = UserXtraAuth.objects.get(username="midlevel")
        request_post_update_hi.user = midlevel
        request_post_update_lo.user = midlevel
        
        render = user_account(request_post_update_hi)
        self.assertTrue(str(render.content).count("abc") == 0)
        self.assertTrue(str(render.content).count("cde") == 0)
        
        render = user_account(request_post_update_lo)
        self.assertTrue(str(render.content).count("abc") == 0)
        self.assertTrue(str(render.content).count("cde") == 0)
        
        # now test updates for bigshot and rookie at
        # the appropriate levels
        rookie = UserXtraAuth.objects.get(username="rookie")
        bigshot = UserXtraAuth.objects.get(username="bigshot")
        
        #test bigshot update
        request_post_update_hi.user = bigshot
        render = user_account(request_post_update_hi)
        
        self.assertTrue(str(render.content).count("abc") == 2)
        self.assertTrue(str(render.content).count("bcd") == 0)
        self.assertTrue(str(render.content).count("cde") == 0)
        self.assertTrue(str(render.content).count(hi_source_key) == 1)
        
        #test rookie update
        request_post_update_lo.user = rookie
        render = user_account(request_post_update_lo)
        
        self.assertTrue(str(render.content).count("abc") == 0)
        self.assertTrue(str(render.content).count("bcd") == 0)
        self.assertTrue(str(render.content).count("cde") == 2)
        self.assertTrue(str(render.content).count(lo_source_key) == 1)
        
            
        
    def test_form_validation(self):
        
        rookie = UserXtraAuth.objects.get(username="rookie")
        bigshot = UserXtraAuth.objects.get(username="bigshot")
        
        #set up requests
        # create a unique source that can be used to search the db
        create_source_key = random_word(string.ascii_lowercase, 10)
        data = {'create_news': 'news', 'new_news_query': 'new', 'new_news_sources': create_source_key, 'new_news_secrecy': 3}
        request_post_create = RequestFactory().post('/', data)
        
        update_source_key_3 = random_word(string.ascii_lowercase, 10)
        data = {'update_update': 'news', 'update_news_query': 'new', 'update_news_sources': update_source_key_3, 'update_news_secrecy': 3, 'update_news_select' : NewsListing.objects.get(queryId="bcd").id}
        request_post_update_3 = RequestFactory().post('/', data)
        
        update_source_key_5 = random_word(string.ascii_lowercase, 10)
        data = {'update_update': 'news', 'update_news_query': 'new', 'update_news_sources': update_source_key_5, 'update_news_secrecy': 5, 'update_news_select' : NewsListing.objects.get(queryId="abc").id}
        request_post_update_5 = RequestFactory().post('/', data)
        
        update_source_key_5_to_3 = random_word(string.ascii_lowercase, 10)
        data = {'update_update': 'news', 'update_news_query': 'new', 'update_news_sources': update_source_key_5_to_3, 'update_news_secrecy': 3, 'update_news_select' : NewsListing.objects.get(queryId="abc").id}
        request_post_update_5_to_3 = RequestFactory().post('/', data)
        
        
        data = {'update_delete': 'news', 'update_news_select': NewsListing.objects.get(queryId="bcd").id}
        request_post_delete = RequestFactory().post('/', data)
        
        ######
        # WRITE TEST
        #  1. Write down (not allowed)
        #  2. Write up (allowed) 
        ####
        
        
        self.assertEqual(len(NewsListing.objects.filter(sources=create_source_key)), 0)
        request_post_create.user = bigshot
        user_account(request_post_create)
        # should not have added (5->3) is a write-down
        self.assertEqual(len(NewsListing.objects.filter(sources=create_source_key)), 0)
        request_post_create.user = rookie
        user_account(request_post_create)
        self.assertEqual(len(NewsListing.objects.filter(sources=create_source_key)), 1)
        
        
        
        ####
        # Update Test
        #   1. Attempt to update down (not allowed)
        #   2. Attempt to update same level (allowed)
        #   3. Attempt to update same level to lower level (not allowed)
        # 
        # Attempting to update up is also technically not 
        # allowed in this lab... but it's just weird enough
        # that we won't test it here. Satisfied to simply not
        # post any information (read up)
        
        # attempt to update at an item at a different security level (5->3)
        bcd = NewsListing.objects.get(queryId="bcd")
        self.assertFalse(bcd.sources == update_source_key_3)
        request_post_update_3.user = bigshot
        render = user_account(request_post_update_3)
        bcd = NewsListing.objects.get(queryId="bcd")
        self.assertFalse(bcd.sources == update_source_key_3)
        
        bcd = NewsListing.objects.get(queryId="abc")
        self.assertFalse(bcd.sources == update_source_key_5)
        request_post_update_5.user = bigshot
        render = user_account(request_post_update_5)
        bcd = NewsListing.objects.get(queryId="abc")
        self.assertTrue(bcd.sources == update_source_key_5)
        
        bcd = NewsListing.objects.get(queryId="abc")
        self.assertEqual(bcd.secrecy, 5)
        request_post_update_5_to_3.user = bigshot
        render = user_account(request_post_update_5_to_3)
        bcd = NewsListing.objects.get(queryId="abc")
        self.assertEqual(bcd.secrecy, 5)
            
        
        ####
        # DELETE TEST
        # 1. Attempt to delete a lower secrecy item (not allowed)
        # 2. Attempt to delete an item at the same level (allowed)
        ###
        # attempt to delete at a different security level (5->3) and fail
        
        self.assertEqual(len(NewsListing.objects.filter(queryId="bcd")), 1)
        request_post_delete.user = bigshot
        render = user_account(request_post_delete)
        self.assertEqual(len(NewsListing.objects.filter(queryId="bcd")), 1)
        
        NewsListing.objects.create(queryId="to_delete", query="Delete Secret", sources="", secrecy=5,lastuser="")
        
        data = {'update_delete': 'news', 'update_news_select': NewsListing.objects.get(queryId="to_delete").id}
        request_post_delete_ok = RequestFactory().post('/', data)
        
        self.assertEqual(len(NewsListing.objects.filter(queryId="to_delete")), 1)
        request_post_delete_ok.user = bigshot
        render = user_account(request_post_delete_ok)
        self.assertEqual(len(NewsListing.objects.filter(queryId="to_delete")), 0)
            

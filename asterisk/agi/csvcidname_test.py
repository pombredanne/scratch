import tempfile
import shutil
import unittest
import StringIO
import os

import csvcidname


class Tests(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_no_such_file(self):
        stdout = StringIO.StringIO()
        self.assertEqual(
            csvcidname.main(None, stdout, 
                            os.path.join(self.tempdir, "test")), 1)
        self.assertEqual(stdout.getvalue(), """\
verbose "couldn't find csv file %s/test"
""" % self.tempdir)
    
    def test_no_callerid(self):
        stdin = StringIO.StringIO("""\
nothere:

""")
        stdout = StringIO.StringIO()
        filename = os.path.join(self.tempdir, "test")
        file(filename, "w").close()
        csvcidname.main(stdin, stdout, filename)
        self.assertEqual(stdout.getvalue(), "")
        
    def test_no_matching_name(self):
        stdin = StringIO.StringIO("""\
agi_something: onetwothree 
agi_callerid: 123

""")
	class Stdin(object):
	    def generator(self):
                for line in stdin:
                    yield line
                while True:
                    yield "more\n"
	
	    def readline(self):
	        return self.generator().next()

        stdout = StringIO.StringIO()
        filename = os.path.join(self.tempdir, "test")
        file(filename, "w").close()
        
        csvcidname.main(Stdin(), stdout, filename)
        self.assertEqual(stdout.getvalue(), "")

    def test_match(self):
        stdin = StringIO.StringIO("""\
agi_something: onetwothree 
agi_callerid: 123

""")
        stdout = StringIO.StringIO()
        filename = os.path.join(self.tempdir, "test")
        file(filename, "w").write("""\
"456","D E F"
"123","A B C"
""")
        csvcidname.main(stdin, stdout, filename)
        self.assertEqual(stdout.getvalue(), """\
verbose "Changing CallerID to A B C<123>"
set callerid "A B C<123>"
""")


if __name__ == "__main__":
    unittest.main()


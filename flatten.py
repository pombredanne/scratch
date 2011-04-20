
import tempfile


class Test(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test(self):
        os.mkdir(os.path.join(self.dir, "a"))
        open(os.path.join(self.dir, "a", "file"), "w").close()

        flatten(os.path.join(self.dir, "a"))

        self.assert_(os.path.exists(os.path.join(self.dir, "file")))
        




def main():

if __name__ == "__main__":
    print "Hello World";

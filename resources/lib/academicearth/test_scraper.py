import unittest
import scraper

class UniversitiesIT(unittest.TestCase):

    def test_get_universities(self):
        yale = {
            'url': u'http://www.academicearth.org/universities/yale',
            'name': u'Yale',
            'icon': u'http://ae_img.s3.amazonaws.com/University/3/200x100_Logo.jpg',
        }

        unis = scraper.get_universities()

        # currently there are 41 universities
        self.assertTrue(len(unis) > 35)

        # hopefully Yale will always be there...
        self.assertTrue(yale in unis)

    def test_get_university_metadata(self):
        url = 'http://www.academicearth.org/universities/university-of-oxford'
        metadata = scraper.get_university_metadata(url)
        print metadata

import unittest
import scraper

class UniversityIT(unittest.TestCase):

    def test_get_universities_partial(self):
        yale = {
            'url': u'http://www.academicearth.org/universities/yale',
            'name': u'Yale',
            'icon': u'http://ae_img.s3.amazonaws.com/University/3/200x100_Logo.jpg',
        }

        unis = scraper.University.get_universities_partial()

        # currently there are 41 universities
        self.assertTrue(len(unis) > 35)

        # hopefully Yale will always be there...
        self.assertTrue(yale in unis)

    def test_from_url(self):
        url = 'http://www.academicearth.org/universities/university-of-oxford'
        uni = scraper.University.from_url(url)

        assert uni['name'] == 'Oxford'
        assert uni['description'].startswith('The University of Oxford')
        assert len(uni['courses']) > 7
        assert len(uni['lectures']) > 0

from bs4 import BeautifulSoup
import unittest

from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_actual_search_results(self):
       
        search_term = "cosine tangent"  # Change this to the desired search term
        response = self.client.post("/", data={"search_term": search_term})

        # Check if the request was successful (status code 200)
        self.assertEqual(response.status_code, 200)

        # Parse the HTML response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the actual search results (video titles)
        actual_results = []

        # Assuming each video title is enclosed in an <h2> tag
        video_titles = soup.find_all('h2')

        for title in video_titles:
            actual_results.append(title.text)

        # Define the expected results for this specific test case
        expected_results = ['Evaluating Improper Integrals', 'Higher Derivatives and Their Applications', 'Evaluating Integrals With Trigonometric Functions', 'Implicit Differentiation', 'Polar coordinates 2 | Parametric equations and polar coordinates | Precalculus | Khan Academy', 'Trigonometric Identities', 'Finding Local Maxima and Minima by Differentiation', 'Integration By Trigonometric Substitution', 'Polar coordinates 1 | Parametric equations and polar coordinates | Precalculus | Khan Academy', 'Unit Circle Definition of Trig Functions', 'Derivatives of Composite Functions: The Chain Rule', 'Basic trigonometry II | Basic trigonometry | Trigonometry | Khan Academy', 'Ferris Wheel Trig Problem (part 2)', 'Integration Using The Substitution Rule', 'Inverse trig functions: arctan | Trigonometry | Khan Academy', 'The unit circle definition of trigonometric function', "Understanding Limits and L'Hospital's Rule", 'Understanding Differentiation Part 1: The Slope of a Tangent Line', 'Trig identities part 3 (part 5 if you watch the proofs) | Trigonometry | Khan Academy', 'Advanced Strategy for Integration in Calculus', 'Determining the equation of a trigonometric function', 'Inverse trig functions: arccos | Trigonometry | Khan Academy', 'Integration By Parts', 'Graphs of trig functions', 'Proof of the law of cosines | Trig identities and examples | Trigonometry | Khan Academy', 'Understanding Differentiation Part 2: Rates of Change', 'The Mean Value Theorem For Integrals: Average Value of a Function', 'Trig identities part 2 (part 4 if you watch the proofs) | Trigonometry | Khan Academy', 'What is a Derivative? Deriving the Power Rule', 'Derivatives of Trigonometric Functions', 'Basic trigonometry | Basic trigonometry | Trigonometry | Khan Academy']

        # Check if all elements in actual_results are in expected_results
        self.assertSetEqual(set(actual_results), set(expected_results))
    


    def test_unrelated_search(self):
        """Test search with unrelated keyword"""
        term = "hello world"
        response = self.client.post("/", data={"search_term": term})
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraph_text = soup.find('p').get_text()
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"There are no videos related to '{term}'", paragraph_text)
    


    def test_related_search(self):
        """Test search with related keyword"""
        term = "cosine"
        response = self.client.post('/', data={"search_term": term})
        soup = BeautifulSoup(response.text, 'html.parser')
        self.assertEqual(f'Search Results for "{term}"', soup.find('h1').get_text())

        ul_element = soup.find('ul', class_='video-list')

        # Find all <li> elements within the <ul> element
        li_elements = ul_element.find_all('li')

        # Count the total number of <li> elements
        total_li_elements = len(li_elements)
        self.assertGreater(total_li_elements, 0)

        self.assertEqual(200, response.status_code)



    def test_video_heading_link(self):
        """Test video element has heading with link"""
        term = "cosine"
        response = self.client.post('/', data={"search_term": term})
        soup = BeautifulSoup(response.text, 'html.parser')
        ul_element = soup.find('ul', class_='video-list')

        # Find all <li> elements within the <ul> element
        li_elements = ul_element.find_all('li')
        has_a_tag = li_elements[0].find('h2').find('a') is not None
        self.assertTrue(has_a_tag)

    def test_timestamp_links(self):
        search_term = "cosine tangent"  # Change this to the desired search term
        response = self.client.post("/", data={"search_term": search_term})

        # Check if the request was successful (status code 200)
        self.assertEqual(response.status_code, 200)

        # Parse the HTML response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the timestamps with links from the HTML
        timestamps_with_links = []

        # Find all <p> elements with class "video-metadata"
        video_metadata_elements = soup.find_all('p', class_='video-metadata')

        for metadata in video_metadata_elements:
            # Find any <a> elements within the <p> element
            timestamp_links = metadata.find_all('a')

            for link in timestamp_links:
                timestamps_with_links.append(link.get('href'))

        # Check if any timestamps have embedded links
        self.assertTrue(any(timestamps_with_links))

        # Check if the links are valid (start with "http" or "https")
        for link in timestamps_with_links:
            self.assertTrue(link.startswith("http://") or link.startswith("https://"))


flask_test = unittest.TestLoader().loadTestsFromTestCase(AppTestCase)


main = unittest.TestSuite([
    flask_test
])

if __name__=='__main__':
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(main)
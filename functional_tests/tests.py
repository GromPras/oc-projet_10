import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By


class NewAPIClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.browser = webdriver.Firefox()
        return super().setUp()

    def tearDown(self) -> None:
        self.browser.quit()
        return super().tearDown()

    def test_can_discover_api_root(self):
        # A client request the api' root url
        self.browser.get("http://localhost:8000")

        # The page heading should mention "Api Root"
        page_heading = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertIsNotNone(page_heading)
        self.assertIn("Api Root", page_heading.text)


if __name__ == "__main__":
    unittest.main()

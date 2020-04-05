
raise NotImplementedError("coming soon")

from selenium import webdriver

from arackpy.backends.backend_default import Backend


class Backend_Selenium(Backend):
    """Uses Selenium to get html thereby getting around the problem of page
    loading related running javascript scripts.
    """

    def __init__(self, spider):
        super(Backend_Selenium, self).__init__(spider)
        self.driver = webdriver.Firefox()

    def urlread(self, url, timeout):
        self.driver.get(url)

    def urlparse(self):
        return self.driver.execute_script("return document.documentElement.outerHTML")

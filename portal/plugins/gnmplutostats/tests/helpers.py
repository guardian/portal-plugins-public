class MockResponse(object):
    def __init__(self,status_code,body_content):
        self.status_code=status_code
        self.text = body_content
        self.headers = {}
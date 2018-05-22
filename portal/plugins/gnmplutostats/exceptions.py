class HttpError(StandardError):
    def __init__(self, requests_response):
        self.status_code = requests_response.status_code
        self.body = requests_response.text
        self.response_headers = requests_response.headers

    def __str__(self):
        return "server responded {status} {body}".format(status=self.status_code,body=self.body)


class InvalidMetadata(StandardError):
    pass
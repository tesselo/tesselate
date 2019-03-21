class TesselateMockResponseBase(object):

    def json(self):
        return {}

    def raise_for_status(self):
        pass

    @property
    def content(self):
        return self.json()

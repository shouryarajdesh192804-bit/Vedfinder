class AdManager:

    def __init__(self):
        self.enabled = False

    def banner(self):

        return {
            "enabled": self.enabled,
            "client": "",
            "slot": ""
        }

ads = AdManager()
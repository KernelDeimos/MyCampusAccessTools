class PostData:
    def __init__(self):
        self.items = []
    def add_item(self,name,value):
        self.items.append([name,value])
    def get_string(self):
        # Python for the win! Love one-lining this stuff! - EAD
        res = '&'.join([item[0] + "=" + item[1] for item in self.items])
        return res
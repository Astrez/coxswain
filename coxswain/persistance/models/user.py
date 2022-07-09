class User:
    def __init__(self, username = "", password = "", name = "", **kwargs):
        self.username = username
        self.password = password
        self.name = name
        # U : User
        # A : Admin
        print(kwargs)
        if kwargs.get("role", None) != "U":
            self.role = "A"
        else:
            self.role = "U"

    def compare(self, newPassword):
        return self.password == newPassword
    
    def getDict(self):
        return {
            "username" : self.username,
            "name" : self.name,
            "role" : self.role
        }
    
    def save(self):
        return {
            "username" : self.username,
            "password" : self.password,
            "name" : self.name,
            "role" : self.role
        }
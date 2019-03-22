from collections import UserList


class Stack(UserList):

    def push(self, val):
        self.append(val)

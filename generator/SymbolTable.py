class Symbol:
    def __init__(self, name, value):
        self.__name = name
        self.__value = value
        self.__type = ""

    def getName(self):
        return self.__name

    def getValue(self):
        return self.__value

    def setValue(self, value):
        self.__value = value

    def setName(self,name):
        self.__name = name

    def setType(self,type):
        self.__type = type

    def getType(self):
        return self.__type

class SymbolTable:
    def __init__(self):
        self.SymbolList = list()

    def add(self, symbol):
        self.SymbolList.append(symbol)

    def find(self, name):
        if not self.SymbolList:
            return None
        for i in self.SymbolList:
            if i.getName() == name:
                return i
        return None

    def pop(self,name):
        if not self.SymbolList:
            return None
        for i in range(len(self.SymbolList)):
            if self.SymbolList[i].getName() == name:
                return self.SymbolList.pop(i)
        return None

    def update(self, name, value):
        if not self.SymbolList:
            return False
        for i in self.SymbolList:
            if i.getName() ==name:
                i.setValue(value)
                return True
        return False

    def clear(self):
        self.SymbolList.clear()



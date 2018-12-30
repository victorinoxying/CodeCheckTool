import os
import random
from random import choice
from generator.SymbolTable import Symbol,SymbolTable

tag_other = '//TAG.OTHER'
tag_body = '//TAG.BODY'
tag_safe = '//TAG.SAFE'
tag_unsafe = '//TAG.UNSAFE'
#OVERFLOW_NUM = 4594967296
MAXLENTH = 50
MAX_OBJECT_NUM = 20
MAX_VALUE = 100
TYPE_INT = 'int'
TYPE_POINT = 'int *'

def standardizeStr(code, tag, level):
    length = len(code)
    result = level*'\t'+code+ (MAXLENTH-length-level*4)*' '+tag+'\n'
    return result

HEAD = standardizeStr('#include <stdlib.h>',tag_other,0)+ standardizeStr('int main(){',tag_body,0)
END = standardizeStr('return 0;',tag_body,1)+'}'+49*' '+tag_body

class Generator:
    def __init__(self):
        self.__table = SymbolTable()
        self.__typeList =[
            TYPE_INT,
            TYPE_POINT
        ]
        self.undeclare_set = set()
        self.declared_set = set()
        self.assigned_set = set()
        self.point_set = set()
        self.record_set = set()

    def flushSet(self):
        self.undeclare_set.clear()
        self.declared_set.clear()
        self.assigned_set.clear()
        self.point_set.clear()
        self.record_set.clear()
        self.__table.clear()
        for i in range(MAX_OBJECT_NUM):
            self.undeclare_set.add('obj_'+str(i))

    def declare(self,name,type=""):
        symbol = Symbol(name,0)
        if type=="":
            type = choice(self.__typeList)
        symbol.setType(type)
        if (symbol.getType() == "int"):
            self.__table.add(symbol)
            content = type + ' ' + name + ';'
        if (symbol.getType() == "int *"):
            self.__table.add(symbol)
            self.point_set.add(name)
            self.record_set.add(name)
            content = type + name + ';'
        tag = tag_body
        return content,tag

    def free(self,name):
        if name in self.point_set:
            tag = tag_safe
            self.point_set.remove(name)
        else:
            tag = tag_unsafe
        content = 'free('+name+');'
        return content, tag

    def assignNum(self,name):
        value = random.randint(-MAX_VALUE, MAX_VALUE)
        symbol = self.__table.pop(name)
        content=''
        tag=''
        if symbol.getType() == TYPE_INT:
            tag = tag_safe
            symbol.setValue(value)
            content = name+' = '+ str(value)+';'
        else:
            content = ""
            tag = tag_other
        self.__table.add(symbol)
        return content, tag

    def assignValue(self,lName,rName):
        lSymbol = self.__table.pop(lName)
        rSymbol = self.__table.find(rName)
        rValue = rSymbol.getValue()
        rType =rSymbol.getType()
        lType = lSymbol.getType()

        content=''
        tag = ''
        if lType==TYPE_POINT and rType == TYPE_INT:
            if lName in self.point_set:
                tag = tag_safe
                lSymbol.setValue(rValue)
                content = lName+'= &'+rName+';'
            else:
                tag = tag_unsafe
                lSymbol.setValue(rValue)
                content = lName + '= &' + rName + ';'
        elif lType == TYPE_POINT and rType == TYPE_POINT:
            if lName in self.point_set:
                if rName in self.point_set:
                    tag = tag_safe
                    lSymbol.setValue(rValue)
                    content = lName+'= '+rName+';'
            else:
                tag = tag_unsafe
                lSymbol.setValue(rValue)
                content = lName + '= ' + rName + ';'
        elif lType == TYPE_INT and rType == TYPE_POINT:
            tag = tag_other
            content=""
        else:
            tag = tag_body
            lSymbol.setValue(rValue)
            content = lName+' = '+rName+';'
        self.__table.add(lSymbol)
        return content, tag

    def stm(self,min = 10, max = 15, assignedNeed = 1,free = True):
        if not self.undeclare_set:
            return
        code = ""
        op_list = [self.assignNum, self.declare, self.assignValue,self.free]
        i = random.randint(min, max)
        while i > 0 or assignedNeed > len(self.assigned_set):
            func = choice(op_list)
            i = i-1
            if func == self.declare:
                if not self.undeclare_set:
                    i = i + 1
                    continue
                luckyOne = self.undeclare_set.pop()
                self.declared_set.add(luckyOne)
                content,tag = func(luckyOne)
                code += standardizeStr(content,tag,1)
                # print(content,tag)
            elif func == self.assignNum:
                if not self.declared_set:
                    i = i+1
                    continue
                luckyOne = self.declared_set.pop()
                self.declared_set.add(luckyOne)
                self.assigned_set.add(luckyOne)
                content,tag = func(luckyOne)
                if content=="":
                    code =code
                else:
                    code += standardizeStr(content, tag,1)
                # print(content,tag)
            elif func == self.free:
                if free==True:
                    if not self.record_set:
                        i = i+1
                        continue
                    luckyOne = self.record_set.pop()
                    self.record_set.add(luckyOne)
                    content, tag = func(luckyOne)
                    code += standardizeStr(content, tag, 1)
            else:#assignValue
                if len(self.assigned_set)<2:
                    i=i+1
                    continue
                lValue = self.assigned_set.pop()
                rValue = self.assigned_set.pop()
                self.assigned_set.add(lValue)
                self.assigned_set.add(rValue)
                content,tag = func(lValue,rValue)
                if content=="":
                    code =code
                else:
                    code += standardizeStr(content, tag,1)
                # print(content,tag)
        return code

    def nomal_stm(self):
        self.flushSet()
        code = HEAD
        code += self.stm()
        code += END

        return code

    def if_stm(self):
        self.flushSet()
        code = HEAD
        d1 = self.undeclare_set.pop()
        self.declared_set.add(d1)
        de1, dtag1 = self.declare(d1,'int *')
        code += standardizeStr(de1, dtag1, 1)
        code += self.stm(4, 5, 1,False)

        left_condition = random.randint(1, 40)
        right_condition = random.randint(1, 40)
        if_code = 'if(%s < %s){' %(left_condition,right_condition)

        ifOne = self.record_set.pop()
        self.record_set.add(ifOne)
        content1, tag1 = self.free(ifOne)

        else_code = '} else{'
        tempnum = random.random()
        if(tempnum>0.5):
            elseOne = self.undeclare_set.pop()
            content2, tag2 = self.declare(elseOne)
            self.declared_set.add(elseOne)
        else:
            elsetwo = self.declared_set.pop()
            content2, tag2 = self.assignNum(elsetwo)
        if_end_code = '}'

        code+=standardizeStr(if_code,tag_body,1)
        code+= standardizeStr(content1,tag1,2)
        code+= standardizeStr(else_code, tag_body,1)
        code += standardizeStr(content2, tag2,2)
        code+= standardizeStr(if_end_code, tag_body,1)

        code += self.stm(4, 5, 2)
        code += END

        return code

    def print_value_table(self):
        if not self.__table.SymbolList:
            print('no value')
        else:
            for i in self.__table.SymbolList:
                print('type:', i.getType(), 'name:',i.getName(), 'value:',i.getValue())

    def getData(self, fileName, num):
        if not os.path.exists(fileName):
            print('wrong file path')
            return
        #func_list = [self.nomal_stm,self.if_stm]
            #, self.while_stm, self.if_stm, self.for_stm
        for i in range(num):
            codePath = fileName+'/code_'+ str(i)+'.c'
            func = self.if_stm
            with open(codePath,'w') as fileStream:
                fileStream.write(func())




if __name__ == '__main__':
    ge = Generator()
    ge.getData('D:/test/',10)


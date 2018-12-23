import random
from random import choice
from generator.SymbolTable import Symbol,SymbolTable

tag_other = '//TAG.OTHER'
tag_body = '//TAG.BODY'
tag_safe = '//TAG.SAFE'
tag_unsafe = '//TAG.UNSAFE'
OVERFLOW_NUM = 4594967296
MAXLENTH = 50
MAX_OBJECT_NUM = 10
MAX_VALUE = 100
TYPE_INT = 'int'
TYPE_UINT = 'unsigned int'
def standardizeStr(code, tag, level):
    length = len(code)
    result = level*'\t'+code+ (MAXLENTH-length-level*4)*' '+tag+'\n'
    return result

HEAD = standardizeStr('#include <stdlib.h>',tag_other,0)+ standardizeStr('int main(){',tag_body,0)
END = standardizeStr('return 0;',tag_body,1)+standardizeStr('}',tag_other,0)

class Generator:
    def __init__(self):
        self.__table = SymbolTable()
        self.__typeList =[
            TYPE_INT,
            TYPE_UINT
        ]
        self.undeclare_set = set()
        self.declared_set = set()
        self.assigned_set = set()

    def flushSet(self):
        self.undeclare_set.clear()
        for i in range(MAX_OBJECT_NUM):
            self.undeclare_set.add('obj_'+str(i))

    def declare(self,name):
        symbol = Symbol(name,0)
        type = choice(self.__typeList)
        symbol.setType(type)
        self.__table.add(symbol)
        content = type + ' '+ name+';'
        tag = tag_body
        return content,tag

    def assignNum(self,name):
        tag = tag_safe
        value = random.randint(-MAX_VALUE, MAX_VALUE)
        symbol = self.__table.pop(name)
        if value <= 0 and symbol.getType() == TYPE_UINT:
            tag = tag_unsafe
            symbol.setValue(OVERFLOW_NUM+value)
        else:
            symbol.setValue(value)
        self.__table.add(symbol)
        content = name+' = '+ str(value)+';'

        return content,tag

    def assignValue(self,lName,rName):
        lSymbol = self.__table.pop(lName)
        rSymbol = self.__table.find(rName)
        rValue = rSymbol.getValue()
        rType = rSymbol.getType()
        lType = lSymbol.getType()
        tag = tag_safe
        if lType==TYPE_UINT and rType ==TYPE_INT:
            tag = tag_unsafe
            if rValue <=0:
                lSymbol.setValue(OVERFLOW_NUM+rValue)
            else:
                lSymbol.setValue(rValue)
        else:
            lSymbol.setValue(rValue)
        self.__table.add(lSymbol)
        content = lName+' = '+rName+';'
        return content, tag

    def stm(self,min = 10, max = 15, assignedNeed = 1):
        if not self.undeclare_set:
            return
        code = HEAD
        op_list = [self.assignNum, self.declare, self.assignValue]
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
                code +=standardizeStr(content, tag,1)
                # print(content,tag)
            else:
                if len(self.assigned_set)<2:
                    i=i+1
                    continue
                slice = random.sample(self.assigned_set,2)
                content,tag = func(slice[0],slice[1])
                code += standardizeStr(content, tag,1)
                # print(content,tag)
        return code

    def nomal_stm(self):
        self.flushSet()
        code = self.stm()
        code+=END
        print(code)

    def if_stm(self):
        self.flushSet()
        code = self.stm(3, 4, 3)
        left_condition = self.assigned_set.pop()
        right_condition = self.assigned_set.pop()
        state = self.assigned_set.pop()
        self.assigned_set.add(left_condition)
        self.assigned_set.add(right_condition)
        self.assigned_set.add(state)

        if_code = 'if(%s < %s){' %(left_condition,right_condition)
        state_code = '%s--;' % state
        else_code = '} else{'
        else_state_code = '%s++;' %state
        if_end_code = '}'




    def for_stm(self):
        self.flushSet()
        code = self.stm(3,4,3)

        init = self.assigned_set.pop()
        condition = self.assigned_set.pop()
        state = self.assigned_set.pop()
        self.assigned_set.add(init)
        self.assigned_set.add(condition)
        self.assigned_set.add(state)

        condition_symbol =  self.__table.find(condition)
        init_symbol = self.__table.pop(init)
        state_symbol =  self.__table.pop(state)

        compare_value = condition_symbol.getValue()
        init_value = random.randint(-MAX_VALUE,compare_value)
        state_value = state_symbol.getValue()
        differ_value = compare_value - init_value

        # for循环处理
        for_start_code = 'for(%s = %s; %s < %s; %s++){' %(init,init_value,init,condition,init)
        for_state_code = '%s--;' % state
        for_end_code = '}'
        if init_symbol.getType()==TYPE_UINT and init_value<=0:
            init_symbol.setValue(MAX_VALUE+init_value)

            code+=standardizeStr(for_start_code,tag_unsafe,1)
            code+=standardizeStr(for_state_code, tag_body,2)
            code+=standardizeStr(for_end_code,tag_body,1)
            code+=END

            self.__table.add(init_symbol)
            self.__table.add(state_symbol)
            print(code)
            return
        new_state_value = state_value - differ_value
        state_tag = tag_safe
        if state_symbol.getType() == TYPE_UINT and new_state_value<0:
            new_state_value+=MAX_VALUE
            state_tag = tag_unsafe
        state_symbol.setValue(new_state_value)
        init_symbol.setValue(compare_value)

        code += standardizeStr(for_start_code, tag_body,1)
        code += standardizeStr(for_state_code, state_tag,2)
        code += standardizeStr(for_end_code, tag_body,1)
        code += END

        self.__table.add(init_symbol)
        self.__table.add(state_symbol)
        print(code)

        # print('table:')
        # for i in self.__table.SymbolList:
        #     print(i.getName(),i.getType(),i.getValue())










if __name__ == '__main__':
    ge = Generator()
    ge.nomal_stm()

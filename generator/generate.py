import os
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
END = standardizeStr('return 0;',tag_body,1)+'}'+49*' '+tag_body

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
        self.declared_set.clear()
        self.assigned_set.clear()
        self.__table.clear()
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

        value = random.randint(-MAX_VALUE, MAX_VALUE)
        symbol = self.__table.pop(name)
        if value <= 0 and symbol.getType() == TYPE_UINT:
            tag = tag_unsafe
            symbol.setValue(OVERFLOW_NUM+value)
        else:
            tag = tag_safe
            symbol.setValue(value)
        self.__table.add(symbol)
        content = name+' = '+ str(value)+';'
        return content,tag

    def assignValue(self,lName,rName):
        lSymbol = self.__table.pop(lName)
        rSymbol = self.__table.find(rName)
        rValue = rSymbol.getValue()
        rType =rSymbol.getType()
        lType = lSymbol.getType()

        if lType==TYPE_UINT and rType == TYPE_INT:
            tag = tag_unsafe
            if rValue<=0:
                lSymbol.setValue(OVERFLOW_NUM+rValue)
            else:
                lSymbol.setValue(rValue)
        else:
            tag = tag_safe
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
                lValue = self.assigned_set.pop()
                rValue = self.assigned_set.pop()
                self.assigned_set.add(lValue)
                self.assigned_set.add(rValue)
                content,tag = func(lValue,rValue)
                code += standardizeStr(content, tag,1)
                # print(content,tag)
        return code

    def nomal_stm(self):
        self.flushSet()
        code = self.stm()
        code += END

        # print(code)
        return code

    def while_stm(self):
        self.flushSet()
        code = self.stm(3, 4, 3)
        left_condition = self.assigned_set.pop()
        self.assigned_set.add(left_condition)

        left_condition_symbol = self.__table.pop(left_condition)
        left_value = left_condition_symbol.getValue()
        left_type = left_condition_symbol.getType()
        right_value = random.randint(-MAX_VALUE,MAX_VALUE)

        while_code = 'while(%s > %s){'%(left_condition,right_value)
        state_code = '%s--;'%left_condition
        while_end_code = '}'

        state_tag = tag_safe

        if left_value <= right_value:
            state_tag =tag_body
        else:
            if left_type == TYPE_UINT and right_value <= 0:
                state_tag = tag_unsafe
                left_condition_symbol.setValue(OVERFLOW_NUM + right_value)
            else:
                left_condition_symbol.setValue(right_value)


        self.__table.add(left_condition_symbol)
        code+=standardizeStr(while_code,tag_body,1)
        code+=standardizeStr(state_code,state_tag,2)
        code+=standardizeStr(while_end_code,tag_body,1)
        code += END

        # print(code)
        return code




    def if_stm(self):
        self.flushSet()
        code = self.stm(5, 7, 4)
        left_condition = self.assigned_set.pop()
        right_condition = self.assigned_set.pop()
        state = self.assigned_set.pop()
        else_state = self.assigned_set.pop()
        self.assigned_set.add(left_condition)
        self.assigned_set.add(right_condition)
        self.assigned_set.add(state)
        self.assigned_set.add(else_state)

        change_num = random.randint(10, 40)

        if_code = 'if(%s < %s){' %(left_condition,right_condition)
        state_code = '%s -= %s;' % (state, change_num)
        else_code = '} else{'
        else_state_code = '%s = %s;' % (state, else_state)
        if_end_code = '}'

        left_condition_symbol = self.__table.find(left_condition)
        right_condition_symbol = self.__table.find(right_condition)
        state_symbol = self.__table.pop(state)
        else_state_symbol = self.__table.pop(else_state)
        else_state_value = else_state_symbol.getValue()
        state_type = state_symbol.getType()
        state_value = state_symbol.getValue()

        if_state_tag = tag_safe
        else_state_tag = tag_safe

        if left_condition_symbol.getValue() < right_condition_symbol.getValue():
            else_state_tag =tag_body
            state_value -= change_num
            if state_value<=0 and state_type == TYPE_UINT:
                if_state_tag = tag_unsafe
                state_symbol.setValue(state_value+OVERFLOW_NUM)
            else:
                state_symbol.setValue(state_value)
        else:
            if_state_tag = tag_body
            if else_state_symbol.getType() == TYPE_UINT and state_type == TYPE_INT:
                else_state_tag = tag_unsafe
                if else_state_value<= 0:
                    else_state_value += OVERFLOW_NUM
                    state_symbol.setValue(else_state_value)
                else:
                    state_symbol.setValue(else_state_value)
            else:
                state_symbol.setValue(else_state_value)

        self.__table.add(state_symbol)
        self.__table.add(else_state_symbol)

        code+=standardizeStr(if_code,tag_body,1)
        code+= standardizeStr(state_code,if_state_tag,2)
        code+= standardizeStr(else_code, tag_body,1)
        code += standardizeStr(else_state_code, else_state_tag,2)
        code+= standardizeStr(if_end_code, tag_body,1)
        code += END
        # print(code)
        return code


    def for_stm(self):
        self.flushSet()
        code = self.stm(3,4,3)

        init = self.assigned_set.pop()
        condition = self.assigned_set.pop()
        state = self.assigned_set.pop()
        self.assigned_set.add(init)
        self.assigned_set.add(state)
        self.assigned_set.add(condition)

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
        for_tag = tag_safe
        state_tag = tag_safe

        # for赋值语句unsafe
        if init_symbol.getType()==TYPE_UINT and init_value<=0:
            for_tag = tag_unsafe
            init_value += OVERFLOW_NUM
            differ_value = compare_value - init_value

        # for循环条件完结
        if differ_value<=0:
            state_tag = tag_body
            compare_value = init_value
        # 执行了for循环
        else:
            state_value -= differ_value
            if state_symbol.getType() == TYPE_UINT and state_value <= 0:
                state_value += OVERFLOW_NUM
                state_tag = tag_unsafe
        state_symbol.setValue(state_value)
        init_symbol.setValue(compare_value)

        self.__table.add(init_symbol)
        self.__table.add(state_symbol)
        code += standardizeStr(for_start_code, for_tag,1)
        code += standardizeStr(for_state_code, state_tag,2)
        code += standardizeStr(for_end_code, tag_body,1)
        code += END
        # print(code)
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
        func_list = [self.nomal_stm, self.while_stm, self.if_stm, self.for_stm]
        for i in range(num):
            codePath = fileName+'/code_'+ str(i)+'.c'
            func = func_list[i% len(func_list)]
            with open(codePath,'w') as fileStream:
                fileStream.write(func())




if __name__ == '__main__':
    ge = Generator()
    ge.getData('D:/python_program/test/',10)
    # for i in range(10):
    #     print(ge.nomal_stm())
    #     ge.print_value_table()

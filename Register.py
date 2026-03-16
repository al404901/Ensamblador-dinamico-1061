class Register:
    def __init__(self):
        self.value = 0.0
        self.tag= None
        self.busy = False

    def update(self, new_value, tag):
        if self.busy and self.tag==tag:
            self.value = new_value
            self.busy = False
            self.tag = None

class RegisterBank:
    def __init__(self):
        self.float_regs ={}
        self.int_regs ={}
        for i in range(16):
            int_name='r'+str(i)
            float_name='f'+str(i)
            new_int_register=Register()
            new_float_register =Register()
            self.int_regs[int_name] = new_int_register
            self.float_regs[float_name]=new_float_register

    def getRegister(self, name: str) -> Register:
        if name[0] =='r':
            return self.int_regs[name]
        elif name[0]=='f':
            return self.float_regs[name]
        else:
            raise ValueError(f'{name}: Invalid register name or out of range')

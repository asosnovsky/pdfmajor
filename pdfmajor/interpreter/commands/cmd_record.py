
class CmdRecord:
    def __init__(self, file_name: str = "./cmd_record"):
        self.file = open(file_name, 'w')
        self.file.write("c_name,func_name,args\n")
    def write(self, c_name, func_name, args):
        self.file.write(f"{c_name},{func_name},{args}\n")
    def close(self):
        self.file.close()

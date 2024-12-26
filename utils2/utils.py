class Utils:
    def __init__(self, path):
        """初始化 Person 对象"""
        self.name = path
    def greet(self):
        """打印问候语"""
        return f"你好，我叫 {self.name}，我 {self.age} 岁。"

    def have_birthday(self):
        """年龄加一"""
        self.age += 1
        print(f"生日快乐！现在你 {self.age} 岁了。")
import configparser
import os


class ReadConfig(object):
    """
    定义一个读取配置文件的类
    """

    def __init__(self, filepath=None):
        if filepath:
            cf_path = filepath
        else:
            # 获取当前文件所在目录的上一级目录，即项目所在目录E:/xd_api_test
            root_dir = os.path.dirname(os.path.abspath('.'))
            cf_path = os.path.join(root_dir, "config.ini")
        self.cf = configparser.ConfigParser()
        self.cf.read(cf_path)

    def get_db(self, sections, param):
        value = self.cf.get(sections, param)
        return value


if __name__ == '__main__':
    test = ReadConfig()
    print(test.get_db("Mysql-Database", "host"))

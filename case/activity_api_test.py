# coding = utf-8
import json
import time
from datetime import datetime
from util.db_util import MysqlDb
from util.request_util import RequestUtil
from util.send_mail import SendMail


class ActivityTestCase(object):
    def loadAllCaseByApp(self, app):
        """
        根据app加载全部测试用例
        @param app:
        @return:
        """
        my_db = MysqlDb()
        sql = "select * from `case` where app ='{0}'".format(app)
        results = my_db.query(sql)
        return results

    def findCaseById(self, case_id):
        """
        根据id找用例
        @param case_id:
        @return:
        """
        my_db = MysqlDb()
        sql = "select * from `case` where id ='{0}'".format(case_id)
        results = my_db.query(sql, state="one")
        return results

    def loadconfigByAppAndKey(self, app, key):
        """
        根据app和key加载配置
        @param app:
        @param key:
        @return:
        """
        my_db = MysqlDb()
        sql = "select * from `config` where app ='{0}' and dict_key='{1}' ".format(app, key)
        # print(sql)
        results = my_db.query(sql, state="one")
        return results

    def updateResultByCaseId(self, response, is_pass, msg, case_id):
        """
        根据用例id，更新响应内容和测试内容
        @param response:
        @param is_pass:
        @param msg:
        @param case_id:
        @return:
        """
        my_db = MysqlDb()
        current_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        # print(current_time)
        if is_pass:
            sql = "update `case` set response='{0}',pass='{1}',msg='{2}',update_time='{3}' where id={4}".format("",
                                                                                                                is_pass,
                                                                                                                msg,
                                                                                                                current_time,
                                                                                                                case_id)
        else:
            sql = "update `case` set response=\"{0}\",pass='{1}',msg='{2}',update_time='{3}' where id={4}".format(
                str(response), is_pass, msg, current_time, case_id)
        rows = my_db.execute(sql)
        return rows

    def runAllcase(self, app):
        """
        执行全部用例的入口
        @param app:
        @return:
        """
        # print("runAllcase")

        # 获取全部测试用例
        results = self.loadAllCaseByApp(app)

        for case in results:
            print(case)
            if case["run"] == "yes":
                try:
                    # 获取接口域名
                    # api_host_obj = None
                    if case["platform"] == "dianping":
                        api_host_obj = self.loadconfigByAppAndKey(app, "host_dp")
                    elif case["platform"] == "meituan":
                        api_host_obj = self.loadconfigByAppAndKey(app, "host_mt")
                    # 执行用例
                    # print(api_host_obj)
                    response = self.runCase(case, api_host_obj)
                    # 响应断言
                    assert_msg = self.assertResponse(case, response)
                    # 更新结果储存数据库
                    rows = self.updateResultByCaseId(response, assert_msg['is_pass'], assert_msg['msg'], case['id'])
                    print("更新结果：rows={0}".format(str(rows)))
                except Exception as e:
                    print("用例编号：{0}, 用例标题：{1}, 执行保存：{2}".format(case["id"], case["title"], e))

        # 发送测试报告
        self.sendTestPeport(app)

    def runCase(self, case, api_host_obj):
        """
        执行单个用例
        @param case:
        @param api_host_obj:
        @return:
        """
        # print("runCase")
        headers = json.loads(case["headers"])
        body = json.loads(case["request_body"])
        method = case["method"]
        url = api_host_obj["dict_value"] + case["url"]
        # 是否有前置条件
        if case["pre_case_id"] > -1:
            print("有前置条件")
            pre_case_id = case["pre_case_id"]
            pre_case = self.findCaseById(pre_case_id)
            # 递归调用
            pre_response = self.runCase(pre_case, api_host_obj)
            # 前置条件断言
            pre_assert_msg = self.assertResponse(pre_case, pre_response)
            if not pre_assert_msg["is_pass"]:
                # 前置条件不通过，直接返回
                pre_response["msg"] = "前置条件不通过——" + pre_response["msg"]
                return pre_response
            # 判断需要case前置条件的是哪个字段
            pre_fields = json.loads(case["pre_fields"])
            for pre_field in pre_fields:
                # print(pre_field)
                if pre_field["scope"] == "header":
                    # 遍历headers，替换对应的字段值，即寻找同名的字段
                    for header in headers:
                        field_name = pre_field["field"]
                        if header == field_name:
                            field_value = pre_response["data"][field_name]
                            headers[field_name] = field_value
                elif pre_field["scope"] == "body":
                    print("替换body")
        print(headers)
        # 发起请求
        req = RequestUtil()
        if method == "post":
            content_type = headers["Content-Type"]
            response = req.request(url, method, headers=headers, param=body, content_type=content_type)
            return response
        else:
            response = req.request(url, method, headers=headers, param=body)
            return response



    def assertResponse(self, case, response):
        """
        断言响应内容，更新用例执行情况
        @param case:
        @param response:
        @return:
        """
        # print("assertResponse")
        assert_type = case["assert_type"]
        expect_result = case["expect_result"]
        is_pass = False
        if assert_type == "code":
            response_code = response["code"]
            if int(expect_result) == response_code:
                is_pass = True
                print("测试通过")
            else:
                print("测试不通过")
                is_pass = False
        elif assert_type == "data_json_array":
            data_array = response["data"]
            if data_array is not None and isinstance(data_array, list) and len(data_array) > int(expect_result):
                is_pass = True
                print("测试通过")
            else:
                print("测试不通过")
                is_pass = False
        elif assert_type == "data_json":
            data = response["data"]
            if data is not None and isinstance(data, dict) and len(data) > int(expect_result):
                is_pass = True
                print("测试通过")
            else:
                print("测试不通过")
                is_pass = False
        elif assert_type == "code&data_json":
            response_code = response["code"]
            data = response["data"]
            if int(expect_result) == response_code:
                if data is not None and isinstance(data, dict) and len(data) > 0:
                    is_pass = True
                    print("测试通过")
                else:
                    print("测试不通过")
                    is_pass = False
            else:
                print("测试不通过")
                is_pass = False
        elif assert_type == "code&data_json_array":
            response_code = response["code"]
            data_array = response["data"]
            if int(expect_result) == response_code:
                if data_array is not None and isinstance(data_array, list) and len(data_array) > 0:
                    is_pass = True
                    print("测试通过")
                else:
                    print("测试不通过")
                    is_pass = False
            else:
                print("测试不通过")
                is_pass = False

        msg = "模块:{0}, 标题:{1}, 平台:{2}, 断言类型是:{3}, 响应msg:{4}".format(case["module"], case["title"], case["platform"],
                                                                    case["assert_type"], response["msg"])
        # 拼装信息
        assert_msg = {"is_pass": is_pass, "msg": msg}
        return assert_msg

    def sendTestPeport(self, app):
        """
        发送邮件，测试报告
        @param app:
        @return:
        """
        # print("sendTestPeport")
        # 加载全部用例
        results = self.loadAllCaseByApp(app)
        content = """
        <html><body>
            <h3>{0} 接口测试报告：</h3>
            <h4>pass用例</h4>
            <table border="1">
            <tr>
              <th>编号</th>
              <th>模块</th>
              <th>标题</th>
              <th>是否通过</th>
              <th>备注</th>
              <th>响应</th>
            </tr>
            {1}
            </table>
            <h4>fail用例</h4>
            <table border="1">
            <tr>
              <th>编号</th>
              <th>模块</th>
              <th>标题</th>
              <th>是否通过</th>
              <th>备注</th>
              <th>响应</th>
            </tr>
            {2}
            </table>
            </body></html>  
        """
        template_true = ""
        template_false = ""
        for case in results:
            if case["pass"] == str(True):
                template_true += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>".format(
                    case['id'], case['module'], case['title'], case['pass'], case['msg'], case['response'])
            elif case["pass"] == str(False):
                template_false += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>".format(
                    case['id'], case['module'], case['title'], case['pass'], case['msg'], case['response'])
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        content = content.format(current_time, template_true, template_false)
        mail_host = self.loadconfigByAppAndKey(app, "mail_host")["dict_value"]
        mail_title = self.loadconfigByAppAndKey(app, "mail_title")["dict_value"]
        mail_sender = self.loadconfigByAppAndKey(app, "mail_sender")["dict_value"]
        mail_auth_code = self.loadconfigByAppAndKey(app, "mail_auth_code")["dict_value"]
        mail_receivers = self.loadconfigByAppAndKey(app, "mail_receivers")["dict_value"]
        mail = SendMail(mail_host)
        mail.send(mail_title, content, mail_sender, mail_auth_code, mail_receivers)


if __name__ == '__main__':
    # print("main")
    test = ActivityTestCase()
    # results = test.loadAllCaseByApp("商业活动")

    # results = test.findCaseById(1)

    # results = test.loadconfigByAppAndKey("商业活动","host_dp")
    # print(results)

    test.runAllcase("商业活动")

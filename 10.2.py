import pymysql
import time


# ====================== 登录验证模块 ======================
def login_system():
    """系统登录功能（关联 company2.user 表）"""
    print("\n" + "=" * 30)
    print("    欢迎使用学生信息管理系统")
    print("=" * 30)

    while True:
        username = input("请输入用户名（输入0退出）：").strip()
        if username == '0':
            return None  # 返回None表示主动退出

        password = input("请输入密码：").strip()

        try:
            # 连接 company2 数据库验证身份
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="root123456",
                database="company2",  # 复用之前的用户表数据库
                charset="utf8mb4"
            )
            with conn.cursor() as cursor:
                # 查询用户名和密码是否匹配
                sql = "SELECT * FROM users WHERE username = %s AND password = %s"
                cursor.execute(sql, (username, password))
                user = cursor.fetchone()

                if user:
                    print(f"\n✅ 登录成功！欢迎，{username}！")
                    conn.close()
                    return username  # 登录成功，返回用户名
                else:
                    print("❌ 用户名或密码错误，请重新输入！\n")
            conn.close()
        except Exception as e:
            print(f"❌ 登录验证异常: {e}")
            return None


# ====================== 学生管理核心类 ======================
class StudentManager:
    # 初始化数据库连接
    def __init__(self, current_user):
        self.current_user = current_user  # 记录当前登录的操作员
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",
                password="root123456",
                database="student_db",  # 学生数据库
                charset="utf8mb4",
                autocommit=False
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            print("✅ 学生数据库连接成功")
        except Exception as e:
            print("❌ 数据库连接失败：", e)

    # 日志记录工具（升级：记录操作人）
    def write_log(self, msg):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("student_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] [操作员:{self.current_user}] {msg}\n")

    # 1. 添加学生信息 + 录入成绩
    def add_student(self, stu_id, name, age, major, chinese, math, english):
        try:
            sql_stu = "INSERT INTO student(stu_id, name, age, major) VALUES(%s,%s,%s,%s)"
            self.cursor.execute(sql_stu, (stu_id, name, age, major))

            sql_score = "INSERT INTO student_score(stu_id, chinese, math, english) VALUES(%s,%s,%s,%s)"
            self.cursor.execute(sql_score, (stu_id, chinese, math, english))

            self.conn.commit()
            print("✅ 学生信息及成绩添加成功")
            self.write_log(f"新增学生：学号{stu_id} 姓名{name}")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 添加失败！学号重复或数据格式错误. 详情: {e}")

    # 2. 查看所有学生
    def show_all_student(self):
        sql = """
        SELECT s.stu_id, s.name, s.age, s.major, sc.chinese, sc.math, sc.english
        FROM student s
        LEFT JOIN student_score sc ON s.stu_id = sc.stu_id
        """
        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        if not res:
            print("暂无学生数据！")
            return

        print("\n========== 学生完整信息及成绩列表 ==========")
        for item in res:
            c = item["chinese"] or 0
            m = item["math"] or 0
            e = item["english"] or 0
            total = c + m + e
            avg = total / 3

            print(f"学号：{item['stu_id']} | 姓名：{item['name']} | 年龄：{item['age']} | 专业：{item['major']}")
            print(f"语文：{c} | 数学：{m} | 英语：{e} | 总分：{total} | 平均分：{avg:.1f}")
            print("-" * 90)

    # 3. 按学号精准查询
    def search_score_by_id(self, stu_id):
        sql = """
        SELECT s.stu_id, s.name, s.age, s.major, sc.chinese, sc.math, sc.english
        FROM student s
        LEFT JOIN student_score sc ON s.stu_id = sc.stu_id
        WHERE s.stu_id = %s
        """
        self.cursor.execute(sql, (stu_id,))
        res = self.cursor.fetchone()

        if res:
            c = res["chinese"] or 0
            m = res["math"] or 0
            e = res["english"] or 0
            total = c + m + e
            avg = total / 3

            print("\n========== 学生成绩详情 ==========")
            print(f"学号：{res['stu_id']} | 姓名：{res['name']} | 年龄：{res['age']} | 专业：{res['major']}")
            print(f"语文：{c} | 数学：{m} | 英语：{e} | 总分：{total} | 平均分：{avg:.1f}")
        else:
            print("❌ 未查询到该学生信息！")

    # 4. 修改学生基础信息
    def update_student_info(self, stu_id, new_age, new_major):
        try:
            sql = "UPDATE student SET age=%s, major=%s WHERE stu_id=%s"
            self.cursor.execute(sql, (new_age, new_major, stu_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("✅ 学生基础信息修改成功")
                self.write_log(f"修改学生基础信息：学号{stu_id}")
            else:
                print("❌ 未找到该学生")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 修改失败: {e}")

    # 5. 单独修改学生成绩
    def update_student_score(self, stu_id, c, m, e):
        try:
            sql = "UPDATE student_score SET chinese=%s, math=%s, english=%s WHERE stu_id=%s"
            self.cursor.execute(sql, (c, m, e, stu_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("✅ 学生成绩修改成功")
                self.write_log(f"修改学生成绩：学号{stu_id}")
            else:
                print("❌ 未找到该学生成绩数据")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 成绩修改失败: {e}")

    # 6. 删除学生信息（级联删除成绩）
    def delete_student(self, stu_id):
        try:
            sql = "DELETE FROM student WHERE stu_id=%s"
            self.cursor.execute(sql, (stu_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("✅ 学生信息及对应成绩已全部删除")
                self.write_log(f"删除学生数据：学号{stu_id}")
            else:
                print("❌ 未找到该学生")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 删除失败: {e}")

    # 关闭数据库连接
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("✅ 数据库连接已关闭")


# ====================== 主菜单流程 ======================
def main():
    # 第一步：登录验证
    current_user = login_system()

    # 如果用户输入0退出，则直接结束程序
    if not current_user:
        print("👋 已退出系统，再见！")
        return

    # 第二步：登录成功，初始化学生管理对象，并传入当前操作员
    sm = StudentManager(current_user)

    # 第三步：进入学生管理主菜单
    while True:
        print(f"\n======= 学生信息成绩管理系统【当前用户：{sm.current_user}】=======")
        print("1. 添加学生（含成绩录入）")
        print("2. 查看所有学生完整信息")
        print("3. 按学号查询学生成绩")
        print("4. 修改学生基础信息")
        print("5. 修改学生成绩信息")
        print("6. 删除学生（含成绩）")
        print("0. 退出系统")
        print("=" * 50)

        choice = input("请输入功能编号：")

        if choice == "1":
            sid = input("请输入学生学号：")
            name = input("请输入学生姓名：")
            age = input("请输入学生年龄：")
            major = input("请输入所学专业：")
            try:
                c = int(input("请输入语文成绩："))
                m = int(input("请输入数学成绩："))
                e = int(input("请输入英语成绩："))
                sm.add_student(sid, name, age, major, c, m, e)
            except ValueError:
                print("❌ 成绩必须输入数字！")

        elif choice == "2":
            sm.show_all_student()

        elif choice == "3":
            sid = input("请输入查询学号：")
            sm.search_score_by_id(sid)

        elif choice == "4":
            sid = input("请输入要修改的学号：")
            age = input("请输入新年龄：")
            major = input("请输入新专业：")
            sm.update_student_info(sid, age, major)

        elif choice == "5":
            sid = input("请输入要修改成绩的学号：")
            try:
                c = int(input("请输入新语文成绩："))
                m = int(input("请输入新数学成绩："))
                e = int(input("请输入新英语成绩："))
                sm.update_student_score(sid, c, m, e)
            except ValueError:
                print("❌ 成绩必须输入数字！")

        elif choice == "6":
            sid = input("请输入要删除的学号：")
            sm.delete_student(sid)

        elif choice == "0":
            sm.close()
            print("👋 系统退出成功，再见！")
            break

        else:
            print("❌ 输入无效，请输入0-6的数字！")


if __name__ == "__main__":
    main()

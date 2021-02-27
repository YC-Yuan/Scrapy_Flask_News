from utils.snowflake import MySnow

if __name__ == '__main__':
    snowflake = MySnow(dataID=00)  # 数据表编号
    snowflake.get_id()
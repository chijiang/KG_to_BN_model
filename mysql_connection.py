from functools import wraps
import pymysql
import copy
import pandas as pd

class MySqlManip():
    def __init__(self, 
                 host:str = "localhost" , 
                 port: int = 3306, 
                 user: str = "",
                 password: str = "",
                 database: str = "IOT") -> None:
        self.conn = pymysql.connect(
            user = user, 
            host = host, 
            port = port, 
            passwd = password, 
            database = database)
        self.database = database
    
    def connection(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.conn.connect()
            ret = func(self, *args, **kwargs)
            self.conn.commit()
            self.conn.close()
            return ret
        return wrapper
    
    @connection
    def create_params_table(self, table:str = 'ml_params_table'):
        with self.conn.cursor() as cur:
            cur.execute(f'''
            CREATE TABLE IF NOT EXISTS `{self.database}`.`{table}` (
            `ID` int NOT NULL AUTO_INCREMENT,
            `Name` varchar(255) NOT NULL unique,
            PRIMARY KEY (`ID` DESC)
            );'''
        )
    
    @connection
    def fetch(self, query):
        with self.conn.cursor() as cur:
            cur.execute(query)
            data = cur.fetchall()
            column_des = cur.description
            column_names = [column_des[i][0] for i in range(len(column_des))]
        return data, column_names

    @connection
    def insert(self, query):
        with self.conn.cursor() as cur:
            cur.execute(query)
            
    def make_model_table(self, table_name: str = "ml_data_bubble", param_columns: list = [], target_colums: list = []):
        # insert paramters into table
        all_params = copy.copy(param_columns)
        all_params.extend(target_colums)

        query = 'INSERT IGNORE INTO `IOT`.`ml_params_table` (Name) VALUES ("{params}");'
        query = query.format(params = '"),("'.join(all_params))
        self.insert(query)

        data, _ = self.fetch(f'''SELECT ID FROM `IOT`.`ml_params_table` WHERE Name in ("{'","'.join(param_columns)}")''')
        ids = [str(x[0]) for x in data]
        param_ids = "` varchar(255) NULL, `".join(ids)
        
        data, _ = self.fetch(f'''SELECT ID FROM `IOT`.`ml_params_table` WHERE Name in ("{'","'.join(target_colums)}")''')
        ids = ["target_"+str(x[0]) for x in data]
        target_ids = "` varchar(255) NULL, `".join(ids)
            
        query = f'''
        CREATE TABLE IF NOT EXISTS `{self.database}`.`{table_name}` (
        `ID` int NOT NULL AUTO_INCREMENT,
        `BatchNr` varchar(255) NULL,
        `StartTime` varchar(255) NULL,
        `EndTime` varchar(255) NULL,
        `Factory` varchar(255) NULL,
        `ProductLine` varchar(255) NULL,
        `Product` varchar(255) NULL,
        `{param_ids}` varchar(255) NULL,
        `{target_ids}` varchar(255) NULL,
        PRIMARY KEY (`ID` DESC)
        );'''
        self.insert(query)
        
    def load_data_to_dataframe(self, table_name: str, columns: list[str] = [], where: dict = {}):
        query_columns = "*" if not columns else "`" + "`, `".join(columns) + "`"
        query = f'''SELECT {query_columns} FROM {table_name}'''
        if where:
            where_info = [f"`{name}`=\"{value}\"" for name, value in where.items()]
            query += f''' WHERE {" AND ".join(where_info)}'''
        data, column_names = self.fetch(query)

        dataframe = pd.DataFrame([list(x) for x in data], columns = column_names)
        return dataframe
        


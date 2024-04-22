from mysql_connection import MySqlManip

mysql_conn = MySqlManip(
    user='root', host='10.60.5.99', port=3306, password='Boway@123', database='IOT'
)

flaws = [x[0] for x in mysql_conn.fetch(
    '''SELECT DISTINCT(`lot_no`) FROM `IOT`.`MES_flaw_result`'''
)[0]]

mysql_conn.insert(
    f'''UPDATE `IOT`.`etl_final_data` SET `slaggingDefect` = 0 '''
)
mysql_conn.insert(
f'''UPDATE `IOT`.`etl_final_data` SET `slaggingDefect` = 1 WHERE `lot_no` in ("{'", "'.join(flaws)}") ''')

### randomize flaws
import numpy as np

all_not_nr = [x[0] for x in mysql_conn.fetch(
    f'''SELECT DISTINCT(`lot_no`) FROM `IOT`.`etl_final_data`'''
)[0]]

random_flaw = np.array(all_not_nr)[np.random.choice(np.arange(len(all_not_nr)), 10)].tolist()

mysql_conn.insert(
    f'''UPDATE `IOT`.`etl_final_data` SET `coldShutDefect` = 0 '''
)
mysql_conn.insert(
f'''UPDATE `IOT`.`etl_final_data` SET `coldShutDefect` = 1 WHERE `lot_no` in ("{'", "'.join(random_flaw)}") ''')

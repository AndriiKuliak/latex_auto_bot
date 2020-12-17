import sqlite3

import config
import user_info
from logger import logger

TABLE_NAME = 'user_status'

class DBProxy:
    def __init__(self):
        db_connection = None

        try:
            db_connection = sqlite3.connect(config.DATABASE_FILE)
            logger.debug('Trying to establish connection to DB...')
            logger.info('Successfully connected to DB')

            self.__check_db_consistency(db_connection)

        except sqlite3.Error as e:
            logger.error('Cannot connect to DB: %s' % e)
        
        finally:
            if (db_connection):
                db_connection.close()

    def __check_db_consistency(self, db_connection):
        logger.debug('Checking DB consistency...')
        
        cursor = db_connection.cursor()
        result = cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}'").fetchone()
        if result is None:
            logger.info('Initializing DP structure...')

            cursor.execute(f"""CREATE TABLE {TABLE_NAME}
                               (user_id integer, last_state integer, last_message_time integer)
                            """)
            db_connection.commit()

    def __add_new_user(self, current_user_info, db_connection):
        query = f"INSERT INTO {TABLE_NAME} VALUES (?,?,?)"

        cursor = db_connection.cursor()
        cursor.execute(query, (current_user_info.user_id, current_user_info.last_state.value, current_user_info.last_message_time))

        db_connection.commit()


    def __check_user_availability(self, current_user_info, db_connection):
        query = f"SELECT * FROM {TABLE_NAME} WHERE user_id=?"

        result = False

        cursor = db_connection.cursor()
        cursor.execute(query, [(current_user_info.user_id)])
        result = cursor.fetchone() is None

        return result
    
    def get_user_info(self, current_user_info):
        query = f"SELECT * FROM {TABLE_NAME} WHERE user_id=?"

        ret_val = None
        db_connection = None

        try:
            db_connection = sqlite3.connect(config.DATABASE_FILE)

            cursor = db_connection.cursor()
            cursor.execute(query, [(current_user_info.user_id)])
            result = cursor.fetchone()

            if result is None:
                logger.warning('New user deceted, registering...')
                self.__add_new_user(current_user_info, db_connection)
                ret_val = current_user_info
            else:
                ret_val = user_info.UserInfo(result[0], result[1], result[2])

        except sqlite3.Error as e:
            logger.error('An error occured: %s' % e)
        
        finally:
            if (db_connection):
                db_connection.close()

        return ret_val

    def set_user_info(self, current_user_info):
        db_connection = None

        try:
            db_connection = sqlite3.connect(config.DATABASE_FILE)

            is_user_available = self.__check_user_availability(current_user_info, db_connection)
            if is_user_available == True:
                self.__add_new_user(user_info, db_connection)    
            else:
                query = f"""UPDATE {TABLE_NAME}
                        SET last_state = {current_user_info.last_state.value},
                            last_message_time = {current_user_info.last_message_time}
                        WHERE user_id = {current_user_info.user_id}
                     """
                cursor = db_connection.cursor()
                cursor.execute(query)

                db_connection.commit()

        except sqlite3.Error as e:
            logger.error('An error occured: %s' % e)
        
        finally:
            if (db_connection):
                db_connection.close()


if __name__ == "__main__":
    proxy = DBProxy()

    print(proxy.get_user_info(user_info.UserInfo(1, 1, 12345)))

    proxy.set_user_info(user_info.UserInfo(1, 3, 12345))

    print(proxy.get_user_info(user_info.UserInfo(1, 1, 0)))

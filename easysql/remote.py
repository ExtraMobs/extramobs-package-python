from dataclasses import fields
from getpass import getpass
import pprint
from typing import Any, Dict, Generator, List, Type, TypeVar

import pyodbc

from .dto_validator import StrictMode, DTOValidator

T = TypeVar("T")


class ConnectionDatabase:
    __username: str
    __password: str
    __target_database: str
    __connection_address: str
    __sql_conn: pyodbc.Connection | None
    __driver_name: str | None

    def __init__(
        self,
        driver_name: str,
        login: str,
        password: str,
        connection_adress: str,
        target_database: str,
    ) -> None:
        self.sql_conn = None

        self.driver_name = driver_name
        self.login = login
        self.password = password
        self.connection_address = connection_adress
        self.target_database = target_database

    def connect(self) -> None:
        if self.__sql_conn is not None and not self.__sql_conn.closed:
            self.__sql_conn.close()

        self.__sql_conn = pyodbc.connect(self.__connection_string)

    def execute_query_to_dto(
        self,
        dto_target: Type[T],
        query: str,
        strict: Any = StrictMode.FULL_STRICT,
        params: Dict[str, object] | None = None,
    ) -> List[T]:
        return list(
            self.execute_query_to_dto_generator(dto_target, query, strict, params)
        )

    def execute_query_to_dto_generator(
        self,
        dto_target: Type[T],
        query: str,
        strict: Any = StrictMode.FULL_STRICT,
        params: List[Any] | None = None,
    ) -> Generator[T]:

        dto_fields = {f.name: f.type for f in fields(dto_target)}
        parsed_mode = StrictMode.parse(strict)
        
        for dict_object in self.execute_query_generator(query, params):
            DTOValidator.process(dict_object, dto_fields, parsed_mode)
            yield dto_target(**dict_object)

    def execute_query(
        self, query: str, params: Dict[str, object] | None = None
    ) -> Dict[str, object]:
        return list(self.execute_query_generator(query, params))

    def execute_query_generator(
        self, query: str, params: List[Any] | None = None
    ) -> Generator[Dict[str, object]]:
        self.connect()

        cursor = self.sql_conn.execute(query, () if params is None else params)

        try:
            while (row := cursor.fetchone()) is not None:
                col_names = [col[0] for col in row.cursor_description]
                yield dict(zip(col_names, row))
        finally:
            cursor.close()

    @staticmethod
    def from_request_login(
        connection_adress: str = None,
        target_database: str = None,
        driver_name: str = "SQL Server Native Client 11.0",
    ):
        return ConnectionDatabase(
            login=input("Login database: "),
            password=getpass("Password database: ", echo_char="*"),
            connection_adress=connection_adress,
            target_database=target_database,
            driver_name=driver_name,
        )

    @property
    def __connection_string(self):
        return (
            f"Server={self.connection_address};"
            f"Database={self.target_database};"
            f"uid={self.login};"
            f"pwd={self.password};"
            f"TrustServerCertificate=yes;"
            f"Driver={self.driver_name}"
        )

    @property
    def login(self) -> str:
        return self.__username

    @login.setter
    def login(self, value: str) -> None:
        self.__username = value

    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, value: str) -> None:
        self.__password = value

    @property
    def target_database(self) -> str:
        return self.__target_database

    @target_database.setter
    def target_database(self, value: str) -> None:
        self.__target_database = value

    @property
    def connection_address(self) -> str:
        return self.__connection_address

    @connection_address.setter
    def connection_address(self, value: str) -> None:
        self.__connection_address = value

    @property
    def sql_conn(self) -> pyodbc.Connection:
        if self.__sql_conn is None:
            self.connect()
        return self.__sql_conn

    @sql_conn.setter
    def sql_conn(self, value: pyodbc.Connection) -> None:
        self.__sql_conn = value

    @property
    def driver_name(self) -> str:
        return self.__driver_name

    @driver_name.setter
    def driver_name(self, value: str) -> None:
        self.__driver_name = value

from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime
# pylint:disable=wildcard-import,unused-wildcard-import
from dateutil.relativedelta import *
import jwt

from ._extensions import Config


class BaseAuthentication(ABC):
    # pylint:disable=missing-class-docstring
    @abstractmethod
    def create_token(self, extensions: Config, exp: int, **kwargs):
        # pylint:disable=missing-function-docstring
        pass

    @abstractmethod
    def update_token(self, extensions: Config, exp: int, table_name, **kwarg):
        # pylint:disable=missing-function-docstring
        pass

    @abstractmethod
    def encode_token(self, extensions: Config, entity_id: Any, exp: int, table_name: str):
        # pylint:disable=missing-function-docstring
        pass


class Authentication(BaseAuthentication):
    """
        Uses SHA-256 hash algorithm
    """
    #: The reference to the entity key. Defaulted to `id`.
    # See :class:`~flask_jwt_router._extensions` for more information.
    entity_key: str = "id"

    #: The reference to the entity key.
    #: See :class:`~flask_jwt_router._extensions` for more information.
    secret_key: str = None

    #: The reference to the entity ID.
    entity_id: str = None

    def __init__(self):
        # pylint:disable=useless-super-delegation
        super(Authentication, self).__init__()

    def encode_token(self, extensions: Config, entity_id: Any, exp: int, table_name) -> str:
        """
        :param extensions: See :class:`~flask_jwt_router._extensions`
        :param entity_id: Normally the primary key `id` or `user_id`
        :param exp: The expiry duration set when encoding a new token
        :param table_name: The Model Entity `__tablename__`
        :return: str
        """
        self.entity_key = extensions.entity_key
        self.secret_key = extensions.secret_key
        # pylint: disable=line-too-long
        encoded = jwt.encode({
            "table_name": table_name,
            self.entity_key: entity_id,
            # pylint: disable=no-member
            "exp": datetime.utcnow() + relativedelta(days=+exp)
        }, self.secret_key, algorithm="HS256").decode("utf-8")
        return encoded

    def create_token(self, extensions: Config, exp: int, **kwargs) -> str:
        """
        kwargs:
            - entity_id: Represents the entity's primary key
            - table_name: The table name of the entity
        :param extensions: See :class:`~flask_jwt_router._extensions`
        :param exp: The expiry duration set when encoding a new token
        :param kwargs:
        :return: Union[str, None]
        """
        self.entity_id = kwargs.get("entity_id", None)
        table_name = kwargs.get("table_name", None)
        return self.encode_token(extensions, self.entity_id, exp, table_name)

    def update_token(self,
                     extensions: Config,
                     exp: int,
                     table_name: str,
                     **kwargs,
                     ) -> str:
        """
        :param extensions:
        :param exp:
        :param table_name:
        :param kwargs:
        :return: Union[str, None]
        """
        self.entity_id = kwargs.get("entity_id", None)
        return self.encode_token(extensions, self.entity_id, exp, table_name)

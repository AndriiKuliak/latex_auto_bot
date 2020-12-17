import os
from abc import ABC, abstractmethod

from google.cloud import secretmanager

import config
from logger import logger

class SecurityManagerProxyBase(ABC):
    @abstractmethod
    def get_bot_auth_token(self):
        raise NotImplementedError

class GoogleCloudSecurityProxy(SecurityManagerProxyBase):
    def __init__(self):
        logger.debug("GoogleCloudSecurityProxy cretion")
        super().__init__()
        self._sec_mgr_proxy = secretmanager.SecretManagerServiceClient()

    def get_bot_auth_token(self):
        gproject_id = int(os.environ.get('GCP_PROJECT'))

        bot_secret_payload = self._get_secret_info(gproject_id, config.BOT_API_SECRET_NAME)

        return bot_secret_payload.data.decode()

    def _get_secret_info(self, project_id, secret_id):
        secret_full_name = "projects/{}/secrets/{}/versions/latest".format(project_id, secret_id)

        logger.info("Requesting secret '{}'".format(secret_full_name))
        secret_info = self._sec_mgr_proxy.access_secret_version(request={"name": secret_full_name})
        logger.info("Successfully requested secret")

        return secret_info.payload


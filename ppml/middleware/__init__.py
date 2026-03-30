import ppml.services as S
from xolo.client import XoloClient
from fastapi import Depends
from ppml.repositories import UsersProfilesRepository
import ppml.config as Cfg
def get_xolo_client()->XoloClient:
    return XoloClient(
        api_url= Cfg.XOLO_API_URL,
        secret= Cfg.XOLO_SECRET_KEY
    )


def get_users_service(xolo_client:S.XoloClient = Depends(get_xolo_client))->S.UsersService:
    repository = UsersProfilesRepository()
    return S.UsersService(repository=repository, xolo=xolo_client)
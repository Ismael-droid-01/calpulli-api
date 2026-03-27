from fastapi import APIRouter as Router,Depends
from fastapi import status



router = Router(prefix="/ppml")
@router.post("/run")
async def run():
    pass
    # res = await ppml_service.service1(request)
    # return res

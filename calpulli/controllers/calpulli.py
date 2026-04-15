from fastapi import APIRouter as Router,Depends
from fastapi import status



router = Router(prefix="/calpulli")
@router.post("/run")
async def run():
    pass

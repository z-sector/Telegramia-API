from fastapi import APIRouter, status, HTTPException, Body, Depends
from database import get_object, create_document, get_all_objects, update_object, delete_object
from schemas import AdminModel, UpdateAdminModel, ShowAdminModel
from typing import Optional, List
from hashing import Hash
from oauth2 import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['Admins']
)


@router.post('', response_description='Add new admin', response_model=AdminModel,
             status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminModel = Body(...), current_user: AdminModel = Depends(get_current_user)):
    admin.password = Hash.bcrypt(admin.password)
    return await create_document(admin, 'admins')


@router.get('s', response_description='List all admins', response_model=List[ShowAdminModel],
            status_code=status.HTTP_200_OK)
async def list_admins():
    admins = await get_all_objects('admins')
    return admins


@router.get('', response_description='Get a single admin', response_model=ShowAdminModel,
            status_code=status.HTTP_200_OK)
async def show_admin(identifier: Optional[str] = None, admin_name: Optional[str] = None):
    variables = locals()
    options = {'identifier': '_id', 'admin_name': 'name'}
    for key in variables.keys():
        if variables[key] is not None:
            return await get_object({options[key]: variables[key]}, 'admins')
    raise HTTPException(status_code=404, detail='Set some parameters')


@router.put('', response_description='Update an admin', response_model=UpdateAdminModel,
            status_code=status.HTTP_200_OK)
async def update_admin(identifier: Optional[str] = None, admin_name: Optional[str] = None,
                       admin: UpdateAdminModel = Body(...), current_user: AdminModel = Depends(get_current_user)):
    variables = locals()
    options = {'identifier': '_id', 'admin_name': 'name'}
    for key in variables.keys():
        if variables[key] is not None:
            return await update_object({options[key]: variables[key]}, admin, 'admins')
    raise HTTPException(status_code=404, detail='Set some parameters')


@router.delete('', response_description='Delete an admin',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(identifier: Optional[str] = None, admin_name: Optional[str] = None,
                       current_user: AdminModel = Depends(get_current_user)):
    variables = locals()
    options = {'identifier': '_id', 'admin_name': 'name'}
    for key in variables.keys():
        if variables[key] is not None:
            return await delete_object({options[key]: variables[key]}, 'admins')
    raise HTTPException(status_code=404, detail='Set some parameters')
"""Employee Routes - CRUD with Repository DI"""
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
from db.base import get_session
from db.repositories import EmployeeRepository
from db.dependencies import get_employee_repo

router = APIRouter()

@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(employee_in: EmployeeCreate, session: AsyncSession = Depends(get_session), employee_repo: EmployeeRepository = Depends(get_employee_repo)):
    try:
        result = await employee_repo.create(employee_in.dict())
        await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def read_employee(employee_id: UUID, session: AsyncSession = Depends(get_session), employee_repo: EmployeeRepository = Depends(get_employee_repo)):
    try:
        employee = await employee_repo.read(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Not found")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("", response_model=EmployeeListResponse)
async def list_employees(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: AsyncSession = Depends(get_session), employee_repo: EmployeeRepository = Depends(get_employee_repo)):
    try:
        items, total = await employee_repo.list(skip=skip, limit=limit)
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: UUID, employee_in: EmployeeUpdate, session: AsyncSession = Depends(get_session), employee_repo: EmployeeRepository = Depends(get_employee_repo)):
    try:
        employee = await employee_repo.update(employee_id, employee_in.dict(exclude_unset=True))
        if not employee:
            raise HTTPException(status_code=404, detail="Not found")
        await session.commit()
        return employee
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{employee_id}", status_code=204)
async def delete_employee(employee_id: UUID, session: AsyncSession = Depends(get_session), employee_repo: EmployeeRepository = Depends(get_employee_repo)):
    try:
        await employee_repo.delete(employee_id)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

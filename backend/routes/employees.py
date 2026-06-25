"""
Employee Routes - CRUD endpoints for employee (Service-integrated)
GET, POST, PUT, DELETE operations with business logic
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
from services.employee_service import EmployeeService
from db.base import get_session

router = APIRouter()

@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    employee_in: EmployeeCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new employee"""
    try:
        service = EmployeeService(session)
        employee = await service.create_employee(employee_in.dict())
        return employee
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating employee: {str(e)}")

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def read_employee(
    employee_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Get employee by ID"""
    try:
        service = EmployeeService(session)
        employee = await service.get_employee(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employee: {str(e)}")

@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List all employees with pagination"""
    try:
        service = EmployeeService(session)
        employees = await service.list_employees(skip=skip, limit=limit)
        return {"items": employees, "total": len(employees), "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing employees: {str(e)}")

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    employee_in: EmployeeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update employee"""
    try:
        service = EmployeeService(session)
        employee = await service.update_employee(employee_id, employee_in.dict(exclude_unset=True))
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating employee: {str(e)}")

@router.delete("/{employee_id}", status_code=204)
async def delete_employee(
    employee_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Delete employee (soft delete)"""
    try:
        service = EmployeeService(session)
        await service.delete_employee(employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting employee: {str(e)}")

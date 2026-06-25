"""
Employee Service — Employee contract validation, payroll logic
"""

from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import EmployeeRepository
from .base_service import BaseService, ServiceException


class EmployeeService(BaseService):
    """Service for employee operations"""

    def __init__(self, session: AsyncSession, employee_repo: EmployeeRepository):
        super().__init__(session, employee_repo)
        self.employee_repo = employee_repo

    async def create_employee(
        self,
        code_employe: str,
        departement_id: UUID,
        fonction_id: UUID,
        date_embauche: date = None,
        salaire_mensuel: Decimal = None
    ) -> dict:
        """
        Create new employee
        
        Args:
            code_employe: Unique employee code
            departement_id: Department UUID
            fonction_id: Function/Role UUID
            date_embauche: Hiring date
            salaire_mensuel: Monthly salary
            
        Returns:
            Created employee dict
            
        Raises:
            ServiceException if validation fails
        """
        try:
            # Validate code unique
            await self.validate_unique("code_employe", code_employe, "Employee")

            # Validate salary if provided
            if salaire_mensuel:
                self.validate_numeric(salaire_mensuel, min_val=0, field_name="salaire_mensuel")

            # Create employee
            employee = await self.employee_repo.create({
                "code_employe": code_employe,
                "departement_id": departement_id,
                "fonction_id": fonction_id,
                "date_embauche": date_embauche or date.today(),
                "salaire_mensuel": salaire_mensuel
            })

            await self.session.flush()

            self.log_operation(
                "create_employee",
                employee.id,
                {
                    "code_employe": code_employe,
                    "departement_id": departement_id
                }
            )

            return {
                "id": employee.id,
                "code_employe": employee.code_employe,
                "salaire_mensuel": str(employee.salaire_mensuel) if employee.salaire_mensuel else None
            }

        except ServiceException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating employee: {e}", exc_info=True)
            raise ServiceException(f"Failed to create employee: {str(e)}")

    async def calculate_net_salary(
        self,
        gross_salary: Decimal,
        deductions: Decimal = Decimal("0")
    ) -> Decimal:
        """
        Calculate net salary (gross - deductions)
        
        Args:
            gross_salary: Gross salary amount
            deductions: Total deductions (taxes, social, etc.)
            
        Returns:
            Net salary
            
        Raises:
            ServiceException if invalid
        """
        self.validate_numeric(gross_salary, min_val=0, field_name="gross_salary")
        self.validate_numeric(deductions, min_val=0, field_name="deductions")

        gross_salary = Decimal(str(gross_salary))
        deductions = Decimal(str(deductions))

        net = gross_salary - deductions

        if net < 0:
            raise ServiceException("Net salary cannot be negative (deductions exceed gross)")

        return net.quantize(Decimal("0.01"))

    async def is_employee_active(self, employee_id: UUID) -> bool:
        """
        Check if employee is active (hired but not terminated)
        
        Args:
            employee_id: Employee UUID
            
        Returns:
            True if active
        """
        employee = await self.employee_repo.read(employee_id)
        if not employee:
            return False

        # Active if no end date or end date is in future
        if not employee.date_fin_prevue:
            return True

        return employee.date_fin_prevue > date.today()

    async def terminate_employee(
        self,
        employee_id: UUID,
        end_date: date = None
    ) -> dict:
        """
        Terminate employee contract
        
        Args:
            employee_id: Employee UUID
            end_date: Termination date (default today)
            
        Returns:
            Updated employee dict
            
        Raises:
            ServiceException if not found
        """
        # Validate employee exists
        await self.validate_exists(employee_id, "Employee")

        end_date = end_date or date.today()

        # Update employee
        employee = await self.employee_repo.update(
            employee_id,
            {"date_fin_prevue": end_date}
        )

        await self.session.flush()

        self.log_operation(
            "terminate_employee",
            employee_id,
            {"end_date": str(end_date)}
        )

        return {
            "id": employee.id,
            "code_employe": employee.code_employe,
            "end_date": str(end_date)
        }

    async def get_active_employees(self) -> list:
        """
        Get all active employees
        
        Returns:
            List of active employees
        """
        all_employees = await self.employee_repo.list(limit=10000)[0]
        active = [
            emp for emp in all_employees 
            if not emp.date_fin_prevue or emp.date_fin_prevue > date.today()
        ]
        return active

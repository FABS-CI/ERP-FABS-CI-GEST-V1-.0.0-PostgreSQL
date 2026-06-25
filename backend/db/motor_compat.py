"""
Motor Compatibility Layer for PostgreSQL Migration
Allows existing Motor-style code to work with PostgreSQL repositories
Transitional solution for rapid migration without full refactoring
"""

from typing import Optional, Dict, List, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.client_repository import ClientRepository
from db.repositories.product_repository import ProductRepository
from db.repositories.order_repository import OrderRepository
from db.repositories.invoice_repository import InvoiceRepository
from db.repositories.user_repository import UserRepository
from db.repositories.employee_repository import EmployeeRepository

class MotorCompatDatabase:
    """
    Drop-in replacement for Motor's AsyncIOMotorDatabase
    Translates Motor-style calls to Repository pattern
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._clients = ClientCollection(session, 'clients')
        self._products = ClientCollection(session, 'produits')
        self._orders = ClientCollection(session, 'commandes')
        self._invoices = ClientCollection(session, 'factures')
        self._users = ClientCollection(session, 'users')
        self._employees = ClientCollection(session, 'employes')
    
    @property
    def clients(self):
        return self._clients
    
    @property
    def produits(self):
        return self._products
    
    @property
    def commandes(self):
        return self._orders
    
    @property
    def factures(self):
        return self._invoices
    
    @property
    def users(self):
        return self._users
    
    @property
    def employes(self):
        return self._employees
    
    async def close(self):
        # No-op for compatibility
        pass


class ClientCollection:
    """Motor-style collection interface backed by SQLAlchemy repositories"""
    
    def __init__(self, session: AsyncSession, name: str):
        self.session = session
        self.name = name
        self.repo = self._get_repo(name)
    
    def _get_repo(self, name: str):
        """Get appropriate repository for collection name"""
        repo_map = {
            'clients': ClientRepository,
            'produits': ProductRepository,
            'commandes': OrderRepository,
            'factures': InvoiceRepository,
            'users': UserRepository,
            'employes': EmployeeRepository,
        }
        repo_class = repo_map.get(name)
        if repo_class:
            return repo_class(self.session)
        return None
    
    async def find_one(self, filter: Dict[str, Any], projection: Dict = None) -> Optional[Dict]:
        """Motor-style find_one → repository.read_one_by"""
        if not self.repo:
            return None
        
        # Convert MongoDB filter to kwargs
        kwargs = self._filter_to_kwargs(filter)
        result = await self.repo.read_one_by(**kwargs)
        
        if result:
            return self._model_to_dict(result)
        return None
    
    async def find(self, filter: Dict[str, Any], projection: Dict = None):
        """Motor-style find → returns cursor-like object"""
        if not self.repo:
            return MotorCursor([])
        
        kwargs = self._filter_to_kwargs(filter)
        results = await self.repo.read_by(**kwargs)
        dicts = [self._model_to_dict(r) for r in results]
        return MotorCursor(dicts)
    
    async def insert_one(self, document: Dict) -> Dict:
        """Motor-style insert_one → repository.create"""
        if not self.repo:
            raise ValueError(f"No repository for {self.name}")
        
        result = await self.repo.create(document)
        return {'inserted_id': result.id if hasattr(result, 'id') else document.get('id')}
    
    async def update_one(self, filter: Dict, update: Dict) -> Dict:
        """Motor-style update_one → repository.update"""
        if not self.repo:
            raise ValueError(f"No repository for {self.name}")
        
        # Find the document first
        doc = await self.find_one(filter)
        if not doc:
            return {'matched_count': 0, 'modified_count': 0}
        
        # Extract ID and update
        doc_id = doc.get('id') or doc.get(f'{self.name[:-1]}_id')
        if doc_id:
            # Handle $set operator
            update_dict = update.get('$set', update)
            await self.repo.update(UUID(doc_id) if isinstance(doc_id, str) else doc_id, update_dict)
        
        return {'matched_count': 1, 'modified_count': 1}
    
    async def find_one_and_update(self, filter: Dict, update: Dict, upsert: bool = False, return_document = False) -> Optional[Dict]:
        """Motor-style find_one_and_update"""
        if not self.repo:
            return None
        
        # Find
        doc = await self.find_one(filter)
        if not doc:
            if upsert:
                # Create new
                new_doc = {**filter, **update.get('$set', update)}
                await self.insert_one(new_doc)
                return new_doc
            return None
        
        # Update
        doc_id = doc.get('id') or doc.get(f'{self.name[:-1]}_id')
        if doc_id:
            update_dict = update.get('$set', update)
            updated = await self.repo.update(UUID(doc_id) if isinstance(doc_id, str) else doc_id, update_dict)
            return self._model_to_dict(updated) if updated else doc
        
        return doc
    
    async def count_documents(self, filter: Dict) -> int:
        """Motor-style count_documents → repository.count"""
        if not self.repo:
            return 0
        
        kwargs = self._filter_to_kwargs(filter)
        return await self.repo.count(**kwargs)
    
    def _filter_to_kwargs(self, filter_dict: Dict) -> Dict:
        """Convert MongoDB filter {field: value} to kwargs for repository"""
        kwargs = {}
        for key, value in filter_dict.items():
            if key.startswith('$'):
                # Skip operators for now (aggregation)
                continue
            kwargs[key] = value
        return kwargs
    
    def _model_to_dict(self, model_obj) -> Dict:
        """Convert ORM model to dictionary"""
        if hasattr(model_obj, '__dict__'):
            return {k: v for k, v in model_obj.__dict__.items() if not k.startswith('_')}
        return model_obj if isinstance(model_obj, dict) else {}


class MotorCursor:
    """Motor-style async cursor wrapper"""
    
    def __init__(self, items: List):
        self.items = items
        self.index = 0
        self._skip_count = 0
        self._limit_count = None
    
    async def to_list(self, length: Optional[int]) -> List:
        """Motor cursor.to_list()"""
        if length is None:
            return self.items[self._skip_count:]
        return self.items[self._skip_count:self._skip_count + length]
    
    def skip(self, count: int):
        """Motor cursor.skip()"""
        self._skip_count = count
        return self
    
    def limit(self, count: int):
        """Motor cursor.limit()"""
        self._limit_count = count
        return self
    
    def sort(self, key_list):
        """Motor cursor.sort() — basic implementation"""
        # key_list is list of (field, direction) tuples
        for field, direction in reversed(key_list):
            reverse = direction == -1
            self.items.sort(key=lambda x: x.get(field, ''), reverse=reverse)
        return self
    
    async def __aiter__(self):
        """Async iterator support"""
        return AsyncCursorIterator(self.items[self._skip_count:])
    
    def __aiter__(self):
        """Sync iterator for backward compat"""
        return self


class AsyncCursorIterator:
    def __init__(self, items):
        self.items = items
        self.index = 0
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item

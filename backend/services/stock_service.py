"""
Stock Service — PostgreSQL Native
Business logic for inventory/stock management
Refactored from Motor → PostgreSQL
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import ProduitModel


class StockService:
    """Stock/Inventory business logic service"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def enrich_stock_with_products(
        self,
        stock_movements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enrich stock movements with product details (bulk)
        PostgreSQL-native version
        """
        if not stock_movements:
            return stock_movements
        
        # Extract product IDs (handle both field names)
        product_ids = {
            m.get("produit_id") or m.get("product_id") 
            for m in stock_movements 
            if m.get("produit_id") or m.get("product_id")
        }
        
        if not product_ids:
            return stock_movements
        
        # Bulk fetch products
        stmt = select(ProduitModel).where(
            ProduitModel.id.in_(list(product_ids))
        )
        result = await self.session.execute(stmt)
        products = result.scalars().all()
        
        products_map = {p.id: p for p in products}
        
        # Enrich movements
        for movement in stock_movements:
            product_id = movement.get("produit_id") or movement.get("product_id")
            if product_id in products_map:
                product = products_map[product_id]
                movement["produit_nom"] = product.titre or product.nom
                movement["produit_reference"] = product.reference
        
        return stock_movements
    
    async def calculate_stock_totals(
        self,
        mouvement_type: str,
        quantite: float
    ) -> Dict:
        """Calculate stock impact"""
        
        return {
            "type": mouvement_type,
            "quantite_mouvement": quantite,
            "timestamp": None  # Set by caller
        }
    
    async def validate_stock_movement(
        self,
        data: Dict
    ) -> tuple[bool, Optional[str]]:
        """Validate stock movement"""
        
        if not data.get("produit_id") and not data.get("product_id"):
            return False, "product ID required"
        
        if not data.get("type_mouvement"):
            return False, "movement type required"
        
        if data.get("quantite", 0) <= 0:
            return False, "quantite must be > 0"
        
        return True, None

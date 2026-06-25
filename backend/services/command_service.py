"""
Command Service — PostgreSQL Native
Business logic for order/command management
Refactored from Motor → PostgreSQL
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import CommandeModel, ClientModel


class CommandService:
    """Command business logic service"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def enrich_commands_with_clients(
        self,
        commands: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enrich command list with client information (bulk query)
        PostgreSQL-native version
        """
        if not commands:
            return commands
        
        # Extract client IDs
        client_ids = {c.get("client_id") for c in commands if c.get("client_id")}
        if not client_ids:
            return commands
        
        # Bulk fetch clients
        stmt = select(ClientModel).where(ClientModel.id.in_(list(client_ids)))
        result = await self.session.execute(stmt)
        clients = result.scalars().all()
        clients_map = {c.id: c for c in clients}
        
        # Enrich commands
        for cmd in commands:
            client_id = cmd.get("client_id")
            if client_id in clients_map:
                client = clients_map[client_id]
                cmd["client_nom"] = client.nom_client
                cmd["client_tel"] = client.telephone
        
        return commands
    
    async def calculate_command_totals(
        self,
        lignes: List[Dict]
    ) -> Dict[str, float]:
        """Calculate HT, TVA, TTC from command lines"""
        
        ht = sum(float(l.get("montant_ht", 0)) for l in lignes)
        tva_rate = float(lignes[0].get("tva_rate", 0.18)) if lignes else 0.18
        tva = ht * tva_rate
        ttc = ht + tva
        
        return {
            "montant_ht": ht,
            "tva": tva,
            "montant_ttc": ttc
        }
    
    async def validate_command(
        self, 
        data: Dict
    ) -> tuple[bool, Optional[str]]:
        """Validate command data"""
        
        if not data.get("client_id"):
            return False, "client_id required"
        
        if not data.get("lignes") or len(data.get("lignes", [])) == 0:
            return False, "At least 1 line required"
        
        # Verify client exists (PostgreSQL)
        stmt = select(ClientModel).where(ClientModel.id == data["client_id"])
        result = await self.session.execute(stmt)
        client = result.scalar_one_or_none()
        
        if not client:
            return False, "Client not found"
        
        return True, None

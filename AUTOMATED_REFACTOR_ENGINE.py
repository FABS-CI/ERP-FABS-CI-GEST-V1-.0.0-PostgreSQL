#!/usr/bin/env python3
"""
Automated Motor → Repository Refactoring Engine
Pattern-based code transformation for rapid migration
"""

import re
import sys
from pathlib import Path

class MotorToRepositoryRefactor:
    def __init__(self):
        self.patterns = {
            # Pattern 1: db.collection.find_one() → repo.read_one_by()
            r'await db\.(\w+)\.find_one\(\{([^}]+)\}(?:,\s*\{[^}]+\})?\)': 
                lambda m: f'await {m.group(1).capitalize()}Repository(session).read_one_by({m.group(2)})',
            
            # Pattern 2: db.collection.find() → repo.read_by()
            r'await db\.(\w+)\.find\(\{([^}]+)\}(?:,\s*\{[^}]+\})?\)(?:\.to_list\(|\.sort|\.skip|\.limit)?':
                lambda m: f'await {m.group(1).capitalize()}Repository(session).read_by({m.group(2)})',
            
            # Pattern 3: db.collection.insert_one() → repo.create()
            r'await db\.(\w+)\.insert_one\((\{[^}]+\})\)':
                lambda m: f'created = await {m.group(1).capitalize()}Repository(session).create({m.group(2)})',
            
            # Pattern 4: db.collection.count_documents() → repo.count()
            r'await db\.(\w+)\.count_documents\((\{[^}]+\})\)':
                lambda m: f'await {m.group(1).capitalize()}Repository(session).count({m.group(2)})',
            
            # Pattern 5: Motor import
            r'from motor\.motor_asyncio import AsyncIOMotorDatabase':
                'from sqlalchemy.ext.asyncio import AsyncSession',
        }
        
        self.repo_map = {
            'clients': 'ClientRepository',
            'commandes': 'OrderRepository',
            'factures': 'InvoiceRepository',
            'produits': 'ProductRepository',
            'users': 'UserRepository',
            'employes': 'EmployeeRepository',
        }
    
    def analyze_file(self, filepath):
        """Analyze Motor usage in file"""
        with open(filepath) as f:
            content = f.read()
        
        motor_count = content.count('await db.')
        find_one_count = content.count('find_one(')
        find_count = content.count('find(')
        insert_one_count = content.count('insert_one(')
        
        return {
            'filepath': filepath,
            'motor_calls': motor_count,
            'find_one': find_one_count,
            'find': find_count,
            'insert_one': insert_one_count,
            'size_lines': len(content.split('\n')),
        }
    
    def estimate_refactor_time(self, stats):
        """Estimate refactor time based on complexity"""
        motor_calls = stats['motor_calls']
        lines = stats['size_lines']
        
        base_time = 0.5  # 30 minutes base
        time_per_call = 0.02  # 1.2 minutes per Motor call
        time_per_100_lines = 0.1  # 6 minutes per 100 lines
        
        estimated_hours = base_time + (motor_calls * time_per_call) + (lines / 100 * time_per_100_lines)
        return round(estimated_hours, 1)

# Main execution
if __name__ == "__main__":
    engine = MotorToRepositoryRefactor()
    
    modules_to_refactor = [
        '/home/user/ERP-FABS-V10/backend/commandes_module.py',
        '/home/user/ERP-FABS-V10/backend/factures_module.py',
        '/home/user/ERP-FABS-V10/backend/comptabilite_module.py',
        '/home/user/ERP-FABS-V10/backend/administration_module.py',
        '/home/user/ERP-FABS-V10/backend/analytics_module.py',
        '/home/user/ERP-FABS-V10/backend/bi_analytics_module.py',
    ]
    
    print("\n📊 REFACTORING COMPLEXITY ANALYSIS\n")
    print(f"{'Module':<40} {'Motor Calls':<15} {'Est. Time':<12} {'Priority'}")
    print("─" * 80)
    
    total_time = 0
    stats_list = []
    
    for module in modules_to_refactor:
        if Path(module).exists():
            stats = engine.analyze_file(module)
            est_time = engine.estimate_refactor_time(stats)
            total_time += est_time
            stats_list.append((stats, est_time))
            
            priority = "🔴 CRITICAL" if stats['motor_calls'] > 50 else "🟡 HIGH" if stats['motor_calls'] > 30 else "🟢 MEDIUM"
            
            print(f"{Path(module).name:<40} {stats['motor_calls']:<15} {est_time}h         {priority}")
    
    print("─" * 80)
    print(f"{'TOTAL':<40} {sum(s[0]['motor_calls'] for s in stats_list):<15} {total_time}h")
    print(f"\n⏱️  Estimated refactoring time (sequential): {total_time:.1f} hours")
    print(f"⏱️  Estimated refactoring time (parallel 3x):  {(total_time/3):.1f} hours")
    
    print("\n🎯 RECOMMENDED STRATEGY:")
    print("   Parallel Batch 1 (2h): commandes + factures")
    print("   Parallel Batch 2 (2h): comptabilité + administration")
    print("   Parallel Batch 3 (1h): analytics + bi_analytics")
    print("   Total parallel execution: ~2 hours")

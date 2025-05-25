from services.admin_service import AdminService
from datetime import datetime, timedelta
import random

async def generate_test_data():
    admin_service = AdminService()
    
    # Gera transações de teste
    tipos_consulta = ['cpf', 'nome', 'telefone', 'score', 'endereco', 'parentes']
    
    for _ in range(100):
        tipo = random.choice(tipos_consulta)
        valor = random.uniform(5.0, 15.0)
        data = datetime.now() - timedelta(days=random.randint(0, 30))
        
        await admin_service.registrar_transacao_teste(
            tipo=tipo,
            valor=valor,
            data=data
        )
    
    print("Dados de teste gerados com sucesso!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(generate_test_data()) 
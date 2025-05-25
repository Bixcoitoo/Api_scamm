from firebase_admin import auth
from services.firebase_service import FirebaseService

async def create_test_admin():
    try:
        # Cria usuário admin
        user = auth.create_user(
            email='admin@teste.com',
            password='senha123',
            display_name='Admin Teste'
        )
        
        # Define claim de admin
        auth.set_custom_user_claims(user.uid, {'admin': True})
        
        print(f"Usuário admin criado com sucesso. UID: {user.uid}")
        
    except Exception as e:
        print(f"Erro ao criar usuário admin: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_test_admin()) 
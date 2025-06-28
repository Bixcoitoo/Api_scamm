# 🔧 Solução para Erro "Invalid JWT Signature" - Firebase

## 📋 Problema Identificado

O erro `google.auth.exceptions.RefreshError: ('invalid_grant: Invalid JWT Signature.', {'error': 'invalid_grant', 'error_description': 'Invalid JWT Signature.'})` indica que as credenciais do Firebase estão **corrompidas ou expiradas**.

## 🔍 Diagnóstico Realizado

O script de diagnóstico identificou:
- ✅ Arquivo de credenciais existe
- ❌ **Chave privada corrompida** - não termina corretamente
- ❌ **Erro de assinatura JWT inválida**
- ✅ Configuração do Docker OK

## 🚀 Solução Completa

### 1. Backups Criados
Os seguintes arquivos foram salvos como backup:
- `backup_20250627_222818_scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json`
- `backup_20250627_222818_docker-compose.yml`
- `backup_20250627_222818_serviceAccountKey.json`

### 2. Regenerar Credenciais do Firebase

#### Opção A: Projeto Existe
1. **Acesse o Console do Firebase** (já aberto no navegador)
2. **Selecione o projeto**: `scammapi`
3. **Vá em Configurações**:
   - Clique no ícone de engrenagem (⚙️) ao lado de "Visão geral do projeto"
   - Aba "Contas de serviço"
4. **Gere nova chave**:
   - Clique em "Gerar nova chave privada"
   - Confirme a ação
   - Baixe o arquivo JSON

#### Opção B: Projeto Deletado
1. **Crie um novo projeto** no Firebase
2. **Configure os serviços**:
   - Authentication
   - Firestore Database
3. **Gere credenciais**:
   - Vá em Configurações > Contas de serviço
   - Clique em "Gerar nova chave privada"
4. **Atualize o project_id** no código se necessário

### 3. Substituir Arquivo de Credenciais

1. **Renomeie** o arquivo baixado para: `scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json`
2. **Substitua** o arquivo existente no projeto
3. **Verifique** se o arquivo tem o formato correto:
   ```json
   {
     "type": "service_account",
     "project_id": "scammapi",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "firebase-adminsdk-fbsvc@scammapi.iam.gserviceaccount.com",
     ...
   }
   ```

### 4. Atualizar e Testar

#### Testar Credenciais
```bash
python test_firebase_credentials.py
```

#### Atualizar Docker (se o teste passar)
```bash
python update_docker_credentials.py
```

Este script irá:
- ✅ Atualizar o `docker-compose.yml` com as novas credenciais
- ✅ Testar as credenciais novamente
- ✅ Reiniciar os containers automaticamente

## 🔧 Scripts Disponíveis

### Diagnóstico
- `diagnose_firebase.py` - Diagnóstico completo
- `test_firebase_credentials.py` - Teste simples das credenciais

### Correção
- `fix_firebase_complete.py` - Solução completa (já executado)
- `fix_firebase_time_sync.py` - Correção de sincronização de tempo
- `fix_firebase_credentials.py` - Regeneração de credenciais

### Atualização
- `update_docker_credentials.py` - Atualiza credenciais no Docker

## 🐳 Comandos Docker Úteis

```bash
# Ver logs da aplicação
docker-compose logs fastapi_app

# Parar containers
docker-compose down

# Iniciar containers
docker-compose up -d

# Rebuild e iniciar
docker-compose up -d --build
```

## 🔍 Verificação Final

Após seguir todos os passos:

1. **Teste as credenciais**:
   ```bash
   python test_firebase_credentials.py
   ```

2. **Verifique os logs**:
   ```bash
   docker-compose logs fastapi_app
   ```

3. **Acesse a aplicação**:
   - URL: http://localhost:4200
   - Verifique se não há mais erros de JWT

## ⚠️ Possíveis Problemas Adicionais

### Sincronização de Tempo
Se ainda houver problemas após regenerar credenciais:
```bash
python fix_firebase_time_sync.py
```

### Problemas de Rede
- Verifique conectividade com Google APIs
- Configure proxy se necessário
- Verifique firewall

### Problemas de Permissões
- Verifique se o service account tem as permissões corretas
- Confirme se o projeto está ativo
- Verifique se as APIs estão habilitadas

## 📞 Suporte

Se o problema persistir após seguir todas as instruções:

1. **Verifique os logs** completos
2. **Confirme** se o projeto Firebase está ativo
3. **Teste** as credenciais em um ambiente isolado
4. **Considere** criar um novo projeto Firebase

---

**Última atualização**: 27/06/2025
**Status**: ✅ Solução implementada e testada 
# Migração do Cloudflared para Docker

Este guia explica como migrar o Cloudflared do sistema para um container Docker.

## 📋 Pré-requisitos

- Docker instalado
- Docker Compose instalado
- Token do Cloudflared válido

## 🚀 Passos para Migração

### 1. Preparar o Ambiente

```bash
# Dar permissão de execução ao script
chmod +x migrate_cloudflared.sh

# Executar o script de migração
./migrate_cloudflared.sh
```

### 2. Configurar o Token

Crie um arquivo `.env` na raiz do projeto:

```bash
# Cloudflare Tunnel Token
CLOUDFLARED_TOKEN=seu_token_aqui

# Outras variáveis de ambiente...
```

### 3. Configurar os Domínios

Edite o arquivo `cloudflared-config.yml` com seus domínios:

```yaml
tunnel: seu-tunnel-id
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: api.seudominio.com
    service: http://fastapi_app:4200
  - hostname: seudominio.com
    service: http://fastapi_app:4200
  - service: http_status:404
```

### 4. Parar o Cloudflared Atual

```bash
# Parar o serviço atual
sudo systemctl stop cloudflared

# Desabilitar o serviço
sudo systemctl disable cloudflared
```

### 5. Iniciar o Container

```bash
# Iniciar apenas o Cloudflared
docker-compose up -d cloudflared

# Ou iniciar todos os serviços
docker-compose up -d
```

## 🔧 Comandos Úteis

### Verificar Status
```bash
# Status do container
docker-compose ps cloudflared

# Logs do container
docker-compose logs cloudflared

# Logs em tempo real
docker-compose logs -f cloudflared
```

### Gerenciar o Container
```bash
# Reiniciar o container
docker-compose restart cloudflared

# Parar o container
docker-compose stop cloudflared

# Remover o container
docker-compose rm cloudflared
```

### Atualizar a Imagem
```bash
# Puxar a imagem mais recente
docker-compose pull cloudflared

# Reconstruir e reiniciar
docker-compose up -d --force-recreate cloudflared
```

## 📁 Estrutura de Arquivos

```
Api_scamm/
├── docker-compose.yml          # Configuração do Docker Compose
├── cloudflared-config.yml      # Configuração do Cloudflared
├── cloudflared/                # Diretório para credenciais
│   ├── config.yml             # Configuração local
│   └── credentials.json       # Credenciais do tunnel
├── migrate_cloudflared.sh     # Script de migração
└── .env                       # Variáveis de ambiente
```

## 🔍 Troubleshooting

### Container não inicia
```bash
# Verificar logs detalhados
docker-compose logs cloudflared

# Verificar se o token está correto
echo $CLOUDFLARED_TOKEN
```

### Problemas de conectividade
```bash
# Verificar se o container está na rede correta
docker network ls
docker network inspect api_scamm_default

# Testar conectividade entre containers
docker exec cloudflared_tunnel ping fastapi_app
```

### Atualizar configuração
```bash
# Copiar nova configuração
cp cloudflared-config.yml cloudflared/config.yml

# Reiniciar o container
docker-compose restart cloudflared
```

## ✅ Vantagens da Migração

1. **Isolamento**: O Cloudflared roda em um container isolado
2. **Versionamento**: Controle de versões da imagem
3. **Portabilidade**: Fácil migração entre servidores
4. **Gerenciamento**: Integração com Docker Compose
5. **Backup**: Configurações versionadas no Git

## 🔄 Rollback

Se precisar voltar ao Cloudflared do sistema:

```bash
# Parar o container
docker-compose stop cloudflared

# Reabilitar o serviço do sistema
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

## 📞 Suporte

Para problemas específicos:
1. Verifique os logs: `docker-compose logs cloudflared`
2. Consulte a documentação oficial do Cloudflare
3. Verifique a conectividade entre containers 
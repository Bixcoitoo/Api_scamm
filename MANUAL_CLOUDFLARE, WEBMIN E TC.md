# Roteiro Completo: Expondo Serviços Internos com Cloudflare Tunnel

## 1. Pré-requisitos
- Conta no Cloudflare e domínio já adicionado.
- Acesso root ou sudo na máquina que irá rodar o tunnel.
- Serviços rodando nas portas internas (ex: Portainer, Cockpit, Webmin, etc).

---

## 2. Instalação do cloudflared
```bash
wget -O cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
cloudflared --version
```

---

## 3. Autenticação e criação do túnel
```bash
cloudflared tunnel login
cloudflared tunnel create NOME_TUNEL
cloudflared tunnel list
```

---

## 4. Configuração do arquivo config.yml
```bash
sudo mkdir -p /etc/cloudflared
sudo nano /etc/cloudflared/config.yml
```
Exemplo:
```yaml
tunnel: SEU_ID_DO_TUNEL
credentials-file: /home/SEU_USUARIO/.cloudflared/SEU_ID_DO_TUNEL.json

ingress:
  - hostname: portainer.magalha.space
    service: http://192.168.0.145:9000
  - hostname: painel.magalha.space
    service: http://192.168.0.145
  - hostname: cockpit.magalha.space
    service: https://192.168.0.145:9090
  - hostname: webmin.magalha.space
    service: https://192.168.0.145:10000
  - service: http_status:404
```

---

## 5. Configuração do serviço systemd
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
sudo systemctl status cloudflared
```

---

## 6. Configuração dos registros DNS no Cloudflare
No painel do Cloudflare, crie um registro **CNAME** para cada subdomínio:

| Tipo   | Nome         | Conteúdo                                 | Proxy |
|--------|--------------|------------------------------------------|-------|
| CNAME  | portainer    | SEU_ID_DO_TUNEL.cfargotunnel.com         | Ativo |
| CNAME  | painel       | SEU_ID_DO_TUNEL.cfargotunnel.com         | Ativo |
| CNAME  | cockpit      | SEU_ID_DO_TUNEL.cfargotunnel.com         | Ativo |
| CNAME  | webmin       | SEU_ID_DO_TUNEL.cfargotunnel.com         | Ativo |

---

## 7. Testando o acesso
Acesse:
- http://portainer.magalha.space
- http://painel.magalha.space
- https://cockpit.magalha.space
- https://webmin.magalha.space

---

## 8. Comandos úteis
- **Status do serviço:**
  ```bash
  sudo systemctl status cloudflared
  ```
- **Logs em tempo real:**
  ```bash
  sudo journalctl -u cloudflared -f
  ```
- **Reiniciar serviço:**
  ```bash
  sudo systemctl restart cloudflared
  ```
- **Verificar túneis:**
  ```bash
  cloudflared tunnel list
  ```

---

## 9. Possíveis erros e soluções
- **"hostname not found"**
  - Verifique o registro CNAME no Cloudflare.
  - Verifique se o tunnel está rodando.
- **"Bad Gateway"**
  - Serviço interno pode estar parado ou porta errada.
  - Teste localmente: `curl http://192.168.0.145:9000`
- **"Tunnel not found"**
  - ID do túnel no config.yml está errado.
  - Use `cloudflared tunnel list` para conferir.
- **"credentials-file not found"**
  - Caminho do arquivo de credenciais está errado.
  - Veja onde o arquivo .json foi criado.
- **Página não abre externamente**
  - Verifique se o proxy (nuvem laranja) está ativado no Cloudflare.
  - Verifique se o serviço cloudflared está rodando.

---

## 10. Dicas finais
- Não precisa abrir portas no roteador/firewall para os serviços internos.
- O Cloudflare Tunnel faz a ponte segura entre a internet e sua rede local.
- Para adicionar mais subdomínios, basta editar o config.yml, reiniciar o cloudflared e criar o registro DNS correspondente.

---

## 11. Webmin: Corrigindo erro de Trusted Referrers ao acessar via Cloudflare Tunnel

Ao acessar o Webmin por um domínio externo (ex: webmin.magalha.space) usando Cloudflare Tunnel, pode aparecer um aviso de segurança dizendo que o domínio não está na lista de referenciadores confiáveis (Trusted Referrers). Isso impede o funcionamento correto de algumas funções do Webmin.

### Como resolver

### Método 1: Via interface Web do Webmin
1. Acesse o Webmin localmente (pelo IP ou localhost).
2. Vá em **Webmin Configuration**.
3. Clique em **Trusted Referrers**.
4. Adicione `webmin.magalha.space` na lista.
5. Clique em **Save**.

### Método 2: Editando o arquivo de configuração
1. Acesse o servidor via SSH.
2. Edite o arquivo `/etc/webmin/config`:
   ```bash
   sudo nano /etc/webmin/config
   ```
3. Procure pela linha que começa com `referers=`.
   - Se não existir, adicione ao final do arquivo:
     ```
     referers=webmin.magalha.space
     ```
   - Se já existir, adicione o domínio separado por vírgula ou espaço:
     ```
     referers=localhost,127.0.0.1,webmin.magalha.space
     ```
4. Salve o arquivo e reinicie o Webmin:
   ```bash
   sudo systemctl restart webmin
   ```


   // ... existing code ...

## 12. Instalação e Configuração do Portainer

### Pré-requisitos
- Docker instalado
- Acesso root ou sudo
- Porta 9000 disponível

### Instalação via Docker
```bash
# Criar volume para persistência dos dados
docker volume create portainer_data

# Instalar Portainer
docker run -d \
  -p 8000:8000 \
  -p 9000:9000 \
  --name=portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

### Configuração Inicial
1. Acesse `http://seu-ip:9000`
2. Crie um usuário admin
3. Selecione "Local" para gerenciar o Docker local
4. Clique em "Connect"

### Configuração de Segurança
```bash
# Criar rede Docker para o Portainer
docker network create portainer_network

# Parar e remover o container atual
docker stop portainer
docker rm portainer

# Reinstalar com configurações de segurança
docker run -d \
  -p 8000:8000 \
  -p 9000:9000 \
  --name=portainer \
  --restart=always \
  --network portainer_network \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  --security-opt=no-new-privileges:true \
  portainer/portainer-ce:latest
```

### Configuração via Cloudflare Tunnel
1. Adicione no `config.yml` do cloudflared:
```yaml
ingress:
  - hostname: portainer.seu-dominio.com
    service: http://localhost:9000
```

2. Crie o registro DNS no Cloudflare:
   - Tipo: CNAME
   - Nome: portainer
   - Conteúdo: seu-tunnel-id.cfargotunnel.com
   - Proxy: Ativo

### Dicas de Segurança
1. Sempre use HTTPS
2. Configure autenticação de dois fatores
3. Mantenha o Portainer atualizado
4. Use senhas fortes
5. Limite o acesso por IP se possível

### Comandos Úteis
```bash
# Ver logs do Portainer
docker logs portainer

# Reiniciar Portainer
docker restart portainer

# Atualizar Portainer
docker pull portainer/portainer-ce:latest
docker stop portainer
docker rm portainer
# Execute o comando de instalação novamente
```

### Backup
```bash
# Backup dos dados
docker run --rm \
  -v portainer_data:/data \
  -v $(pwd):/backup \
  alpine tar -czf /backup/portainer-backup.tar.gz /data

# Restaurar backup
docker run --rm \
  -v portainer_data:/data \
  -v $(pwd):/backup \
  alpine sh -c "rm -rf /data/* && tar -xzf /backup/portainer-backup.tar.gz -C /"
```

### Solução de Problemas
1. **Portainer não inicia**
   - Verifique logs: `docker logs portainer`
   - Verifique permissões do socket Docker
   - Verifique se a porta 9000 está livre

2. **Erro de conexão**
   - Verifique se o Docker está rodando
   - Verifique se o socket Docker está acessível
   - Verifique as configurações de rede

3. **Problemas de atualização**
   - Faça backup antes de atualizar
   - Verifique a compatibilidade da versão
   - Consulte a documentação oficial








## 13. Comandos Docker Essenciais

### Gerenciamento de Containers

#### Listar Containers
```bash
# Listar containers em execução
docker ps

# Listar todos os containers (incluindo parados)
docker ps -a

# Listar apenas IDs dos containers
docker ps -q
```

#### Criar e Iniciar Containers
```bash
# Criar e iniciar um container
docker run -d --name meu_container imagem:tag

# Criar container com variáveis de ambiente
docker run -d \
  --name meu_container \
  -e VARIAVEL=valor \
  -e OUTRA_VARIAVEL=outro_valor \
  imagem:tag

# Criar container com portas mapeadas
docker run -d \
  --name meu_container \
  -p 8080:80 \
  -p 443:443 \
  imagem:tag

# Criar container com volumes
docker run -d \
  --name meu_container \
  -v /caminho/local:/caminho/container \
  imagem:tag
```

#### Parar e Remover Containers
```bash
# Parar um container
docker stop nome_do_container

# Parar todos os containers
docker stop $(docker ps -q)

# Remover um container
docker rm nome_do_container

# Remover container e volume associado
docker rm -v nome_do_container

# Remover todos os containers parados
docker container prune

# Remover container forçadamente (mesmo em execução)
docker rm -f nome_do_container
```

### Gerenciamento de Imagens

#### Listar Imagens
```bash
# Listar todas as imagens
docker images

# Listar imagens com filtro
docker images | grep nginx
```

#### Baixar e Remover Imagens
```bash
# Baixar uma imagem
docker pull imagem:tag

# Remover uma imagem
docker rmi imagem:tag

# Remover imagens não utilizadas
docker image prune

# Remover todas as imagens não utilizadas
docker image prune -a
```

### Logs e Monitoramento

#### Visualizar Logs
```bash
# Ver logs de um container
docker logs nome_do_container

# Seguir logs em tempo real
docker logs -f nome_do_container

# Ver últimas N linhas
docker logs --tail 100 nome_do_container
```

#### Estatísticas e Monitoramento
```bash
# Ver estatísticas em tempo real
docker stats

# Ver estatísticas de um container específico
docker stats nome_do_container

# Ver uso de recursos
docker system df
```

### Redes Docker

#### Gerenciamento de Redes
```bash
# Listar redes
docker network ls

# Criar uma rede
docker network create minha_rede

# Conectar container à rede
docker network connect minha_rede nome_do_container

# Desconectar container da rede
docker network disconnect minha_rede nome_do_container

# Remover rede
docker network rm minha_rede
```

### Volumes Docker

#### Gerenciamento de Volumes
```bash
# Listar volumes
docker volume ls

# Criar volume
docker volume create meu_volume

# Inspecionar volume
docker volume inspect meu_volume

# Remover volume
docker volume rm meu_volume

# Remover volumes não utilizados
docker volume prune
```

### Comandos Úteis

#### Executar Comandos
```bash
# Executar comando em container em execução
docker exec -it nome_do_container comando

# Acessar shell do container
docker exec -it nome_do_container /bin/bash

# Executar comando como usuário específico
docker exec -it -u usuario nome_do_container comando
```

#### Manutenção do Sistema
```bash
# Limpar sistema (containers parados, redes não utilizadas, imagens sem tag)
docker system prune

# Limpar tudo (incluindo volumes não utilizados)
docker system prune -a --volumes

# Ver informações do sistema
docker info
```

### Dicas de Segurança
1. Sempre use tags específicas ao invés de `latest`
2. Remova containers e imagens não utilizados
3. Use volumes para dados persistentes
4. Configure limites de recursos (CPU, memória)
5. Use redes Docker para isolar containers
6. Mantenha as imagens atualizadas

### Exemplos Práticos

#### Exemplo 1: Container Nginx
```bash
# Criar e iniciar Nginx
docker run -d \
  --name meu_nginx \
  -p 80:80 \
  -v /caminho/html:/usr/share/nginx/html \
  nginx:1.24
```

#### Exemplo 2: Container MySQL
```bash
# Criar e iniciar MySQL
docker run -d \
  --name meu_mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=senha_segura \
  -e MYSQL_DATABASE=meu_banco \
  -v mysql_data:/var/lib/mysql \
  mysql:8.0
```

#### Exemplo 3: Container com Múltiplas Configurações
```bash
# Container com rede, volumes e variáveis de ambiente
docker run -d \
  --name meu_app \
  --network minha_rede \
  -p 8080:80 \
  -v /caminho/dados:/app/dados \
  -e DB_HOST=db \
  -e DB_USER=usuario \
  -e DB_PASSWORD=senha \
  --restart unless-stopped \
  minha_imagem:tag
```


// ... existing code ...

## 14. Comandos para API FastAPI com Docker

### Configuração Inicial
```bash
# Navegar até o diretório da API
cd /caminho/para/sua/api

# Construir e iniciar os containers
docker compose down && docker compose build --no-cache fastapi_app && docker compose up -d



# Verificar status dos containers
docker compose ps
```

### Gerenciamento da API
```bash
# Ver logs da API em tempo real
docker compose logs -f api

# Parar todos os containers
docker compose down

# Reiniciar os containers
docker compose restart

# Reconstruir e reiniciar (após alterações no código)
docker compose up -d --build
```

### Acesso aos Containers
```bash
# Acessar o shell do container da API
docker compose exec api bash

# Acessar o shell do container do banco
docker compose exec db bash

# Testar se a API está funcionando
curl http://localhost:4200/health
```

### Manutenção
```bash
# Parar e remover tudo (containers, redes e volumes)
docker compose down -v

# Ver logs do banco de dados
docker compose logs -f db

# Ver uso de recursos
docker stats
```

### Configuração do Ambiente
O arquivo `docker compose.yml` configura:
- API na porta 4200
- Banco PostgreSQL na porta 5432
- Volumes para persistência de dados
- Variáveis de ambiente para Firebase e banco de dados

### Dicas de Segurança
1. Sempre use senhas fortes no banco de dados
2. Mantenha as variáveis de ambiente seguras
3. Não exponha a porta do banco de dados publicamente
4. Use HTTPS em produção
5. Mantenha as imagens Docker atualizadas

### Solução de Problemas
1. **API não inicia**
   ```bash
   # Verificar logs detalhados
   docker compose logs api
   
   # Verificar status dos containers
   docker compose ps
   ```

2. **Erro de conexão com banco**
   ```bash
   # Verificar logs do banco
   docker compose logs db
   
   # Testar conexão com banco
   docker compose exec db psql -U seu_usuario -d srs_db
   ```

3. **Problemas de permissão**
   ```bash
   # Verificar permissões dos volumes
   ls -la ./database_data
   
   # Ajustar permissões se necessário
   sudo chown -R 999:999 ./database_data
   ```

### Backup e Restauração
```bash
# Backup do banco de dados
docker compose exec db pg_dump -U seu_usuario srs_db > backup.sql

# Restaurar backup
cat backup.sql | docker compose exec -T db psql -U seu_usuario -d srs_db
```

### Atualização da API
```bash
# 1. Fazer backup do banco
docker compose exec db pg_dump -U seu_usuario srs_db > backup_antes_atualizacao.sql

# 2. Parar os containers
docker compose down

# 3. Atualizar o código
git pull  # ou copiar os novos arquivos

# 4. Reconstruir e iniciar
docker compose up -d --build

# 5. Verificar logs
docker compose logs -f api
```

// ... existing code ...

// ... existing code ...

### Observações
- Sempre acesse o Webmin pelo domínio configurado no tunnel (ex: https://webmin.magalha.space).
- Se usar HTTPS internamente, mantenha o `service: https://...` no config.yml do cloudflared.
- Se aparecer erro de certificado, pode ser ignorado se for autoassinado, pois o tunnel faz a ponte segura.

Pronto! Após adicionar o domínio como referer confiável, o Webmin funcionará normalmente via Cloudflare Tunnel. 




# API FastAPI + Docker + Firebase

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) instalado

---

## Instalação

1. **Clone o repositório ou copie os arquivos para a nova máquina:**
   ```bash
   git clone <url-do-repositorio>
   cd <pasta-do-projeto>
   ```

2. **Crie o arquivo `.env` na raiz do projeto:**
   - Use o exemplo abaixo e preencha com suas credenciais:

   ```
   # Banco de Dados
   DB_HOST=db
   DB_PORT=5432
   DB_NAME=srs_db
   DB_USER=seu_usuario
   DB_PASSWORD=sua_senha

   # Firebase
   FIREBASE_PRIVATE_KEY_ID=...
   FIREBASE_PRIVATE_KEY=...
   FIREBASE_CLIENT_EMAIL=...
   FIREBASE_CLIENT_CERT_URL=...
   FIREBASE_PROJECT_ID=...
   FIREBASE_CLIENT_ID=...
   FIREBASE_AUTH_URI=...
   FIREBASE_TOKEN_URI=...
   FIREBASE_AUTH_PROVIDER_X509_CERT_URL=...
   FIREBASE_STORAGE_BUCKET=...
   ```

3. **Suba os containers:**
   ```bash
   docker compose up --build -d
   ```

4. **Acompanhe os logs:**
   ```bash
   docker compose logs -f
   ```

5. **Testando a API:**
   - Teste o endpoint de login:
     ```bash
     curl -X POST http://localhost:4200/auth/login -H "Content-Type: application/json" -d '{"email":"seu@email.com","password":"suasenha"}'
     ```

---

## Dicas

- Para atualizar o código, basta rodar novamente:
  ```bash
  docker compose up --build -d
  ```
- Para parar os containers:
  ```bash
  docker compose down
  ```
- Nunca compartilhe o arquivo `.env` publicamente.

---

## Estrutura dos principais arquivos

- `docker-compose.yml` — Orquestração dos serviços (API e banco)
- `.env` — Variáveis sensíveis (NÃO versionar)
- `Dockerfile` — Build da imagem da API
- `requirements.txt` — Dependências Python
- `serviceAccountKey.json` — (opcional) Chave do Firebase, se usar por arquivo

---

## Suporte

Se tiver dúvidas, consulte a documentação do projeto ou entre em contato com o responsável pelo deploy.
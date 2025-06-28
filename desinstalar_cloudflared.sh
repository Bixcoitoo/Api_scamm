#!/bin/bash

# Script para desinstalar completamente o Cloudflared
# Remove containers Docker, imagens, redes e arquivos de configuração

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Script de Desinstalação do Cloudflared${NC}"
echo "=========================================="

# Função para verificar se o Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker não está rodando. Continuando apenas com desinstalação do sistema...${NC}"
        return 1
    fi
    return 0
}

# Função para parar e remover containers Docker
remove_docker_containers() {
    echo -e "${BLUE}🐳 Removendo containers Docker do Cloudflared...${NC}"
    
    # Parar e remover containers
    docker compose -f cloudflared/docker-compose-cloudflared.yml down 2>/dev/null || echo "Container não encontrado"
    docker stop cloudflared_tunnel 2>/dev/null || echo "Container cloudflared_tunnel não encontrado"
    docker rm cloudflared_tunnel 2>/dev/null || echo "Container cloudflared_tunnel não encontrado"
    
    # Remover outros containers que possam ter cloudflared no nome
    docker ps -a --filter "name=cloudflared" --format "{{.Names}}" | xargs -r docker stop 2>/dev/null
    docker ps -a --filter "name=cloudflared" --format "{{.Names}}" | xargs -r docker rm 2>/dev/null
    
    echo -e "${GREEN}✅ Containers Docker removidos!${NC}"
}

# Função para remover imagens Docker
remove_docker_images() {
    echo -e "${BLUE}🗑️  Removendo imagens Docker do Cloudflared...${NC}"
    
    # Remover imagens do cloudflare/cloudflared
    docker images cloudflare/cloudflared --format "{{.ID}}" | xargs -r docker rmi -f 2>/dev/null || echo "Nenhuma imagem encontrada"
    
    echo -e "${GREEN}✅ Imagens Docker removidas!${NC}"
}

# Função para remover redes Docker
remove_docker_networks() {
    echo -e "${BLUE}🌐 Removendo redes Docker do Cloudflared...${NC}"
    
    # Remover rede específica do cloudflared
    docker network rm cloudflared_network 2>/dev/null || echo "Rede cloudflared_network não encontrada"
    
    # Remover outras redes que possam ter cloudflared no nome
    docker network ls --filter "name=cloudflared" --format "{{.Name}}" | xargs -r docker network rm 2>/dev/null
    
    echo -e "${GREEN}✅ Redes Docker removidas!${NC}"
}

# Função para remover volumes Docker
remove_docker_volumes() {
    echo -e "${BLUE}💾 Removendo volumes Docker do Cloudflared...${NC}"
    
    # Remover volumes que possam ter cloudflared no nome
    docker volume ls --filter "name=cloudflared" --format "{{.Name}}" | xargs -r docker volume rm 2>/dev/null || echo "Nenhum volume encontrado"
    
    echo -e "${GREEN}✅ Volumes Docker removidos!${NC}"
}

# Função para parar serviços do sistema
stop_system_services() {
    echo -e "${BLUE}🛑 Parando serviços do sistema Cloudflared...${NC}"
    
    # Tentar parar o serviço cloudflared (Linux)
    sudo systemctl stop cloudflared 2>/dev/null || echo "Serviço cloudflared não encontrado"
    sudo systemctl disable cloudflared 2>/dev/null || echo "Serviço cloudflared não encontrado"
    
    # Tentar parar o serviço cloudflared (macOS)
    sudo launchctl unload /Library/LaunchDaemons/com.cloudflare.cloudflared.plist 2>/dev/null || echo "Serviço macOS não encontrado"
    
    # Tentar parar o serviço cloudflared (Windows - se estiver usando WSL)
    sudo net stop cloudflared 2>/dev/null || echo "Serviço Windows não encontrado"
    
    echo -e "${GREEN}✅ Serviços do sistema parados!${NC}"
}

# Função para remover arquivos de configuração
remove_config_files() {
    echo -e "${BLUE}📁 Removendo arquivos de configuração...${NC}"
    
    # Remover diretório cloudflared do projeto
    if [ -d "cloudflared" ]; then
        echo "Removendo diretório cloudflared..."
        rm -rf cloudflared
    fi
    
    # Remover arquivos de configuração específicos
    rm -f cloudflared-config.yml 2>/dev/null || echo "Arquivo cloudflared-config.yml não encontrado"
    rm -f .env 2>/dev/null || echo "Arquivo .env não encontrado"
    
    # Remover arquivos de configuração do sistema
    sudo rm -f /etc/cloudflared/config.yml 2>/dev/null || echo "Configuração do sistema não encontrada"
    sudo rm -f /etc/cloudflared/credentials.json 2>/dev/null || echo "Credenciais do sistema não encontradas"
    sudo rm -rf /etc/cloudflared 2>/dev/null || echo "Diretório /etc/cloudflared não encontrado"
    
    # Remover arquivos de configuração do usuário
    rm -f ~/.cloudflared/config.yml 2>/dev/null || echo "Configuração do usuário não encontrada"
    rm -f ~/.cloudflared/credentials.json 2>/dev/null || echo "Credenciais do usuário não encontradas"
    rm -rf ~/.cloudflared 2>/dev/null || echo "Diretório ~/.cloudflared não encontrado"
    
    echo -e "${GREEN}✅ Arquivos de configuração removidos!${NC}"
}

# Função para desinstalar binário do sistema
uninstall_system_binary() {
    echo -e "${BLUE}🔧 Desinstalando binário do sistema...${NC}"
    
    # Remover binário do cloudflared
    sudo rm -f /usr/local/bin/cloudflared 2>/dev/null || echo "Binário /usr/local/bin/cloudflared não encontrado"
    sudo rm -f /usr/bin/cloudflared 2>/dev/null || echo "Binário /usr/bin/cloudflared não encontrado"
    sudo rm -f /opt/cloudflared/cloudflared 2>/dev/null || echo "Binário /opt/cloudflared/cloudflared não encontrado"
    
    # Remover diretório de instalação
    sudo rm -rf /opt/cloudflared 2>/dev/null || echo "Diretório /opt/cloudflared não encontrado"
    
    echo -e "${GREEN}✅ Binário do sistema removido!${NC}"
}

# Função para limpar cache e logs
clean_cache_logs() {
    echo -e "${BLUE}🧹 Limpando cache e logs...${NC}"
    
    # Limpar cache do Docker
    docker system prune -f 2>/dev/null || echo "Erro ao limpar cache do Docker"
    
    # Remover logs do cloudflared
    sudo rm -f /var/log/cloudflared.log 2>/dev/null || echo "Log do sistema não encontrado"
    sudo rm -f /var/log/cloudflared/* 2>/dev/null || echo "Logs do sistema não encontrados"
    
    echo -e "${GREEN}✅ Cache e logs limpos!${NC}"
}

# Função principal
main() {
    echo -e "${YELLOW}⚠️  ATENÇÃO: Este script irá remover completamente o Cloudflared!${NC}"
    echo "Isso inclui:"
    echo "- Containers Docker"
    echo "- Imagens Docker"
    echo "- Redes Docker"
    echo "- Arquivos de configuração"
    echo "- Binários do sistema"
    echo "- Serviços do sistema"
    echo ""
    
    read -p "Tem certeza que deseja continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${YELLOW}❌ Desinstalação cancelada.${NC}"
        exit 0
    fi
    
    echo ""
    echo -e "${BLUE}🚀 Iniciando desinstalação completa...${NC}"
    echo ""
    
    # Verificar Docker
    if check_docker; then
        remove_docker_containers
        remove_docker_images
        remove_docker_networks
        remove_docker_volumes
    fi
    
    # Parar serviços do sistema
    stop_system_services
    
    # Remover arquivos de configuração
    remove_config_files
    
    # Desinstalar binário do sistema
    uninstall_system_binary
    
    # Limpar cache e logs
    clean_cache_logs
    
    echo ""
    echo -e "${GREEN}✅ Desinstalação completa do Cloudflared concluída!${NC}"
    echo ""
    echo -e "${BLUE}📋 Resumo do que foi removido:${NC}"
    echo "• Containers Docker do Cloudflared"
    echo "• Imagens Docker do Cloudflared"
    echo "• Redes Docker do Cloudflared"
    echo "• Arquivos de configuração"
    echo "• Binários do sistema"
    echo "• Serviços do sistema"
    echo "• Cache e logs"
    echo ""
    echo -e "${YELLOW}💡 Dica: Se você quiser reinstalar o Cloudflared no futuro,${NC}"
    echo "   consulte a documentação oficial do Cloudflare."
}

# Executar função principal
main "$@" 
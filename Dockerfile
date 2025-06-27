# Usa uma imagem oficial do Python como base
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Atualiza pip e instala dependências Python
RUN pip install --upgrade pip && \
    pip install wheel setuptools && \
    pip install -r requirements.txt && \
    pip install pydantic-settings

# Copia todo o código da API para dentro do container
COPY . .

# Garante que as pastas de certificados e estáticos existam
RUN mkdir -p /app/certificates /app/static

# Expõe a porta usada pela API
EXPOSE 4200

# Comando para rodar a API (ajustado para usar SSL se os arquivos existirem)
CMD ["python", "run.py"]

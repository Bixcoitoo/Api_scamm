from pydantic import BaseModel, Field
from typing import List, Optional

class DadosBasicos(BaseModel):
    nome: str
    cpf: str
    nascimento: str
    nome_mae: str
    nome_pai: str
    sexo: str
    contatos_id: str

class Contatos(BaseModel):
    emails: List[str] = Field(default_factory=list)
    telefones: List[str] = Field(default_factory=list)

class Parente(BaseModel):
    grau: str
    cpf: str
    nome: str

class Financeiro(BaseModel):
    irpf: Optional[dict] = None
    poder_aquisitivo: Optional[dict] = None
    score: Optional[dict] = None

class Profissional(BaseModel):
    pis: Optional[str] = None
    profissao: Optional[dict] = None

class Educacao(BaseModel):
    instituicao: Optional[str] = None
    curso: Optional[str] = None
    ano_ingresso: Optional[int] = None

class DadosEleitorais(BaseModel):
    titulo: Optional[str] = None
    zona: Optional[str] = None
    secao: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None

class Endereco(BaseModel):
    tipo: str
    logradouro: str
    numero: str
    complemento: Optional[str]
    bairro: str
    cidade: str
    uf: str
    cep: str
    data_atualizacao: str
    data_inclusao: str
    tipo_endereco: str

class PessoaCompleta(BaseModel):
    dados_basicos: DadosBasicos
    contatos: Contatos = Field(default_factory=lambda: Contatos())
    enderecos: List[Endereco] = Field(default_factory=list)
    parentes: List[Parente] = Field(default_factory=list)
    financeiro: Financeiro = Field(default_factory=lambda: Financeiro())
    profissional: Profissional = Field(default_factory=lambda: Profissional())
    educacao: Optional[Educacao] = None
    eleitoral: Optional[DadosEleitorais] = None 
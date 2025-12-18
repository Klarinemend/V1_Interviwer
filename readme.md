
# Assistente de Engenharia de Requisitos com IA

> Um sistema interativo que utiliza o **Google Gemini** para realizar a elicitação de requisitos de software, atuando como um Engenheiro Sênior e gerando relatórios técnicos automatizados.

## Sobre o Projeto

Este projeto consiste em uma interface de chat desenvolvida em **Python** que conecta o usuário a uma instância personalizada do modelo Gemini (Google). O objetivo é auxiliar desenvolvedores, Product Owners e analistas na fase inicial de concepção de um software.

A IA não apenas responde a perguntas, mas conduz uma **entrevista ativa**, fazendo perguntas estratégicas para descobrir lacunas no escopo antes de gerar um documento final contendo:
*   Requisitos Funcionais (RF)
*   Requisitos Não-Funcionais (RNF)
*   Regras de Negócio
*   Sugestão de Stack Tecnológica

## Tecnologias Utilizadas

*   **[Python 3.x](https://www.python.org/)**: Linguagem base.
*   **[Google Generative AI SDK](https://ai.google.dev/)**: Para conexão com o modelo `gemini-1.5-flash`.
*   **[Streamlit](https://streamlit.io/)**: Para criação da interface web interativa (Chat UI).

## Como Executar

### 1. Pré-requisitos

Você precisa ter o Python instalado e uma chave de API do Google (gratuita).
*   Obtenha sua chave em: [Google AI Studio](https://aistudio.google.com/)

### 2. Instalação

Clone este repositório ou baixe os arquivos, depois instale as dependências:

```bash
pip install google-generativeai streamlit
```

### 3. Configuração

Abra o arquivo `app.py` e procure pela linha:

```python
API_KEY = AIzaSyC3b8SzRgbjat49CAzoxSuPY9wXTNJRlRI
```

Substitua o texto entre aspas pela sua chave obtida no passo 1.

### 4. Rodando a Aplicação

No terminal, dentro da pasta do projeto, execute:

```bash
streamlit run app.py
```

O navegador abrirá automaticamente no endereço `http://localhost:8501`.

## 💡 Como Usar

1.  **Inicie a conversa**: Digite no chat a ideia básica do seu software (ex: *"Quero criar um app de delivery de ração"*).
2.  **Responda a IA**: O assistente fará perguntas para entender melhor o escopo (ex: *"O app terá rastreamento em tempo real?", "Haverá pagamento online?"*).
3.  **Gere o Relatório**: Quando estiver satisfeito com as informações passadas, clique no botão **"📄 Gerar Relatório Final"** na barra lateral ou peça no chat *"Gere o relatório"*.
4.  **Copie o Resultado**: A IA fornecerá um documento estruturado pronto para ser usado na documentação do projeto.

## 📂 Estrutura do Projeto

```
/
├── app.py              # Código principal da aplicação
├── README.md           # Documentação do projeto
└── requirements.txt    # (Opcional) Lista de dependências
```

## ⚠️ Limitações e Avisos

*   **API Gratuita**: Este projeto utiliza a camada gratuita do Google AI Studio. Existem limites de requisições por minuto (RPM).
*   **Privacidade**: Evite inserir dados sensíveis ou confidenciais reais (senhas, segredos industriais), pois o modelo pode utilizar dados para treinamento na versão gratuita.
*   **Alucinação**: Embora instruída a ser técnica, a IA pode ocasionalmente inventar bibliotecas ou fatos. Sempre revise o relatório gerado.

## 📄 Licença

Este projeto é de uso livre para fins educacionais e de portfólio.

---

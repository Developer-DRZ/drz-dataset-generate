# Gerador de Dataset para Fine-Tuning do Qwen2.5:3B

Este projeto contém scripts Python para gerar um dataset de treinamento e realizar o fine-tuning do modelo Qwen2.5:3B, focado em um chatbot para a empresa AutoAvaliar.

## Sobre o Projeto

O dataset gerado simula conversas entre usuários e um assistente virtual chamado "Fulano" da empresa AutoAvaliar. As conversas são focadas em cenários onde os usuários estão interessados em comprar carros, fornecendo informações como marca, modelo, preço e estado.

## Requisitos

- Python 3.7+
- Bibliotecas Python:
  - google-generativeai
  - tqdm
  - requests
  - python-dotenv
  - transformers
  - torch
  - datasets
  - accelerate
  - colorama

## Instalação

1. Clone este repositório:
```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure sua chave de API do Google Gemini:
   - Obtenha uma chave de API em [Google AI Studio](https://ai.google.dev/)
   - Crie um arquivo `.env` na raiz do projeto (você pode copiar o arquivo `.env.example`)
   - Adicione sua chave de API no arquivo `.env`:
     ```
     GOOGLE_API_KEY=sua_chave_api_aqui
     ```

## Uso

### Executando Todos os Passos

Para executar todos os passos em sequência, use o script `run_all.py`:

```bash
python run_all.py
```

Este script irá:
1. Gerar o dataset
2. Analisar o dataset
3. Perguntar se você deseja visualizar o dataset
4. Perguntar se você deseja realizar o fine-tuning do modelo
5. Se você realizar o fine-tuning, perguntar se deseja testar o modelo

Você pode pular etapas específicas usando as opções:
- `--skip-generate`: Pula a geração do dataset
- `--skip-analyze`: Pula a análise do dataset
- `--skip-visualize`: Pula a visualização do dataset
- `--skip-finetune`: Pula o fine-tuning do modelo

### Geração do Dataset

Execute o script principal para gerar o dataset:

```bash
python generate_dataset.py
```

Por padrão, o script irá gerar 50 exemplos de conversas. Você pode modificar este número editando o parâmetro `num_examples` na chamada da função `generate_dataset()` no método `main()`.

### Análise do Dataset

Após gerar o dataset, você pode analisá-lo para verificar se está no formato correto:

```bash
python analyze_dataset.py
```

Este script carrega o dataset gerado e exibe estatísticas sobre ele, como o número de exemplos válidos, os campos presentes no ActionInput e o tamanho médio das conversas.

### Visualização do Dataset

Para visualizar os exemplos do dataset de forma interativa e colorida:

```bash
python visualize_dataset.py
```

Este script permite navegar pelos exemplos do dataset usando comandos simples:
- `n`: Próximo exemplo
- `p`: Exemplo anterior
- `r`: Exemplo aleatório
- `q`: Sair

Você pode especificar o arquivo de entrada com `--input`.

### Conversão do Dataset

Se você precisar converter o dataset para outros formatos, pode usar o script de conversão:

```bash
python convert_dataset.py --format json --output dataset.json
```

Formatos suportados:
- `json`: Converte para um arquivo JSON
- `csv`: Converte para um arquivo CSV
- `txt`: Salva cada exemplo em um arquivo de texto separado

Você pode especificar o arquivo de entrada com `--input` e o caminho de saída com `--output`.

### Fine-Tuning do Modelo

Após gerar e analisar o dataset, você pode realizar o fine-tuning do modelo Qwen2.5:3B usando o script de exemplo:

```bash
python finetune_example.py
```

Este script carrega o dataset gerado e realiza o fine-tuning do modelo Qwen2.5:3B. Você pode personalizar os parâmetros de treinamento editando as variáveis no início do script.

**Requisitos de Hardware**: O fine-tuning do modelo Qwen2.5:3B requer uma GPU com pelo menos 16GB de VRAM. Para GPUs com menos memória, considere usar técnicas como LoRA ou QLoRA para reduzir o consumo de memória.

### Testando o Modelo

Após o fine-tuning, você pode testar o modelo usando o script de teste:

```bash
python test_model.py
```

Este script inicia um chat interativo onde você pode conversar com o modelo fine-tuned e verificar se ele está respondendo corretamente no formato esperado.

## Saída

O script de geração do dataset gera dois tipos de saída:

1. **dataset.jsonl**: Um arquivo no formato JSONL contendo todos os exemplos gerados, pronto para ser usado no fine-tuning do modelo Qwen2.5:3B.

2. **Pasta "exemplos"**: Contém arquivos de texto individuais para cada exemplo, em um formato mais legível para humanos.

O script de fine-tuning salva o modelo treinado na pasta `./qwen2-finetuned`.

## Formato dos Exemplos

Cada exemplo no dataset segue o seguinte formato:

```json
{
  "memory": "Histórico da conversa até o momento",
  "user_input": "Mensagem atual do usuário",
  "output": "Resposta do assistente no formato especificado"
}
```

A resposta do assistente segue o formato:

```
Input: O input do usuário.  
Thought: Pensamento da LLM sobre o input do usuário.
ActionInput: Um JSON object com todos os parâmetros coletados para filtros.
NextAgent: ListingAgent
FinalResponse: "Movendo para o próximo agente".
```

## Personalização

Você pode personalizar o script de geração do dataset modificando:

- As listas de marcas e modelos de carros em `MARCAS` e `MODELOS`
- A lista de estados em `ESTADOS`
- O número de turnos de conversa em `generate_prompt(num_turns=3)`
- A faixa de preços dos carros em `generate_prompt()`

Para o script de fine-tuning, você pode personalizar:

- O modelo base em `MODEL_NAME`
- O diretório de saída em `OUTPUT_DIR`
- Os parâmetros de treinamento como `BATCH_SIZE`, `LEARNING_RATE`, `NUM_EPOCHS`, etc.

Para o script de teste, você pode personalizar:

- O caminho para o modelo fine-tuned em `MODEL_PATH`
- Os parâmetros de geração como `TEMPERATURE`, `TOP_P`, `TOP_K`, etc.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato

Para mais informações sobre a AutoAvaliar, visite [autoavaliar.com.br](https://autoavaliar.com.br). 
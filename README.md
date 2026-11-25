# Consultoria VN

Aplicativo de gerenciamento e acompanhamento de alunos para consultoria fitness, desenvolvido em Python com [Flet](https://flet.dev). Permite cadastrar alunos, registrar avaliações físicas periódicas e acompanhar a evolução de cada um.

## Funcionalidades

### Tela inicial
- Acesso rápido ao cadastro de alunos e à lista de alunos cadastrados.
- Card com a **quantidade de alunos ativos** e o total de cadastrados, atualizado sempre que a tela é aberta.

### Cadastro de aluno
- Campos obrigatórios: nome, altura (m), peso inicial (kg) e foco de resultado.
- Focos disponíveis: Emagrecimento, Ganho de massa muscular, Condicionamento físico, Definição muscular e Qualidade de vida.
- Campo opcional de **próxima avaliação** (DD/MM/AAAA).
- **Medidas corporais opcionais** no cadastro: cintura, abdômen, quadril, braço e coxa (cm). Elas são gravadas na avaliação inicial do aluno.
- Aceita números com vírgula ou ponto (ex.: `1,75` ou `1.75`).
- Validação dos campos, com mensagens de erro e de confirmação.
- A data de início e a avaliação inicial são criadas automaticamente.

### Lista de alunos
- Card por aluno com nome, altura, peso atual, foco, situação (ativo/inativo) e status da avaliação.
- Ações em cada card: **ver acompanhamento**, **editar** e **excluir**.
- A exclusão pede confirmação antes de remover o aluno.

### Acompanhamento do aluno
- Resumo com nome, altura, objetivo, situação, peso inicial, peso atual, data de início e próxima avaliação.
- **Histórico de avaliações**, da mais recente para a mais antiga, com peso, medidas corporais e observações.
- Registro de **nova avaliação** com data, peso, medidas (opcionais), observações e nova data de próxima avaliação.
- O peso atual sempre vem da avaliação mais recente, mesmo que uma avaliação antiga seja lançada depois.

### Edição de aluno
- Altera nome, altura, foco e próxima avaliação.
- Interruptor **Aluno ativo**, que define se o aluno entra na contagem do card da tela inicial.

### Status da avaliação
O status é calculado a partir da data de próxima avaliação:

| Status | Condição |
|---|---|
| Avaliação atrasada | A data é anterior a hoje |
| Avaliação próxima | A data é hoje ou está nos próximos 7 dias |
| Em dia | A data está a mais de 7 dias |
| Sem data definida | Nenhuma data informada |
| Data inválida | O valor salvo não é uma data reconhecível |

O status considera apenas a data. Ao registrar uma nova avaliação, atualize o campo de próxima avaliação, senão o aluno continua como atrasado.

### Armazenamento
- Os dados ficam no arquivo `lista_alunos.json`, na mesma pasta do programa. Ele é criado automaticamente na primeira execução.
- Cadastros antigos são adaptados ao formato atual sem perda de informações. Eles recebem histórico de avaliações, data de início e situação ativa.

## Como executar

Requisitos: Python 3 e uma versão recente do Flet (o código usa `ft.run`).

```bash
pip install flet
python consultoria_vn.py
```

## Estrutura dos dados

Exemplo de aluno em `lista_alunos.json`:

```json
{
    "nome": "Maria Silva",
    "altura": "1.65",
    "peso": "68.0",
    "peso_inicial": "72.0",
    "foco": "Emagrecimento",
    "ativo": true,
    "data_inicio": "2026-10-01",
    "proxima_avaliacao": "2026-12-15",
    "avaliacoes": [
        {
            "data": "2026-10-01",
            "peso": "72.0",
            "cintura": "80.0",
            "abdomen": "88.0",
            "quadril": "100.0",
            "braco": "30.0",
            "coxa": "58.0",
            "observacoes": "Avaliação inicial."
        }
    ]
}
```

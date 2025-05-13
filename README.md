# Automatização - Edeconsil

AUTOMAÇÃO - Edeconsil/
├── BOT/
│   ├── MEGATRON.py
│   ├── otimizer.py
│   ├── auxiliar.py
│   └── BASES/
│       ├── bot_BombaExterna - Ticketing.py
│       ├── bot_ForaHorario.py
│       ├── bot_ituran.py
│       ├── bot_ociosidade.py
│       └── bot_Velocidade.py
│
├── DATABASE/
│   ├── connection.py
│   ├── db.py
│   ├── execute.py
│   └── teste_brinks.py    # Script de teste de conexão com banco de dados
│
├── Sources/
    ├── LISTA DE MOTORISTAS POR CR - DB.xlsx
    ├── veiculos_e_equipamento - atualizar.xlsx
    └── veiculos_e_equipamento - bagunçar.xlsx

##### **MEGATRON.py**
- Arquivo principal para exportar para o AWS onde estam todos os bots juntos.

#### **otimizer.py**
- MEGATRON formatado e otimizado utilizando POO para um controle melhor.





## PONTOS A MELHORAR
1. Otimizar o otimizer para uma forma mais eficiente e mais rápida
   ###### Ideia de como melhorar:
      - Usar uma formato binário para acessar mais rápido. Dessa forma, ele não pecorrerar a lista várias vezes, ele vai ver o índice e se for "1" a coluna está presente, senão, ele não está.
      - Essa lista tem que ter todas as possivéis colunas justa nesse vetor, **SEM ALTERAÇÃO** de ordem.
  
      Ex.: ["DATA", "HORA", "TAG", "MOTORISTA"] -> [1, 1, 0, 1]
      Resumindo: As colunas DATA, HORA e MOTORISTA estão presente.
   
      ´´´python
      if lista[3]:
         df.execute()
      ´´´

3. Configuração do Banco de Dados para o MEGATRON enviar acessá-lo e armazenar nele.
   - Criar todas as tabelas que estamos trabalhando com o bot.
   - Fazer com o que ele busque as rows e altere o dataset para salvar no banco de dados
     
4. Avançar na criação dos outros bots, como Bomba interna e Gerenciarme

5. Tenha em mente que ainda iremos trabalha com **DOCKER** e **AWS**.




# PRAZO ***29 de Junho***

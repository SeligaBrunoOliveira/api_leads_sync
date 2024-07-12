## Descrição do Script
Este script é usado para buscar dados de leads a partir de várias APIs, armazená-los em um banco de dados SQL Server e manter as tabelas atualizadas com as informações mais recentes.
Ele utiliza a biblioteca SQLAlchemy para interagir com o banco de dados e a biblioteca requests para fazer chamadas às APIs.

## Importa as bibibliotecas necessárias 
![image](https://github.com/user-attachments/assets/a1b95b88-e47e-4d9f-bc28-e344e4ad2fd1)

## Etapas do Script

## Configuração da Conexão com o Banco de Dados:
![image](https://github.com/user-attachments/assets/370bb6b3-f804-46ee-ab45-a4e5c95e6cf0)

Define os parâmetros de conexão ao banco de dados, incluindo o tipo de banco de dados, servidor, nome do banco de dados e driver ODBC.

Cria uma string de conexão e um engine SQLAlchemy para conectar-se ao banco de dados.

## Verificação da Existência da Tabela:
![image](https://github.com/user-attachments/assets/0646b21c-b3ec-42c9-a9fa-de6b4596f184)

Conecta-se ao banco de dados e executa uma consulta SQL para verificar se a tabela Teste_Leads existe.

## Configuração da Sessão e Mapeamento Automático:
![image](https://github.com/user-attachments/assets/f30e4225-79b5-497a-b9f3-87c35dea3aa4)

Configura uma sessão SQLAlchemy para interagir com o banco de dados.
Utiliza automap_base para refletir as tabelas existentes no banco de dados e cria um mapeamento automático para a tabela Teste_Leads.

## Definição do Modelo para Nova Tabela:
![image](https://github.com/user-attachments/assets/445f4818-de7d-4a11-adaa-372eafa61984)

Define uma nova tabela chamada data_modification usando declarative_base. Esta tabela armazena a última modificação de dados e uma descrição.

## Função para Converter Strings de Data para Objetos Datetime:
![image](https://github.com/user-attachments/assets/8f5e48c4-f935-42b4-ab8b-35e946538212)

Define a função convert_to_datetime que tenta converter strings de data em objetos datetime utilizando diferentes formatos de data.

## Função para Adicionar Colunas a uma Tabela:
![image](https://github.com/user-attachments/assets/c9c179f1-7302-452e-b2f4-3419dd73e46f)

Define a função add_column que adiciona uma nova coluna a uma tabela existente no banco de dados.

## Função para Buscar e Atualizar Dados com Paginação:
![image](https://github.com/user-attachments/assets/7e66ab22-4eb0-4840-b495-b866bf6a08dd) ![image](https://github.com/user-attachments/assets/d7559fbe-1d88-4854-991e-50c8bb3adab2)
![image](https://github.com/user-attachments/assets/6cb4ec94-65ad-483e-b592-ad4f53ab4715)![image](https://github.com/user-attachments/assets/b8a71f25-0b9f-4c83-92c2-4dc5e2ee4cf2)

** Define a função fetch_and_update que:
Faz chamadas a uma API específica para buscar dados de leads.

Processa os dados recebidos, incluindo a conversão de campos de data e o tratamento de campos adicionais.

Verifica e adiciona novas colunas à tabela Teste_Leads conforme necessário.

Insere ou atualiza os dados no banco de dados.

Garante que todas as páginas de dados sejam processadas.

## Lista de Configurações de APIs:
![image](https://github.com/user-attachments/assets/d769e03c-7d81-4c01-94a3-5a1864c2ab58)

Define uma lista de configurações de APIs, cada uma contendo uma URL e um token de autenticação.

## Execução da Função de Atualização para Cada Configuração de API:
![image](https://github.com/user-attachments/assets/3730bbd7-93e4-435a-9756-905924f79387)

Itera sobre a lista de configurações de APIs e chama a função fetch_and_update para buscar e atualizar os dados para cada API.

## Atualização da Data de Modificação no Banco de Dados:
![image](https://github.com/user-attachments/assets/3ff75ef0-6505-4042-ab12-d0dd8eff9f3c)

Após processar todas as APIs, atualiza ou insere um registro na tabela data_modification para registrar a última data de modificação dos dados.

## Conclusão
Este script é uma ferramenta poderosa para integrar e sincronizar dados de leads de várias APIs em um banco de dados SQL Server, garantindo que as tabelas estejam sempre atualizadas com as informações mais recentes. Ele é altamente configurável e pode ser facilmente adaptado para diferentes fontes de dados e estruturas de banco de dados.

from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table, DDL, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.automap import automap_base
import requests
from datetime import datetime
import json
import time
from urllib.parse import urlparse

# Configuração da conexão com o banco de dados
DATABASE_TYPE = 'mssql+pyodbc'
SERVER = 'YOUR_SERVER'
DATABASE = 'YOUR_DATABASE'
DRIVER = 'ODBC Driver 17 for SQL Server'
CONNECTION_STRING = f"{DATABASE_TYPE}://{SERVER}/{DATABASE}?driver={DRIVER}"

engine = create_engine(CONNECTION_STRING)

with engine.connect() as connection:
    result = connection.execute(text("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Teste_Leads' AND TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_SCHEMA,TABLE_NAME;"))
    for row in result:
        print(f"Schema: {row.TABLE_SCHEMA}, Table: {row.TABLE_NAME}")

Session = sessionmaker(bind=engine)
session = Session()

# Utiliza automap_base para refletir tabelas existentes
AutomapBase = automap_base()
AutomapBase.prepare(autoload_with=engine)  # Atualizado para remover o parâmetro reflect depreciado

mapped_tables = {cls.__table__.name: cls for cls in AutomapBase.classes}

# Verifica se a tabela existe em AutomapBase.classes
if 'Teste_Leads' in mapped_tables:
    # Define o modelo LeadData usando automapping
    LeadData = mapped_tables['Teste_Leads']
else:
    raise Exception("Table 'Teste_Leads' not found in the database")

# Utiliza declarative_base para definir novas tabelas
DeclarativeBase = declarative_base()

class DataModification(DeclarativeBase):
    __tablename__ = 'data_modification'
    id = Column(Integer, primary_key=True)
    last_modification = Column(DateTime)
    cargo_description = Column(String)

# Cria tabelas definidas com DeclarativeBase
DeclarativeBase.metadata.create_all(engine)

def convert_to_datetime(date_str):
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']  # Adicione ou ajuste formatos conforme necessário
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt) if date_str else None
        except ValueError:
            continue
    print(f"Invalid date format: {date_str}")
    return None

def add_column(engine, table_name, column_name, column_type):
    with engine.connect() as conn:
        conn.execute(DDL(f'ALTER TABLE {table_name} ADD {column_name} {column_type};'))

# Função para buscar e atualizar dados com paginação
def fetch_and_update(api_config):
    # Analisa a URL para obter o domínio
    parsed_url = urlparse(api_config['url'])
    domain = parsed_url.netloc
    # Divide o domínio para obter a parte desejada, e.g., 'example' de 'example.com'
    cliente_url = domain.split('.')[0]
    # Obtém a última data de modificação para a descrição 'Api_leads'
    max_date_result = session.query(DataModification).filter_by(cargo_description="Api_leads").first()
    last_modification = max_date_result.last_modification if max_date_result else datetime(2000, 1, 1)

    pagina_atual = 1
    total_de_paginas = 1

    while pagina_atual <= total_de_paginas:
        params = {
            "pagina": pagina_atual,
            "registros_por_pagina": 500,
            #"a_partir_data_modificacao": last_modification.strftime("%Y-%m-%d")
        }
        headers = {
            'accept': 'application/json',
            'email': 'your.email@example.com',
            'token': api_config['token'],
            'Content-Type': 'application/json'
        }
        response = requests.get(api_config['url'], headers=headers, params=params)

        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Invalid JSON response from {api_config['url']}. Skipping and moving to the next URL...")
        except Exception as e:
            print(f"An error occurred while fetching data from {api_config['url']}: {str(e)}")
            # Opcionalmente, você pode registrar os detalhes do erro para fins de depuração
            print(f"Retrying after 20 seconds...")
            time.sleep(20)  # Aguarda 20 segundos antes de tentar novamente
            fetch_and_update(api_config)
            return

        leads = data.get('dados', [])
        if leads:
            all_field_names = set().union(*(d.keys() for d in leads))

            for field in all_field_names:
                if not hasattr(LeadData, field):
                    add_column(engine, LeadData.__table__.name, field, "VARCHAR(MAX)")  # Corrigido

            for item in leads:
                # Converte campos de data
                item['referencia_data'] = convert_to_datetime(item.get('referencia_data'))
                item['data_cad'] = convert_to_datetime(item.get('data_cad'))
                item['data_cancelamento'] = convert_to_datetime(item.get('data_cancelamento'))
                item['data_ultima_interacao'] = convert_to_datetime(item.get('data_ultima_interacao'))
                item['ultima_data_conversao'] = convert_to_datetime(item.get('ultima_data_conversao'))
                item['data_reativacao'] = convert_to_datetime(item.get('data_reativacao'))
                item['data_primeira_interacao_gestor'] = convert_to_datetime(item.get('data_primeira_interacao_gestor'))
                item['data_primeira_interacao_corretor'] = convert_to_datetime(item.get('data_primeira_interacao_corretor'))
                item['data_ult_hist'] = convert_to_datetime(item.get('data_ult_hist'))
                item['data_ultima_alteracao'] = convert_to_datetime(item.get('data_ultima_alteracao'))

                # Manipula campo campos_adicionais
                campos_adicionais_data = item.get('campos_adicionais')
                if campos_adicionais_data:
                    if isinstance(campos_adicionais_data, dict):
                        campos_adicionais_str = json.dumps(campos_adicionais_data)
                    else:
                        campos_adicionais_str = str(campos_adicionais_data)
                else:
                    campos_adicionais_str = None

                item_data = {k: v for k, v in item.items() if hasattr(LeadData, k)}
                item_data['campos_adicionais'] = campos_adicionais_str

                # Adiciona cliente_url a item_data
                item_data['cliente_url'] = cliente_url

                lead = LeadData(**item_data)
                session.merge(lead)

            session.commit()

            total_de_paginas = int(data.get('total_de_paginas', 1))
            print(f"Processed page {pagina_atual}/{total_de_paginas} from {cliente_url}")
            pagina_atual += 1
        else:
            print(f"No more data on page {pagina_atual}. Moving to next URL...")
            break

# Lista de configurações de APIs
api_configs = [
    {'url': 'https://example1.com/api/v1/cvdw/leads', 'token': 'your_token_1'},
    #{'url': 'https://example2.com/api/v1/cvdw/leads', 'token': 'your_token_2'},
    #{'url': 'https://example3.com/api/v1/cvdw/leads', 'token': 'your_token_3'},
    # Adicione mais configurações conforme necessário
]

# Busca e atualização de dados para cada configuração de API
for config in api_configs:
    fetch_and_update(config)

# Após processar todas as configurações de APIs
current_time = datetime.now()
max_date_result = session.query(DataModification).filter_by(cargo_description="Api_leads").first()

if max_date_result:
    # Atualiza o registro existente
    max_date_result.last_modification = current_time
    max_date_result.cargo_description = "Api_leads"
else:
    # Insere um novo registro
    new_record = DataModification(last_modification=current_time,
                                  cargo_description="Api_leads")
    session.add(new_record)

session.commit()

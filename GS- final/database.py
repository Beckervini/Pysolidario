from sqlalchemy import text
from datetime import datetime
from sqlalchemy import ForeignKey, MetaData
from sqlalchemy import create_engine, Column, String, Integer, Date, MetaData, Table, inspect, UniqueConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from excessoes import AuthenticationError


class Database:
    def __init__(self):
        self.engine = create_engine('oracle+oracledb://rm94679:090504@oracle.fiap.com.br?service_name=orcl', echo=False)  
        self.metadata = MetaData()
        self.session = sessionmaker(bind=self.engine)()

        self.create_tables()
    
    
    
    def create_tables(self):
        users_table = Table(
            'users',
            self.metadata,
            Column('cpf', String(20), primary_key=True),
            Column('nome', String(100)),
            Column('genero', String(20)),
            Column('num_telefone', String(20)),
            Column('escolaridade', String(50)),
            Column('dt_nasc', Date),
            Column('tipo_usuario', String(20)),
            Column('email', String(100)),
            Column('senha', String(50)),
            Column('cep', String(20)),
            Column('logradouro', String(100)),
            Column('bairro', String(50)),
            Column('complemento', String(100)),
            Column('numero', String(20)),
            Column('cidade', String(50)),
            Column('estado', String(20)),
        )

        self.metadata.create_all(self.engine)

        
        if not inspect(self.engine).has_table("patients"):
            patients_table = Table(
                'patients',
                self.metadata,
                Column('cpf', String(20), primary_key=True),
                Column('filhos', Integer),
                Column('ocupacao', String(50)),
                Column('estado_civil', String(20)),
                Column('num_niss', String(20)),
                extend_existing=True
            )
            patients_table.create(self.engine)

        
        if not inspect(self.engine).has_table("professionals"):
            professionals_table = Table(
                "professionals",
                self.metadata,
                Column("cpf", String(20), primary_key=True),
                Column("certificacao", String(50)),
                Column("formacao", String(50)),
                Column("cnpj", String(20)),
                extend_existing=True,
            )
            professionals_table.create(self.engine)

        if not inspect(self.engine).has_table("availability"):
            availability_table = Table(
            'availability',
            self.metadata,
            Column('cpf_professional', String(20), nullable=False),
            Column('professional_name', String(100), nullable=False),
            Column('appointment_date', Date, nullable=False),
            Column('appointment_time', String(5), nullable=False),  
            UniqueConstraint('cpf_professional', 'appointment_date', 'appointment_time'),
            extend_existing=True
            )   
            availability_table.create(self.engine)

        appointment_days_table = Table(
            'appointment_days',
            self.metadata,
            Column('cpf_patient', String(20), nullable=False),
            Column('appointment_day', Date, nullable=False),
            Column('appointment_time', String(5), nullable=False),
            UniqueConstraint('cpf_patient', 'appointment_day', 'appointment_time'),
            extend_existing=True
        )       

        try:
            appointment_days_table.create(self.engine, checkfirst=True)
        except Exception as e:
            print(f"Erro ao criar ou verificar tabela appointment_days_table: {e}")

        patient_appointments_table = Table(
            'patient_appointments',
            self.metadata,
            Column('cpf_patient', String(20), ForeignKey('users.cpf'), nullable=False),
            Column('cpf_professional', String(20), ForeignKey('users.cpf'), nullable=False),
            Column('appointment_day', Date, nullable=False),
            Column('appointment_time', String(5), nullable=False),
            Column('appointment_type', String(20), nullable=False),
            UniqueConstraint('cpf_patient', 'appointment_day', 'appointment_time'),
            extend_existing=True
        )

        professional_appointments_table = Table(
            'professional_appointments',
            self.metadata,
            Column('cpf_patient', String(20), ForeignKey('users.cpf'), nullable=False),
            Column('cpf_professional', String(20), ForeignKey('users.cpf'), nullable=False),
            Column('appointment_day', Date, nullable=False),
            Column('appointment_time', String(5), nullable=False),
            Column('appointment_type', String(20), nullable=False),
            UniqueConstraint('cpf_professional', 'appointment_day', 'appointment_time'),
            extend_existing=True
        )

        try:
            patient_appointments_table.create(self.engine, checkfirst=True)
            professional_appointments_table.create(self.engine, checkfirst=True)
        except Exception as e:
            print(f"Erro ao criar ou verificar tabelas de consultas: {e}")

    
    
    
    def register_user(self, data):
        try:
            user_data = {
                "cpf": data["cpf"],
                "nome": data["nome"],
                "genero": data["genero"],
                "num_telefone": data["num_telefone"],
                "escolaridade": data["escolaridade"],
                "dt_nasc": datetime.strptime(data["dt_nasc"], "%Y-%m-%d"),
                "tipo_usuario": data["tipo_usuario"],
                "email": data["email"],
                "senha": data["senha"],
                "cep": data["cep"],
                "logradouro": data["logradouro"],
                "bairro": data["bairro"],
                "complemento": data["complemento"],
                "numero": data["numero"],
                "cidade": data["cidade"],
                "estado": data["estado"],
            }

            self.session.execute(text("INSERT INTO users VALUES (:cpf, :nome, :genero, :num_telefone, :escolaridade, "
                                      ":dt_nasc, :tipo_usuario, :email, :senha, :cep, :logradouro, :bairro, "
                                      ":complemento, :numero, :cidade, :estado)"), user_data)

            if data["tipo_usuario"] in ["paciente", "Paciente"]:
                patient_data = {
                    "cpf": data["cpf"],
                    "filhos": data["filhos"],
                    "ocupacao": data["ocupacao"],
                    "estado_civil": data["estado_civil"],
                    "num_niss": data["num_niss"],
                    }
                self.session.execute(
                    text("INSERT INTO patients VALUES (:cpf, :filhos, :ocupacao, :estado_civil, :num_niss)"),
                    patient_data
                )
                self.session.commit()
            elif data["tipo_usuario"] in ["psicologo", "psicólogo", "psiquiatra"]:
                psychiatrist_data = {
                "cpf": data["cpf"],
                "certificacao": data["certificacao"],
                "formacao": data["formacao"],
                "cnpj": data["cnpj"],
                }
                self.session.execute(text("INSERT INTO professionals VALUES (:cpf, :certificacao, :formacao, :cnpj)"),
                                 psychiatrist_data)

                self.session.commit()

        except exc.IntegrityError:
            self.session.rollback()
            raise ValueError("CPF já cadastrado.")
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao cadastrar usuário: {e}")
            raise
        finally:
            self.close_connection()
    
    
    
    def login_profissional(self, cpf, senha):
        user_data = self.session.execute(
            text("SELECT cpf, nome, genero, num_telefone, escolaridade, dt_nasc, tipo_usuario, email FROM users WHERE cpf = :cpf AND senha = :senha AND tipo_usuario IN ('psicologo', 'psiquiatra')"),
            {"cpf": cpf, "senha": senha}
        ).fetchone()

        if user_data:
            keys = ["cpf", "nome", "genero", "num_telefone", "escolaridade", "dt_nasc", "tipo_usuario", "email"]
            user_dict = dict(zip(keys, user_data))
            return user_dict
        else:
            raise AuthenticationError("Profissional não encontrado ou senha incorreta.")
        
    def login_paciente(self, cpf, senha):
        user_data = self.session.execute(
            text("SELECT cpf, nome, genero, num_telefone, escolaridade, dt_nasc, tipo_usuario, email FROM users WHERE cpf = :cpf AND senha = :senha AND tipo_usuario = 'paciente'"),
            {"cpf": cpf, "senha": senha}
        ).fetchone()

        if user_data:
            keys = ["cpf", "nome", "genero", "num_telefone", "escolaridade", "dt_nasc", "tipo_usuario", "email"]
            user_dict = dict(zip(keys, user_data))
            return user_dict
        else:
            raise AuthenticationError("Paciente não encontrado ou senha incorreta.")
        
    def close_connection(self):
        if self.session:
            self.session.close()
            
        



    



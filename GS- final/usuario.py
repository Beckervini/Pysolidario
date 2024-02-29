from database import Database
from excessoes import InvalidOptionError, AuthenticationError
from funcoes import insert_appointment_day, insert_availability, get_valid_input, view_appointments, cancel_appointments, remove_availability

def register_user(db):
    try:
        print("\n=== Cadastro de Usuário ===")
        print("1. Cadastrar como Psicólogo")
        print("2. Cadastrar como Psiquiatra")
        print("3. Cadastrar como Paciente")

        choice = input("Escolha o tipo de usuário a ser cadastrado: ")

        if choice == '1':
            tipo_usuario = "psicologo"
        elif choice == '2':
            tipo_usuario = "psiquiatra"
        elif choice == '3':
            tipo_usuario = "paciente"
        else:
            raise InvalidOptionError("Opção inválida. Escolha novamente.")
        
        print("\n=== Cadastro de Usuário ===")
        cpf = get_valid_input("CPF: ", "cpf")
        nome = input("Nome: ")
        genero = get_valid_input("Gênero: ", "text")
        num_telefone = get_valid_input("Número de Telefone: ", "numeric")
        escolaridade = input("Escolaridade: ")
        dt_nasc = input("Data de Nascimento (YYYY-MM-DD): ")
        email = input("E-mail: ")
        senha = input("Senha: ")
        cep = get_valid_input("CEP: ", "numeric")
        logradouro = input("Logradouro: ")
        bairro = input("Bairro: ")
        complemento = input("Complemento: ")
        numero = get_valid_input("Número: ", "numeric")
        cidade = input("Cidade: ")
        estado = input("Estado: ")

        data = {
            "cpf": cpf,
            "nome": nome,
            "genero": genero,
            "num_telefone": num_telefone,
            "escolaridade": escolaridade,
            "dt_nasc": dt_nasc,
            "tipo_usuario": tipo_usuario,
            "email": email,
            "senha": senha,
            "cep": cep,
            "logradouro": logradouro,
            "bairro": bairro,
            "complemento": complemento,
            "numero": numero,
            "cidade": cidade,
            "estado": estado,
        }

        if tipo_usuario == "paciente":
            filhos = get_valid_input("Número de Filhos: ", "numeric")
            ocupacao = input("Ocupação: ",)
            estado_civil = get_valid_input("Estado Civil: ", "text")
            num_niss = get_valid_input("Número do NISS: ", "numeric")
            data.update({
                "filhos": filhos,
                "ocupacao": ocupacao,
                "estado_civil": estado_civil,
                "num_niss": num_niss,
            })
        elif tipo_usuario == "psicologo" or "psiquiatra":
            certificacao = input("Certificação: ")
            formacao = input("Formação: ")
            cnpj = get_valid_input("CNPJ: ", "numeric")
            data.update({
                "certificacao": certificacao,
                "formacao": formacao,
                "cnpj": cnpj,
            })

        db.register_user(data)
        print("Usuário cadastrado com sucesso!")

    except Exception as e:
        print(f"Erro ao cadastrar usuário: {e}")


def login_professional(db):
    try:
        print("\n=== Login Profissional ===")
        cpf = input("CPF: ")
        senha = input("Senha: ")

        result_profissional = db.login_profissional(cpf, senha)
        print("Login bem-sucedido! Dados do Profissional:")
        print("CPF:", result_profissional["cpf"])
        print("Nome:", result_profissional["nome"])
        print("Cargo:", result_profissional["tipo_usuario"])
        print("email:", result_profissional["email"])

        tipo_usuario_profissional = result_profissional["tipo_usuario"]
        profissional_logado = result_profissional["nome"]

        while True:
            print("\n=== Opções do Profissional ===")
            print("1. Inserir Disponibilidade")
            print("2. Visualizar Consultas")
            print("3. Cancelar Consultas")
            print("4. Excluir dinsponibilidade")
            print("5. Voltar ao Menu Principal")

            choice = input("Escolha a opção: ")

            if choice == '1':
                insert_availability(db, cpf)
            elif choice == '2':
                view_appointments(db, cpf, tipo_usuario_profissional)
            elif choice == '3':
                cancel_appointments(db, cpf, tipo_usuario_profissional, profissional_logado)
            elif choice == '4':
                remove_availability(db, cpf)
            elif choice == '5':
                break
            else:
                raise InvalidOptionError("Opção inválida. Escolha novamente.")

    except AuthenticationError as ae:
        print(f"Erro de autenticação: {ae}")
    except Exception as e:
        print(f"Erro ao fazer login como profissional: {e}")

def login_patient(db):
    try:
        print("\n=== Login Paciente ===")
        cpf = input("CPF: ")
        senha = input("Senha: ")

        result_paciente = db.login_paciente(cpf, senha)
        
        if result_paciente:
            print("Login bem-sucedido! Dados do Paciente:")
            print("CPF:", result_paciente["cpf"])
            print("Nome:", result_paciente["nome"])
            print("email:", result_paciente["email"])
        else:
            print("Usuario ou senha incorreta.")
        
        tipo_usuario_paciente = result_paciente["tipo_usuario"]
        nome_do_profissional_logado = None

        while True:
            print("\n=== Opções do Paciente ===")
            print("1. Inserir Dia de Atendimento")
            print("2. Visualizar Consultas")
            print("3. Cancelar Consultas")
            print("4. Voltar ao Menu Principal")

            choice = input("Escolha a opção: ")

            if choice == '1':
                insert_appointment_day(db, cpf)
            elif choice == '2':
                view_appointments(db, cpf, "paciente")
            elif choice == '3':
                cancel_appointments(db, cpf, tipo_usuario_paciente, nome_do_profissional_logado)
            elif choice == '4':
                break
            else:
                raise InvalidOptionError("Opção inválida. Escolha novamente.")

    except AuthenticationError as ae:
        print(f"Erro de autenticação: {ae}")
    except Exception as e:
        print(f"Erro ao fazer login como paciente: {e}")
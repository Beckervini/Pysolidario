from database import Database
from excessoes import InvalidOptionError
from usuario import register_user, login_patient, login_professional
#Rm945679 Vinicius Becker, rm550562 Larissa Akemi, rm552292 Julia Nery, 
#rm552389 Isabelli Heloiza, rm98163 Julia Martins
#LINK DO VIDEO: https://youtu.be/wLKYCJd4hkE
def main():
    db = Database()

    try:
        while True:
            print("\n=== Menu Principal ===")
            print("1. Cadastrar Usuário")
            print("2. Entrar como Profissional")
            print("3. Entrar como Paciente")
            print("4. Sair")

            choice = input("Escolha a opção: ")

            if choice == '1':
                register_user(db)
            elif choice == '2':
                login_professional(db)
            elif choice == '3':
                login_patient(db)
            elif choice == '4':
                break
            else:
                raise InvalidOptionError("Opção inválida. Escolha novamente.")
    except Exception as e:
        print(f"Erro não tratado: {e}")
    finally:
        db.close_connection()



if __name__ == "__main__":
    main()
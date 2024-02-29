from database import Database
import excessoes
from sqlalchemy import text, Interval
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import re


def insert_availability(db, cpf):
    try:
        print("\n=== Inserir Disponibilidade ===")

        professional_name = db.session.execute(
            text("SELECT nome FROM users WHERE cpf = :cpf"),
            {"cpf": cpf}
        ).scalar()

        date_str = input("Data desejada para atendimento (YYYY-MM-DD): ")
        time_str = input("Horário: ")

        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(time_str, "%H:%M").strftime("%H:%M")  

        result = db.session.execute(
            text('INSERT INTO availability (cpf_professional, professional_name, appointment_date, appointment_time) VALUES (:cpf_professional, :professional_name, :appointment_date, :appointment_time)'),
            {"cpf_professional": cpf, "professional_name": professional_name, "appointment_date": appointment_date, "appointment_time": appointment_time}
        )
        db.session.commit()

        print("Disponibilidade inserida com sucesso!")

    except IntegrityError as e:
        db.session.rollback()
        if "ORA-00001" in str(e):
            print("Erro ao inserir disponibilidade: A disponibilidade já existe para este profissional na data e horário especificados. Escolha um horário diferente.")
        else:
            print(f"Erro ao inserir disponibilidade: {e}")
        raise

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inserir disponibilidade: {e}")
        raise


def insert_appointment_day(db, cpf):
    try:
        print("\n=== Inserir Dia de Atendimento ===")

        professional_name = db.session.execute(
            text("SELECT nome FROM users WHERE cpf = :cpf"),
            {"cpf": cpf}
        ).scalar()

        appointment_day_str = input("Dia desejado para atendimento (YYYY-MM-DD): ")
        appointment_time_str = input("Horário: ")

        appointment_day = datetime.strptime(appointment_day_str, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(appointment_time_str, "%H:%M").strftime("%H:%M")  

        availability_result = db.session.execute(
            text('SELECT cpf_professional FROM availability WHERE appointment_date = :appointment_date AND appointment_time = :appointment_time'),
            {"appointment_date": appointment_day, "appointment_time": appointment_time}
        ).fetchone()

        if availability_result:
            cpf_professional = availability_result[0]

            appointment_data_patient = {
                "cpf_patient": cpf,
                "cpf_professional": cpf_professional,
                "appointment_day": appointment_day,
                "appointment_time": appointment_time,
                "appointment_type": "Paciente",
            }

            appointment_data_professional = {
                "cpf_patient": cpf,
                "cpf_professional": cpf_professional,
                "appointment_day": appointment_day,
                "appointment_time": appointment_time,
                "appointment_type": "Profissional",
            }

            db.session.execute(
                text('INSERT INTO patient_appointments VALUES (:cpf_patient, :cpf_professional, :appointment_day, :appointment_time, :appointment_type)'),
                appointment_data_patient
            )

            db.session.execute(
                text('INSERT INTO professional_appointments VALUES (:cpf_patient, :cpf_professional, :appointment_day, :appointment_time, :appointment_type)'),
                appointment_data_professional
            )

            db.session.commit()

            print(f"Atendimento marcado com sucesso para o paciente {professional_name} no dia {appointment_day_str} às {appointment_time_str}.")
        else:
            db.session.rollback()
            print("Não foi possível marcar o atendimento. Verifique a disponibilidade do profissional.")

    except IntegrityError as e:
        db.session.rollback()
        if "ORA-00001" in str(e):
            print("Erro ao inserir dia de atendimento: O paciente já possui um agendamento para o dia e horário especificados.")
        else:
            print(f"Erro ao inserir dia de atendimento: {e}")
        raise

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inserir dia de atendimento: {e}")
        raise


def get_valid_input(prompt, input_type):
    while True:
        user_input = input(prompt)
        if input_type == "cpf" and user_input.isdigit():
            return user_input
        elif input_type == "numeric" and user_input.isdigit():
            return user_input
        elif input_type == "text" and user_input.isalpha():
            return user_input
        else:
            print("Entrada inválida. Por favor, insira um valor válido.")

def view_appointments(db, cpf, tipo_usuario):
    try:
        print("\n=== Visualizar Consultas ===")

        if tipo_usuario in ["psicologo", "psiquiatra"]:
            appointments = db.session.execute(
                text("SELECT a.appointment_day, a.appointment_time, a.appointment_type, u.nome as paciente_nome FROM professional_appointments a JOIN users u ON a.cpf_patient = u.cpf WHERE a.cpf_professional = :cpf"),
                {"cpf": cpf}
            ).fetchall()

            for appointment in appointments:
                print("Paciente:", appointment[3])
                print("Data:", appointment[0])
                print("Horário:", appointment[1])
                print("Tipo:", appointment[2])
                print("Profissional:", tipo_usuario)  
                print("------------")

        elif tipo_usuario == "paciente":
            appointments = db.session.execute(
                text("SELECT a.appointment_day, a.appointment_time, a.appointment_type, u.nome as medico_nome, u.tipo_usuario FROM patient_appointments a JOIN users u ON a.cpf_professional = u.cpf WHERE a.cpf_patient = :cpf"),
                {"cpf": cpf}
            ).fetchall()

            for appointment in appointments:
                print("Médico:", appointment[3])
                print("Data:", appointment[0])
                print("Horário:", appointment[1])
                print("Tipo:", appointment[2])
                print("Profissional:", appointment[4])  
                print("------------")

        else:
            print("Tipo de usuário não reconhecido.")

    except Exception as e:
        print(f"Erro ao visualizar consultas: {e}")
    finally:
        db.session.close()


def cancel_appointments(db, cpf, tipo_usuario, nome_do_profissional_logado):
    try:
        print("\n=== Cancelar Consultas ===")

        if tipo_usuario == "paciente":
            appointments_table_name = "patient_appointments"
            user_cpf_column = "cpf_patient"
        elif tipo_usuario in ["psicologo", "psiquiatra"]:
            appointments_table_name = "professional_appointments"
            user_cpf_column = "cpf_professional"
        else:
            print("Tipo de usuário não reconhecido.")
            return

        # Consulta para obter os agendamentos do usuário
        appointments = db.session.execute(
            text(f"SELECT appointment_day, appointment_time FROM {appointments_table_name} WHERE {user_cpf_column} = :cpf"),
            {"cpf": cpf}
        ).fetchall()

        if not appointments:
            print("Nenhum agendamento encontrado para cancelar.")
            return

        print("\n=== Seus Agendamentos ===")
        for i, appointment in enumerate(appointments, start=1):
            print(f"{i}. Data: {appointment[0]}, Horário: {appointment[1]}")

        # Escolha do usuário para cancelar um agendamento
        num_agendamento = input("Escolha o número do agendamento que deseja cancelar (ou '0' para voltar ao menu anterior): ")

        if num_agendamento == '0':
            return  # Voltar ao menu anterior

        num_agendamento = int(num_agendamento) - 1

        # Obtendo os detalhes do agendamento a ser cancelado
        appointment_day, appointment_time = appointments[num_agendamento]

        # Cancelamento do agendamento na tabela patient_appointments
        db.session.execute(
            text(f"DELETE FROM {appointments_table_name} WHERE {user_cpf_column} = :cpf AND appointment_day = :appointment_day AND appointment_time = :appointment_time"),
            {"cpf": cpf, "appointment_day": appointment_day, "appointment_time": appointment_time}
        )

        # Cancelamento do dia na tabela professional_appointments
        db.session.execute(
            text(f"DELETE FROM professional_appointments WHERE cpf_professional = :cpf AND appointment_day = :appointment_day"),
            {"cpf": cpf, "appointment_day": appointment_day}
        )

        db.session.commit()

        print("Consulta cancelada com sucesso!")

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao cancelar consulta: {e}")
        raise
    finally:
        db.session.close()



def remove_availability(db, cpf):
    try:
        print("\n=== Remover Disponibilidade ===")

        
        availability = db.session.execute(
            text("SELECT appointment_date, appointment_time FROM availability WHERE cpf_professional = :cpf"),
            {"cpf": cpf}
        ).fetchall()

        if not availability:
            print("Nenhuma disponibilidade encontrada para remover.")
            return

        print("\n=== Sua Disponibilidade ===")
        for i, entry in enumerate(availability, start=1):
            print(f"{i}. Data: {entry[0]}, Horário: {entry[1]}")

      
        num_disponibilidade = input("Escolha o número da disponibilidade que deseja remover (ou '0' para voltar ao menu anterior): ")

        if num_disponibilidade == '0':
            return  

        num_disponibilidade = int(num_disponibilidade) - 1

      
        appointment_date, appointment_time = availability[num_disponibilidade]

        
        db.session.execute(
            text("DELETE FROM availability WHERE cpf_professional = :cpf AND appointment_date = :appointment_date AND appointment_time = :appointment_time"),
            {"cpf": cpf, "appointment_date": appointment_date, "appointment_time": appointment_time}
        )

        db.session.commit()

        print("Disponibilidade removida com sucesso!")

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao remover disponibilidade: {e}")
        raise
    finally:
        db.session.close()
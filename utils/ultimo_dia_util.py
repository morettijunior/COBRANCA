import calendar
from config import feriados
from datetime import date, timedelta

# 1. Função para gerar os fins de semana do mês atual e do mês anterior
def gerar_fins_de_semana_atual_e_anterior():
    hoje = date.today()
    ano = hoje.year
    mes = hoje.month
    
    # Calcula o mês anterior lidando com a virada de ano (Janeiro -> Dezembro)
    if mes == 1:
        mes_anterior = 12
        ano_anterior = ano - 1
    else:
        mes_anterior = mes - 1
        ano_anterior = ano
        
    lista_fds = []
    
    periodos = [
        (ano_anterior, mes_anterior),
        (ano, mes)
    ]
    
    for a, m in periodos:
        _, ultimo_dia = calendar.monthrange(a, m)
        for dia in range(1, ultimo_dia + 1):
            data_atual = date(a, m, dia)
            # 5 = Sábado, 6 = Domingo
            if data_atual.weekday() in (5, 6):
                lista_fds.append(data_atual)
                
    # Transformamos em set para otimizar e agilizar a busca
    return set(lista_fds)

# 2. Função para encontrar o último dia útil anterior a uma data de referência
def obter_ultimo_dia_util_anterior(data_referencia=None, conjunto_fds=None, conjunto_feriados=None):
    if data_referencia is None:
        data_referencia = date.today()
        
    if conjunto_fds is None:
        conjunto_fds = gerar_fins_de_semana_atual_e_anterior()
        
    if conjunto_feriados is None:
        conjunto_feriados = set()
        
    # Começa a testar a partir do dia imediatamente anterior a hoje
    dia_teste = data_referencia - timedelta(days=1)
    
    # Retrocede enquanto for final de semana ou feriado
    while dia_teste in conjunto_fds or dia_teste in conjunto_feriados:
        dia_teste -= timedelta(days=1)
        
    return dia_teste

# ==========================================
# Execução Principal / Testes
# ==========================================
if __name__ == "__main__":
    hoje = date.today()
    fim_de_semana = gerar_fins_de_semana_atual_e_anterior()
    
    ultimo_util = obter_ultimo_dia_util_anterior(
        data_referencia=hoje, 
        conjunto_fds=fim_de_semana, 
        conjunto_feriados=feriados
    )
    
    print(f"Data de Hoje: {hoje.strftime('%d/%m/%Y')}")
    print(f"O último dia útil anterior é: {ultimo_util.strftime('%d/%m/%Y')}")
    print(ultimo_util)
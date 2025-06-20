from iqoptionapi.stable_api import IQ_Option
import time, pandas as pd

EMAIL = "jonathanpedroo@hotmail.com"
SENHA = "2022goleiro"
VALOR = 10
TIMEFRAME = 1  # minutos
api = IQ_Option(EMAIL, SENHA)
api.connect()
api.change_balance("PRACTICE")

def get_melhor_par():
    pares = api.get_all_open_time()
    payout = api.get_all_profit()
    abertos = {p: payout[p]['turbo'] for p in pares['turbo'] if pares['turbo'][p]['open']}
    return max(abertos, key=abertos.get)

def coletar_candles(par):
    velas = api.get_candles(par, 60, 100, time.time())
    df = pd.DataFrame(velas)
    df['media'] = df['close'].rolling(3).mean()
    return df

def zigzag_simplificado(df):
    df['zigzag'] = 0
    for i in range(2, len(df)-2):
        if df['close'][i] > df['close'][i-2] and df['close'][i] > df['close'][i+2]:
            df.at[i, 'zigzag'] = 1  # topo
        elif df['close'][i] < df['close'][i-2] and df['close'][i] < df['close'][i+2]:
            df.at[i, 'zigzag'] = -1  # fundo
    return df

def price_action(df):
    ult = df.iloc[-1]
    ant = df.iloc[-2]
    if ant['close'] < ant['open'] and ult['close'] > ult['open'] and ult['open'] < ant['close']:
        return "engolfo_alta"
    elif ant['close'] > ant['open'] and ult['close'] < ult['open'] and ult['open'] > ant['close']:
        return "engolfo_baixa"
    return None

def entrar(direcao, par):
    print(f"ENTRADA: {direcao} em {par}")
    status, id = api.buy(VALOR, par, direcao, TIMEFRAME)
    print("SUCESSO" if status else "FALHOU")

print("Robô iniciado...")

while True:
    try:
        par = get_melhor_par()
        df = coletar_candles(par)
        df = zigzag_simplificado(df)
        padrao = price_action(df)

        if df['zigzag'].iloc[-2] == -1 and padrao == "engolfo_alta":
            entrar("call", par)
        elif df['zigzag'].iloc[-2] == 1 and padrao == "engolfo_baixa":
            entrar("put", par)

        time.sleep(60)

    except Exception as e:
        print("Erro:", e)
        time.sleep(10)

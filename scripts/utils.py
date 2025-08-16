def calcular_juros(valor_parcela, vencimento):
    from datetime import date

    # taxa de juros diaria (exemplo: 0,33% ao dia) 0,0033
    taxa_diaria = 0.33 / 100

    # data_atual
    data_atual = date.today()

    # calcular dias de atraso. OBS: nao precisa converter a data pois ela ja vem no formato datetime
    dias_atraso = (data_atual - vencimento).days

    if dias_atraso > 0:
        int_valor_parcela = int(valor_parcela * 100)
        juros_centavos = int(int_valor_parcela * taxa_diaria * dias_atraso)

        return f'{juros_centavos / 100:.2f}'

    return None

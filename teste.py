# def calcular_icms_normal(valor_produto, aliquota):
#     icms = valor_produto * (aliquota / 100)
#     return icms
#
#
# def calcular_bc_st(valor, quantidade):
#     bc = valor * quantidade
#     return bc
#
#
# def calcular_icms_st(bc, aliquota, icms):
#     icmsst = (bc * aliquota / 100) - icms
#     return icmsst
#
#
# valor_total_produto = float(input("Digite o valor total do produto: "))
# aliquota_normal = float(input("Digite a aliquota ICMS normal: "))
# preco_tabelado = float(input("Digite o preco tabelado: "))
# quantidade = float(input("Digite a quantidade: "))
# aliquota_st = float(input("Digite a aliquota ST: "))
#
# icms_normal = calcular_icms_normal(valor_total_produto, aliquota_normal)
# bc_st = calcular_bc_st(preco_tabelado, quantidade)
# icms_st = calcular_icms_st(bc_st, aliquota_st, icms_normal)
#
# print("-=" * 20)
# print(f'ICMS normal {icms_normal:.2f}')
# print(f'Base ST {bc_st:.2f}')
# print(f'ICMS ST {icms_st:.2f}')
# print("-=" * 20)


# from datetime import datetime, date
#
# conta = {
#     'valor': 500.00,
#     'data_vencimento': '08/06/2025'
# }
#
# # taxa de juros diária (exemplo: 0.33% ao dia)
# taxa_diaria = 0.33 / 100
#
# # data atual
# data_atual = date.today()
#
# # converter string para date
# data_vencimento = datetime.strptime(conta['data_vencimento'], '%d/%m/%Y').date()
#
# # calcular dias de atraso
# dias_atraso = (data_atual - data_vencimento).days
#
# if dias_atraso > 0:
#     juros = conta['valor'] * taxa_diaria * dias_atraso
#     valor_total = conta['valor'] + juros
#     print(f"Dias de atraso: {dias_atraso}")
#     print(f"Juros: R$ {juros:.2f}")
#     print(f"Total a pagar: R$ {valor_total:.2f}")
# else:
#     print("Conta ainda não está vencida.")


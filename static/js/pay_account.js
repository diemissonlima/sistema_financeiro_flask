document.addEventListener("DOMContentLoaded", function () {
    const parcela = document.getElementById("valor_parcela");
    const desconto = document.getElementById("valor_desconto");
    const valorJuros = document.getElementById("valor_juros");
    const valorMulta = document.getElementById("valor_multa");
    const valorRecebido = document.getElementById("valor_recebido");
    const saldoInput = document.getElementById("valor_saldo");
    const saldoPagar = document.getElementById("saldo_pagar");

    function parseValor(input) {
        let valor = String(input.value ?? "")
        .replace(/[^\d,.-]/g, "")   // remove R$, espaços e letras
        .replace(/\.(?=\d{3},)/g, "") // remove pontos de milhar (só os que estão antes de 3 dígitos e vírgula)
        .replace(",", ".")          // troca vírgula decimal por ponto
        .trim();

        let numero = parseFloat(valor);
        return isNaN(numero) ? 0 : numero;
    }

    function atualizarSaldo() {
        let vParcela = parseValor(parcela);
        let vDesconto = parseValor(desconto);
        let vJuros = parseValor(valorJuros);
        let vMulta = parseValor(valorMulta);
        let vRecebido = parseValor(valorRecebido);
        let vSaldoPagar = parseValor(saldoPagar);

        console.log(vSaldoPagar);

        let saldo = (vSaldoPagar + vMulta - vDesconto) - vRecebido;
        saldoInput.value = saldo.toFixed(2).replace(".", ",");
    }

    // Adiciona escutadores em todos os campos relevantes
    [parcela, desconto, valorJuros, valorMulta, valorRecebido].forEach(el => {
        el.addEventListener("input", atualizarSaldo);
    });

    // Atualiza no carregamento
    atualizarSaldo();
});

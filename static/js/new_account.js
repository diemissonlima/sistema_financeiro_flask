// Mudar cor do tipo baseado na seleção
document.getElementById('type').addEventListener('change', function() {
    const typeSelect = this;
    const amountInput = document.getElementById('amount');

    if (typeSelect.value === 'pagar') {
        amountInput.className = 'form-control border-danger';
    } else if (typeSelect.value === 'receber') {
        amountInput.className = 'form-control border-success';
    } else {
        amountInput.className = 'form-control';
    }
});

// filtro do modal de fornecedores
  document.getElementById("buscaFornecedor").addEventListener("input", function() {
    const termo = this.value.toLowerCase();
    const itens = document.querySelectorAll("#modalFornecedores tbody tr");

    itens.forEach(item => {
      const texto = item.textContent.toLowerCase();
      item.style.display = texto.includes(termo) ? "" : "none";
    });
  });

// funcao que preenche o campo do fornecedor
function selecionarFornecedor(id, nome) {
    document.getElementById('fornecedorId').value = id;
    document.getElementById('fornecedor').value = nome;
    var modal = bootstrap.Modal.getInstance(document.getElementById('modalFornecedores'));
    modal.hide();
}

// gerar parcelas caso o a forma de pagamento seja a prazo
document.querySelector('#form-parcelas button[type="submit"]').addEventListener('click', function (e) {
    e.preventDefault();

    const intervaloDias = parseInt(document.getElementById('intervalo_dias').value);
    const valor = parseFloat(document.getElementById('amount').value);
    const qtd = parseInt(document.getElementById('quantidade_parcelas').value);
    const dataInicio = new Date(document.getElementById('data_lancamento').value);
    const areaParcelas = document.getElementById('area-parcelas');

    const parcelas = [];

    // Valor base sem arredondar
    const valorBase = valor / qtd;

    // Array inicial com valores arredondados
    for (let i = 0; i < qtd; i++) {
        parcelas.push({
            numero: i + 1,
            valor: parseFloat(valorBase.toFixed(2)), // arredonda
            vencimento: null
        });
    }

    // Ajuste da diferença de centavos
    let somaParcelas = parcelas.reduce((acc, p) => acc + p.valor, 0);
    let diferenca = parseFloat((valor - somaParcelas).toFixed(2));

    let i = 0;
    while (diferenca !== 0) {
        parcelas[i].valor = parseFloat((parcelas[i].valor + (diferenca > 0 ? 0.01 : -0.01)).toFixed(2));
        somaParcelas = parcelas.reduce((acc, p) => acc + p.valor, 0);
        diferenca = parseFloat((valor - somaParcelas).toFixed(2));
        i = (i + 1) % qtd;
    }

    // Define as datas de vencimento
    for (let i = 0; i < qtd; i++) {
        let vencimento = new Date(dataInicio);
        vencimento.setDate(dataInicio.getDate() + intervaloDias * (i + 1));
        parcelas[i].vencimento = vencimento.toISOString().split('T')[0];
    }

    preencherTabela(parcelas);
    areaParcelas.style.display = 'block';
});


function preencherTabela(parcelas) {
    const tbody = document.querySelector('#area-parcelas tbody');
    const container = document.getElementById('hidden-inputs-container');
    tbody.innerHTML = '';
    container.innerHTML = '';

    parcelas.forEach((p, index) => {
        const linha = `<tr>
            <td>${p.numero}</td>
            <td>R$ ${p.valor}</td>
            <td>${new Date(p.vencimento).toLocaleDateString('pt-BR')}</td>
        </tr>`;
        tbody.innerHTML += linha;

        // adiciona inputs ocultos para enviar no form
        const inputNumero = `<input type="hidden" name="parcelas[${index}][numero]" value="${p.numero}">`;
        const inputValor = `<input type="hidden" name="parcelas[${index}][valor]" value="${p.valor}">`;
        const inputVencimento = `<input type="hidden" name="parcelas[${index}][vencimento]" value="${p.vencimento}">`;

        container.innerHTML += inputNumero + inputValor + inputVencimento;
    });
}

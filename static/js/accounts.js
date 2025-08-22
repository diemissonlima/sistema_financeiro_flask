document.addEventListener("DOMContentLoaded", function () {
  const filtroDescricao = document.getElementById("filtroDescricao");
  const filtroFornecedor = document.getElementById("filtroFornecedor");
  const filtroStatus = document.getElementById("filtroStatus");
  const filtroDataDe = document.getElementById("filtroDataDe");
  const filtroDataAte = document.getElementById("filtroDataAte");

  const linhas = document.querySelectorAll("table tbody tr");

  function aplicarFiltros() {
    const desc = filtroDescricao.value.toLowerCase();
    const fornecedor = filtroFornecedor.value.toLowerCase();
    const status = filtroStatus.value;
    const dataDe = filtroDataDe.value;
    const dataAte = filtroDataAte.value;

    linhas.forEach((linha) => {
      const td = linha.querySelectorAll("td");

      const textoDescricao = td[0]?.innerText.toLowerCase();
      const textoFornecedor = td[6]?.innerText.toLowerCase();
      const textoStatus = td[7]?.innerText;
      const textoData = td[3]?.innerText; // formato: dd/mm/yyyy

      let mostra = true;

      if (desc && !textoDescricao.includes(desc)) mostra = false;
      if (fornecedor && !textoFornecedor.includes(fornecedor)) mostra = false;
      if (status && !textoStatus.includes(status)) mostra = false;

      if ((dataDe || dataAte) && textoData) {
        const [dia, mes, ano] = textoData.split("/");
        const dataLinha = new Date(`${ano}-${mes}-${dia}`);
        const dataMin = dataDe ? new Date(dataDe) : null;
        const dataMax = dataAte ? new Date(dataAte) : null;

        if (dataMin && dataLinha < dataMin) mostra = false;
        if (dataMax && dataLinha > dataMax) mostra = false;
      }

      linha.style.display = mostra ? "" : "none";
    });
  }

  [filtroDescricao, filtroFornecedor, filtroStatus, filtroDataDe, filtroDataAte].forEach((el) => {
    el.addEventListener("input", aplicarFiltros);
    el.addEventListener("change", aplicarFiltros);
  });
});

document.querySelectorAll("button[data-account-id]").forEach(btn => {
    btn.addEventListener("click", () => {
        const accountId = btn.dataset.accountId;
        const tipoConta = btn.dataset.tipoConta;

        fetch(`/get_account_info/${tipoConta}/${accountId}`)
            .then(response => response.json())
            .then(data => {

                const tbody = document.querySelector("#modalDetalhesParcela tbody");
                tbody.innerHTML = "";

                data.forEach(item => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${item.descricao_pagamento}</td>
                            <td>${item.recebido}</td>
                            <td>${new Date(item.data_recebimento).toLocaleDateString('pt-BR')}</td>
                            <td>
                                <button type="button" class="btn btn-sm btn-danger" style="width: 95px"
                                   data-id-recebimento=${item.id} data-id_conta=${item.id_contas_pagar}>
                                    <i class="fas fa-xmark me-1"></i>
                                    Estornar
                                </button>
                            </td>
                        </tr>`
                })
            })
    });
});

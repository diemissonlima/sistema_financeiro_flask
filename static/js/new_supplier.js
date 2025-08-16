// consulta de CNPJ
document.querySelector('#form_fornecedor button[type="submit"]').addEventListener('click', function (e) {
    e.preventDefault();

    const valorCNPJ = document.getElementById('cnpj').value.replace(/\D/g, ''); // remove caracteres não numéricos

    if (valorCNPJ.length !== 14) {
        alert("CNPJ inválido. Digite 14 números.");
        return;
    }

    fetch(`/get_supplier_data/${valorCNPJ}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro na consulta do CNPJ.");
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            document.getElementById('name').value = data.nome || '';
            document.getElementById('fantasia').value = data.fantasia || '';
            document.getElementById('email').value = data.email || '';
            document.getElementById('phone').value = data.telefone || '';
            document.getElementById('endereco').value = data.logradouro || '';
            document.getElementById('numero').value = data.numero || '';
            document.getElementById('bairro').value = data.bairro || '';
            document.getElementById('cep').value = data.cep || '';
            document.getElementById('municipio').value = data.municipio || '';
            document.getElementById('estado').value = data.uf || '';
        })
        .catch(error => {
            console.log.error(error);
            alert("Erro ao buscar os dados do fornecedor.");
        });
});

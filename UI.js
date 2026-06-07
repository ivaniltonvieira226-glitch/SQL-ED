const API = "http://localhost:8000";

// Variável principal de estado da aplicação. Começa vazia.
let livros = [];

const output = document.getElementById("output");
const forms = document.getElementById("forms");
const buttons = document.getElementById("buttons");

// ===============================================
// Renderização Auxiliar e Lógica Principal
// ===============================================

// Função auxiliar que apenas desenha os livros que receber como argumento
function renderizarLista(listaLivros) {
    output.innerHTML = "";
    
    // Trata caso a API retorne um erro ou um objeto único de livro ao invés de lista
    if (!Array.isArray(listaLivros)) {
        if (listaLivros && !listaLivros.detail) {
            listaLivros = [listaLivros]; // Transforma em array se for um livro só
        } else {
            output.innerHTML = "<p style='color: red;'>Nenhum livro encontrado ou critério inválido.</p>";
            return;
        }
    }

    if (listaLivros.length === 0) {
        output.innerHTML = "<p>Nenhum livro para exibir.</p>";
        return;
    }

    listaLivros.forEach(livro => {
        const div = document.createElement("div");
        div.innerHTML = `
            <h3>${livro.titulo}</h3>
            ${livro.id ? `<p>ID: ${livro.id}</p>` : ''}
            ${livro.autor ? `<p>Autor: ${livro.autor}</p>` : ''}
            <p>Ano: ${livro.ano}</p>
            ${livro.paginas ? `<p>Páginas: ${livro.paginas}</p>` : ''}
            <p>Status: ${livro.status}</p>
            ${livro.pagina_atual !== undefined ? `<p>Página Atual: ${livro.pagina_atual}</p>` : ''}
            <hr>
        `;
        output.appendChild(div);
    });
}

async function carregarLivros() {
    forms.innerHTML = ""; // Limpa os formulários abertos
    const resposta = await fetch(`${API}/livros`);
    livros = await resposta.json();
    renderizarLista(livros);
}

// ===============================================
// Formulário de Adicionar Livro
// ===============================================
async function mostrarFormularioAdicionar() {
    forms.innerHTML = `
    <h3>Adicionar Livro</h3>
    <form id="addForm">
        <input id="titulo" placeholder="Título" required>
        <input id="autor" placeholder="Autor" required>
        <input id="ano" type="number" placeholder="Ano" required>
        <input id="pagina" type="number" placeholder="Páginas" required>
        <select id="status">
            <option>LENDO</option>
            <option>CONCLUIDO</option>
            <option>NAO_LIDO</option>
            <option>ABANDONADO</option>
        </select>
        <input id="paginaAtual" type="number" placeholder="Página Atual" required>
        <button type="submit">Salvar</button>
    </form>
    `;

    document.getElementById("addForm").addEventListener("submit", async e => {
        e.preventDefault();

        const livro = {
            titulo: document.getElementById("titulo").value,
            autor: document.getElementById("autor").value,
            ano: Number(document.getElementById("ano").value),
            pagina: Number(document.getElementById("pagina").value), // Alinhado com o backend 'pagina'
            status: document.getElementById("status").value,
            pagina_atual: Number(document.getElementById("paginaAtual").value)
        };

        const resposta = await fetch(`${API}/livros`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(livro)
        });

        const dados = await resposta.json();
        alert(dados.mensagem || dados.detail);
        carregarLivros();
    });
}

// ===============================================
// Formulário de Atualizar Livro
// ===============================================
function mostrarFormularioAtualizar() {
    forms.innerHTML = `
    <h3>Atualizar Leitura</h3>
    <form id="updateForm">
        <input id="idLivro" type="number" placeholder="ID" required>
        <select id="novoStatus">
            <option>LENDO</option>
            <option>CONCLUIDO</option>
            <option>NAO_LIDO</option>
            <option>ABANDONADO</option>
        </select>
        <input id="novaPagina" type="number" placeholder="Página Atual" required>
        <button type="submit">Atualizar</button>
    </form>
    `;

    document.getElementById("updateForm").addEventListener("submit", async e => {
        e.preventDefault();

        const id = Number(document.getElementById("idLivro").value);
        const status = document.getElementById("novoStatus").value;
        const pagina = Number(document.getElementById("novaPagina").value);

        const resposta = await fetch(`${API}/livros/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                status: status,
                pagina_atual: pagina
            })
        });

        const dados = await resposta.json();
        if (!resposta.ok) {
            alert(`Erro: ${dados.detail}`);
        } else {
            alert(dados.mensagem);
            carregarLivros();
        }
    });
}

// ===============================================
// Formulário de Remoção
// ===============================================
function mostrarFormularioRemover() {
    forms.innerHTML = `
    <h3>Remover Livro</h3>
    <form id="deleteForm">
        <input id="deleteId" type="number" placeholder="ID" required>
        <button type="submit">Remover</button>
    </form>
    `;

    document.getElementById("deleteForm").addEventListener("submit", async e => {
        e.preventDefault();

        const id = Number(document.getElementById("deleteId").value);

        const resposta = await fetch(`${API}/livros/${id}`, {
            method: "DELETE"
        });
        
        const dados = await resposta.json();
        alert(dados.mensagem || dados.detail);
        carregarLivros();
    });
}

// ===============================================
// Formulário de Buscar por ID
// ===============================================
async function buscarPorId() {
    const id = prompt("Digite o ID:");
    if (!id) return;

    const resposta = await fetch(`${API}/livros/id/${id}`);
    const livro = await resposta.json();
    
    renderizarLista(livro);
}

// ===============================================
// Central de Ano: Filtrar e Ordenar (Mesmo Lugar)
// ===============================================
function mostrarFormularioAno() {
    forms.innerHTML = `
    <h3>Filtros e Ordenação por Ano</h3>
    <div id="anoFormGroup" style="display: flex; flex-direction: column; gap: 10px; max-width: 300px;">
        <input id="anoFiltro" type="number" placeholder="Digite o ano para filtrar">
        
        <button id="btnFiltrar">🔍 Filtrar por este Ano</button>
        <div style="display: flex; gap: 10px;">
            <button id="btnCresc" style="flex: 1;">⬆️ Ano Crescente</button>
            <button id="btnDesc" style="flex: 1;">⬇️ Ano Decrescente</button>
        </div>
    </div>
    `;

    // Ação 1: Filtrar por Ano específico
    document.getElementById("btnFiltrar").addEventListener("click", async () => {
        const ano = document.getElementById("anoFiltro").value;
        if (!ano) {
            alert("Por favor, digite um ano para filtrar.");
            return;
        }
        const resposta = await fetch(`${API}/livros/ano/${ano}`);
        const dados = await resposta.json();
        renderizarLista(dados);
    });

    // Ação 2: Ordenar Crescente
    document.getElementById("btnCresc").addEventListener("click", async () => {
        const resposta = await fetch(`${API}/livros/ordenar/cresc`);
        const dados = await resposta.json();
        renderizarLista(dados);
    });

    // Ação 3: Ordenar Decrescente
    document.getElementById("btnDesc").addEventListener("click", async () => {
        const resposta = await fetch(`${API}/livros/ordenar/desc`);
        const dados = await resposta.json();
        renderizarLista(dados);
    });
}

// ===============================================
// Actions e Event Listener Principal
// ===============================================

const actions = {
    listarLivros: carregarLivros,
    adicionarLivros: mostrarFormularioAdicionar,
    buscarId: buscarPorId,
    atualizarLeitura: mostrarFormularioAtualizar,
    removerLivro: mostrarFormularioRemover,
    FiltrarAno: mostrarFormularioAno,
    clear: () => { output.innerHTML = ""; forms.innerHTML = ""; }
};

buttons.addEventListener("click", (event) => {
    if (event.target.tagName === 'BUTTON') {
        const action = event.target.dataset.action;
        if (action && actions[action]) {
            actions[action]();
        }
    }
});
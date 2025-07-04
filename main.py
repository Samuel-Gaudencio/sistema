import os
from fasthtml.common import *
from supabase import create_client, Client
from dotenv import load_dotenv

# Inicializa o aplicativo e as rotas
app, rts = fast_app()

# Rota para a página inicial
@rts("/")
def homepage():
    return Titled("Estoque", render_form(), render_product_list())


# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Cria um cliente Supabase usando as credenciais armazenadas
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Função para renderizar o formulário de cadastro de produto
def render_form():
    form = Form(
        Fieldset(
            Input(type="text", name="nomeProduto", placeholder="Nome Do Produto", required=True),
            Input(type="number", name="quantidadeEstoque", placeholder="Quantidade Do Produto", required=True),
            Input(type="number", name="preco", placeholder="Preço Do Produto", required=True, step="any"),
            Input(type="text", placeholder="Link da Foto do Produto", name="fotoProduto", required=True),
            Button("Cadastrar Produto", type="submit", cls="secondary"),
        ),
        method="post",
        hx_post="/cadastrar-produto",
        hx_target='#product-list',
        hx_swap='outerHTML',
        hx_on__after_request="this.reset()"
    )
    return form

# Função para renderizar o formulário de edição de produto
def render_edit_form(entry):
    form = Form(
        Fieldset(
            Input(type="hidden", name="id", value=entry['id']),
            Input(type="text", name="nomeProduto", value=entry['nomeProduto'], required=True),
            Input(type="number", name="quantidadeEstoque", value=entry['quantidadeEstoque'], required=True),
            Input(type="number", name="preco", value=entry['preco'], required=True, step="any"),
            Input(type="text", placeholder="Link da Foto do Produto", name="fotoProduto", value=entry['fotoProduto'], required=True),
            Button("Salvar Alterações", type="submit", cls="secondary"),
        ),
        method="post",
        hx_post="/editar-produto",
        hx_target="#product-list",
        hx_swap="outerHTML",
    )
    return form

# Função para renderizar um único produto
def render_product(entry):
    return (
        Article(
            Img(src=f"{entry['fotoProduto']}", width=200, height=200, alt="Foto do Produto"),
            Footer(f"Produto: {entry['nomeProduto']}", Br(),
                   f"Preço: R$ {entry['preco']:,.2f}", Br(),
                   f"Quantidade em Estoque: {entry['quantidadeEstoque']}", Br(),
                   A("Excluir Produto", cls="contrast", hx_delete=f"/deletar/{entry['id']}", hx_target="#product-list", hx_swap="outerHTML"), Br(),
                   A("Editar Produto", cls="contrast", hx_get=f"/editar/{entry['id']}", hx_target=f"#edit-form-{entry['id']}", hx_swap='innerHTML'), Br(),
                   Div(id=f"edit-form-{entry['id']}", cls="edit-form")
                   ),
        )
    )

# Função para adicionar um produto ao banco de dados
def add_product(nomeProduto, quantidadeEstoque, preco, fotoProduto):
    supabase.table("sistema").insert(
        {"nomeProduto": nomeProduto, "fotoProduto": fotoProduto, "preco": preco, "quantidadeEstoque": quantidadeEstoque}
    ).execute()

# Função para deletar um produto do banco de dados
def pop_product(id_product):
    supabase.table("sistema").delete().eq('id', id_product).execute()

# Função para atualizar um produto no banco de dados
def update_product(id_product, nomeProduto, quantidadeEstoque, preco, fotoProduto):
    supabase.table("sistema").update(
        {"nomeProduto": nomeProduto, "fotoProduto": fotoProduto, "preco": preco, "quantidadeEstoque": quantidadeEstoque}
    ).eq('id', id_product).execute()

# Função para obter todos os produtos do banco de dados
def get_produtc():
    response = (
        supabase.table("sistema").select("*").execute()
    )
    return response.data

# Função para renderizar a lista de produtos
def render_product_list():
    products = get_produtc()
    return Div(
        *[render_product(entry) for entry in products],
        id="product-list",
    )


# Rota para cadastrar um produto
@rts("/cadastrar-produto", methods=["post"])
def post(nomeProduto: str, quantidadeEstoque: int, preco: float, fotoProduto: str):
    add_product(nomeProduto, quantidadeEstoque, preco, fotoProduto)
    return render_product_list()

# Rota para deletar um produto
@rts("/deletar/{id}")
def delete(id: int):
    pop_product(id)
    return render_product_list()

# Rota para editar um produto
@rts("/editar-produto", methods=["post"])
def post_edit(id: int, nomeProduto: str, quantidadeEstoque: int, preco: float, fotoProduto: str):
    update_product(id, nomeProduto, quantidadeEstoque, preco, fotoProduto)
    return render_product_list()

# Rota para mostrar o formulário de edição
@rts("/editar/{id}")
def edit(id: int):
    entry = supabase.table("sistema").select("*").eq('id', id).execute().data[0]
    return render_edit_form(entry)

# Inicia o servidor
serve()

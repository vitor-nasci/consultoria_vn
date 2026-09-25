
import json
import os
import flet as ft

# Descobre a pasta onde este arquivo Python está localizado
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# Define o caminho completo do arquivo JSON
NOME_ARQUIVO = os.path.join(
    DIRETORIO_ATUAL,
    "lista_alunos.json"
)

def carregar_dados():
    # Verifica se o arquivo JSON existe
    if not os.path.exists(NOME_ARQUIVO):
        # Se não existir, cria o arquivo com uma lista vazia
        with open(NOME_ARQUIVO, "w", encoding="utf-8") as arq:
            json.dump([], arq, indent=4, ensure_ascii=False)
        return []

    # Se o arquivo existir, tenta carregar os dados
    try:
        with open(NOME_ARQUIVO, "r", encoding="utf-8") as arq:
            return json.load(arq)
    except (json.JSONDecodeError, OSError):
        return []

def salvar_dados(lista_alunos):
    # Salva a lista de alunos no arquivo JSON.
    with open(NOME_ARQUIVO, "w", encoding="utf-8") as arq:
        json.dump(lista_alunos, arq, indent=4, ensure_ascii=False)

def main(page: ft.Page):
    # CONFIGURAÇÕES DA JANELA
    page.title = "Consultoria VN"
    page.window.width = 500
    page.window.height = 650
    page.window.resizable = False
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    # CARREGAR ALUNOS
    alunos = carregar_dados()

    # TELA PRINCIPAL
    def tela_inicio():
        page.clean()
        cabecalho = ft.Column(
            controls=[
                ft.Text(
                    "CONSULTORIA VN",
                    size=28,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Gerenciamento de alunos",
                    size=16
                ),
                ft.Divider()
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
   
        # BOTÕES
        botoes = ft.Column(
            controls=[
                ft.TextButton(
                    "Cadastrar Aluno",
                    icon=ft.Icons.PERSON_ADD,
                    width=250,
                    on_click=lambda e: tela_cadastro()
                ),
                ft.TextButton(
                    "Alunos Cadastrados",
                    icon=ft.Icons.PEOPLE,
                    width=250,
                    on_click=lambda e: tela_alunos()
                )
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

        )

        # LAYOUT DA PÁGINA
        page.add(
            ft.Column(
                controls=[
                    cabecalho,
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        content=botoes
                    )
                ],
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        page.update()

    # TELA DE CADASTRO
    def tela_cadastro():
        page.clean()
        campo_nome = ft.TextField(
            label="Nome do aluno",
            hint_text="Digite o nome completo",
            width=400
        )
        campo_altura = ft.TextField(
            label="Altura (m)",
            hint_text="Ex: 1.75",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400
        )
        campo_peso = ft.TextField(
            label="Peso (kg)",
            hint_text="Ex: 70",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400
        )
        campo_foco = ft.Dropdown(
            label="Foco de resultado",
            width=400,
            options=[
                ft.dropdown.Option("Emagrecimento"),
                ft.dropdown.Option("Ganho de massa muscular"),
                ft.dropdown.Option("Condicionamento físico"),
                ft.dropdown.Option("Definição muscular"),
                ft.dropdown.Option("Qualidade de vida")
            ]
        )

        mensagem_erro = ft.Text(
            "",
            size=14,
            color=ft.Colors.RED_400
        )

        mensagem_confirmacao = ft.Text(
                    "",
                    size=14,
                    color=ft.Colors.RED_400
                )
        # CADASTRAR ALUNO
        def cadastrar_aluno(e):
            nome = campo_nome.value.strip()
            altura = campo_altura.value.strip()
            peso = campo_peso.value.strip()
            foco = campo_foco.value

            # Verificação dos campos
            if not nome or not altura or not peso or not foco:
                mensagem_erro.value = "Preencha todos os campos."
                mensagem_erro.color = ft.Colors.RED_400
                page.update()
                return

            # Cria o aluno
            novo_aluno = {
                "nome": nome,
                "altura": altura,
                "peso": peso,
                "foco": foco
            }
            # Adiciona o aluno à lista
            alunos.append(novo_aluno)
            salvar_dados(alunos)

            # Mensagem de confirmação
            if  nome and altura and peso and foco:
                mensagem_erro.value = ""
                mensagem_confirmacao.value = "Aluno cadastrado com sucesso!"
                mensagem_confirmacao.color = ft.Colors.GREEN_400
                page.update()
                return

            # Limpa os campos
            campo_nome.value = ""
            campo_altura.value = ""
            campo_peso.value = ""
            campo_foco.value = None

        # INTERFACE
        page.add(
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Voltar",
                        on_click=lambda e: tela_inicio()
                    ),
                    ft.Text(
                        "Cadastro de Aluno",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),
            ft.Divider(),
            campo_nome,
            campo_altura,
            campo_peso,
            campo_foco,
            mensagem_erro,
            mensagem_confirmacao,
            ft.TextButton(
                "Cadastrar",
                icon=ft.Icons.SAVE,
                width=400,
                on_click=cadastrar_aluno
            )
        )

        page.update()

    # TELA DE ALUNOS
    def tela_alunos():
        page.clean()

        lista_view = ft.ListView(
            expand=True,
            spacing=10
        )

        # EXIBIR ALUNOS
        def renderizar_alunos():
            lista_view.controls.clear()
            if not alunos:
                lista_view.controls.append(
                    ft.Text(
                        "Nenhum aluno cadastrado.",
                        size=16
                    )
                )
            for index, aluno in enumerate(alunos):

                # EXCLUIR ALUNO
                def excluir_aluno(e, idx=index):
                    alunos.pop(idx)
                    salvar_dados(alunos)
                    renderizar_alunos()

                # EDITAR ALUNO
                def editar_aluno(e, idx=index):
                    abrir_edicao(idx)

                # CARD DO ALUNO
                card = ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    aluno["nome"],
                                    size=18,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(
                                    f"Altura: {aluno['altura']} m"
                                ),
                                ft.Text(
                                    f"Peso: {aluno['peso']} kg"
                                ),
                                ft.Text(
                                    f"Foco: {aluno['foco']}"
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT,
                                            tooltip="Editar",
                                            on_click=editar_aluno
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED_400,
                                            tooltip="Excluir",
                                            on_click=excluir_aluno
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )

                lista_view.controls.append(card)

            page.update()

        # EDITAR ALUNO
        def abrir_edicao(index):
            aluno = alunos[index]
            campo_nome = ft.TextField(
                label="Nome",
                value=aluno["nome"]
            )
            campo_altura = ft.TextField(
                label="Altura",
                value=aluno["altura"]
            )
            campo_peso = ft.TextField(
                label="Peso",
                value=aluno["peso"]
            )
            campo_foco = ft.Dropdown(
                label="Foco de resultado",
                value=aluno["foco"],
                options=[
                    ft.dropdown.Option("Emagrecimento"),
                    ft.dropdown.Option("Ganho de massa muscular"),
                    ft.dropdown.Option("Condicionamento físico"),
                    ft.dropdown.Option("Definição muscular"),
                    ft.dropdown.Option("Qualidade de vida")
                ]
            )

            # SALVAR EDIÇÃO
            def salvar_edicao(e):
                alunos[index]["nome"] = campo_nome.value.strip()
                alunos[index]["altura"] = campo_altura.value.strip()
                alunos[index]["peso"] = campo_peso.value.strip()
                alunos[index]["foco"] = campo_foco.value

                salvar_dados(alunos)
                dialogo.open = False
                renderizar_alunos()
                page.update()

            # FECHAR DIÁLOGO
            def fechar_dialogo(e):
                dialogo.open = False
                page.update()

            # DIÁLOGO
            dialogo = ft.AlertDialog(
                title=ft.Text("Editar aluno"),
                content=ft.Column(
                    controls=[
                        campo_nome,
                        campo_altura,
                        campo_peso,
                        campo_foco
                    ],
                    tight=True
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=fechar_dialogo
                    ),
                    ft.TextButton(
                        "Salvar",
                        on_click=salvar_edicao
                    )
                ]
            )
            page.overlay.append(dialogo)
            dialogo.open = True
            page.update()

        # INTERFACE DA TELA
        page.add(
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Voltar",
                        on_click=lambda e: tela_inicio()
                    ),
                    ft.Text(
                        "Alunos Cadastrados",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),
            ft.Divider(),
            lista_view
        )
        renderizar_alunos()

    # INICIAR SISTEMA
    tela_inicio()

if __name__ == "__main__":
    ft.run(main)


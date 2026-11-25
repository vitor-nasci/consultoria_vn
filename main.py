import json
import os
from datetime import date, datetime, timedelta
import flet as ft

# Descobre a pasta onde este arquivo Python está localizado
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# Define o caminho completo do arquivo JSON
NOME_ARQUIVO = os.path.join(
    DIRETORIO_ATUAL,
    "lista_alunos.json"
)

# Medidas corporais usadas no cadastro e nas avaliações
MEDIDAS = [
    ("cintura", "Cintura (cm)"),
    ("abdomen", "Abdômen (cm)"),
    ("quadril", "Quadril (cm)"),
    ("braco", "Braço (cm)"),
    ("coxa", "Coxa (cm)"),
]

OPCOES_FOCO = [
    "Emagrecimento",
    "Ganho de massa muscular",
    "Condicionamento físico",
    "Definição muscular",
    "Qualidade de vida",
]


def carregar_dados():
    # Verifica se o arquivo JSON existe
    if not os.path.exists(NOME_ARQUIVO):
        with open(NOME_ARQUIVO, "w", encoding="utf-8") as arq:
            json.dump([], arq, indent=4, ensure_ascii=False)
        return []

    try:
        with open(NOME_ARQUIVO, "r", encoding="utf-8") as arq:
            dados = json.load(arq)

        # Adapta os cadastros antigos ao novo formato, sem perder informações
        for aluno in dados:
            if "peso_inicial" not in aluno:
                aluno["peso_inicial"] = aluno.get("peso", "")
            if "avaliacoes" not in aluno:
                aluno["avaliacoes"] = []
                if aluno.get("peso"):
                    aluno["avaliacoes"].append({
                        "data": aluno.get("data_inicio", date.today().isoformat()),
                        "peso": aluno["peso"],
                        "cintura": "",
                        "abdomen": "",
                        "quadril": "",
                        "braco": "",
                        "coxa": "",
                        "observacoes": "Registro inicial importado do cadastro antigo."
                    })
            if "data_inicio" not in aluno:
                aluno["data_inicio"] = date.today().isoformat()
            if "proxima_avaliacao" not in aluno:
                aluno["proxima_avaliacao"] = ""
            # Cadastros antigos são considerados ativos
            if "ativo" not in aluno:
                aluno["ativo"] = True

        return dados

    except (json.JSONDecodeError, OSError):
        return []


def salvar_dados(lista_alunos):
    # Salva a lista de alunos no arquivo JSON
    with open(NOME_ARQUIVO, "w", encoding="utf-8") as arq:
        json.dump(lista_alunos, arq, indent=4, ensure_ascii=False)


def data_para_exibicao(data_texto):
    if not data_texto:
        return "Não definida"
    try:
        return datetime.strptime(data_texto, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data_texto


def classificar_avaliacao(data_texto):
    if not data_texto:
        return "Sem data definida"
    try:
        data_avaliacao = datetime.strptime(data_texto, "%Y-%m-%d").date()
        hoje = date.today()
        if data_avaliacao < hoje:
            return "Avaliação atrasada"
        if data_avaliacao <= hoje + timedelta(days=7):
            return "Avaliação próxima"
        return "Em dia"
    except ValueError:
        return "Data inválida"


def cor_status(status):
    cores = {
        "Avaliação atrasada": ft.Colors.RED_400,
        "Avaliação próxima": ft.Colors.AMBER_400,
        "Em dia": ft.Colors.GREEN_400,
    }
    return cores.get(status, ft.Colors.GREY_400)


def converter_numero(valor):
    return float(valor.strip().replace(",", "."))


def ler_medidas(campos):
    """Lê os campos de medidas (opcionais). Levanta ValueError se algum for inválido."""
    medidas = {}
    for nome, campo in campos.items():
        valor = (campo.value or "").strip()
        if valor:
            numero = converter_numero(valor)
            if numero <= 0:
                raise ValueError
            medidas[nome] = str(numero)
        else:
            medidas[nome] = ""
    return medidas


def peso_atual_do(aluno):
    avaliacoes = aluno.get("avaliacoes", [])
    if avaliacoes:
        return avaliacoes[-1].get("peso", aluno.get("peso", ""))
    return aluno.get("peso", "")


def main(page: ft.Page):
    # CONFIGURAÇÕES DA JANELA
    page.title = "Consultoria VN"
    page.window.width = 600
    page.window.height = 720
    page.window.resizable = False
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    # CARREGAR ALUNOS
    alunos = carregar_dados()

    def mostrar_dialogo(dialogo):
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def fechar_dialogo(dialogo):
        dialogo.open = False
        page.update()

    # TELA PRINCIPAL
    def tela_inicio():
        page.clean()

        total = len(alunos)
        ativos = sum(1 for a in alunos if a.get("ativo", True))

        cabecalho = ft.Column(
            controls=[
                ft.Text(
                    "CONSULTORIA VN",
                    size=28,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Gerenciamento e acompanhamento de alunos",
                    size=14
                ),
                ft.Divider()
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

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
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Card com a quantidade de alunos ativos (parte inferior da tela)
        card_ativos = ft.Card(
            content=ft.Container(
                padding=15,
                width=320,
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.GROUP, size=44),
                        ft.Column(
                            controls=[
                                ft.Text(str(ativos), size=30, weight=ft.FontWeight.BOLD),
                                ft.Text("Alunos ativos", size=14),
                                ft.Text(f"{total} cadastrados no total", size=12, color=ft.Colors.GREY_400)
                            ],
                            spacing=2
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            )
        )

        page.add(
            ft.Column(
                controls=[
                    cabecalho,
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Column(
                            controls=[
                                botoes,
                                ft.Container(height=15),
                                card_ativos
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            tight=True
                        )
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
            label="Peso inicial (kg)",
            hint_text="Ex: 70",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400
        )
        campo_foco = ft.Dropdown(
            label="Foco de resultado",
            width=400,
            options=[ft.dropdown.Option(o) for o in OPCOES_FOCO]
        )
        campo_proxima = ft.TextField(
            label="Próxima avaliação (DD/MM/AAAA)",
            hint_text="Ex: 15/12/2026",
            width=400
        )

        # Medidas corporais (opcionais)
        campos_medidas = {
            nome: ft.TextField(
                label=rotulo,
                keyboard_type=ft.KeyboardType.NUMBER,
                width=195
            )
            for nome, rotulo in MEDIDAS
        }

        mensagem_erro = ft.Text("", size=14, color=ft.Colors.RED_400)
        mensagem_confirmacao = ft.Text("", size=14, color=ft.Colors.GREEN_400)

        def cadastrar_aluno(e):
            mensagem_confirmacao.value = ""
            nome = (campo_nome.value or "").strip()
            altura = (campo_altura.value or "").strip()
            peso = (campo_peso.value or "").strip()
            foco = campo_foco.value
            proxima = (campo_proxima.value or "").strip()

            if not nome or not altura or not peso or not foco:
                mensagem_erro.value = "Preencha todos os campos obrigatórios."
                page.update()
                return

            try:
                altura_numero = converter_numero(altura)
                peso_numero = converter_numero(peso)
                if altura_numero <= 0 or peso_numero <= 0:
                    raise ValueError
            except ValueError:
                mensagem_erro.value = "Altura e peso devem ser números maiores que zero."
                page.update()
                return

            try:
                medidas = ler_medidas(campos_medidas)
            except ValueError:
                mensagem_erro.value = "As medidas corporais devem ser números maiores que zero."
                page.update()
                return

            proxima_iso = ""
            if proxima:
                try:
                    proxima_iso = datetime.strptime(proxima, "%d/%m/%Y").date().isoformat()
                except ValueError:
                    mensagem_erro.value = "Informe a próxima avaliação no formato DD/MM/AAAA."
                    page.update()
                    return

            hoje = date.today().isoformat()
            novo_aluno = {
                "nome": nome,
                "altura": str(altura_numero),
                "peso": str(peso_numero),
                "peso_inicial": str(peso_numero),
                "foco": foco,
                "ativo": True,
                "data_inicio": hoje,
                "proxima_avaliacao": proxima_iso,
                "avaliacoes": [
                    {
                        "data": hoje,
                        "peso": str(peso_numero),
                        "cintura": medidas["cintura"],
                        "abdomen": medidas["abdomen"],
                        "quadril": medidas["quadril"],
                        "braco": medidas["braco"],
                        "coxa": medidas["coxa"],
                        "observacoes": "Avaliação inicial."
                    }
                ]
            }

            alunos.append(novo_aluno)
            salvar_dados(alunos)
            mensagem_erro.value = ""
            mensagem_confirmacao.value = "Aluno cadastrado com sucesso!"
            campo_nome.value = ""
            campo_altura.value = ""
            campo_peso.value = ""
            campo_foco.value = None
            campo_proxima.value = ""
            for campo in campos_medidas.values():
                campo.value = ""
            page.update()

        nomes = list(campos_medidas.keys())
        linhas_medidas = [
            ft.Row(
                controls=[campos_medidas[nomes[i]]] + (
                    [campos_medidas[nomes[i + 1]]] if i + 1 < len(nomes) else []
                ),
                spacing=10
            )
            for i in range(0, len(nomes), 2)
        ]

        page.add(
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Voltar",
                        on_click=lambda e: tela_inicio()
                    ),
                    ft.Text("Cadastro de Aluno", size=24, weight=ft.FontWeight.BOLD)
                ]
            ),
            ft.Divider(),
            ft.Column(
                controls=[
                    campo_nome,
                    campo_altura,
                    campo_peso,
                    campo_foco,
                    campo_proxima,
                    ft.Text("Medidas corporais (opcional)", weight=ft.FontWeight.BOLD),
                    *linhas_medidas,
                    mensagem_erro,
                    mensagem_confirmacao,
                    ft.TextButton(
                        "Cadastrar",
                        icon=ft.Icons.SAVE,
                        width=400,
                        on_click=cadastrar_aluno
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=12
            )
        )
        page.update()

    # TELA DE ALUNOS
    def tela_alunos():
        page.clean()
        lista_view = ft.ListView(expand=True, spacing=10)

        def renderizar_alunos():
            lista_view.controls.clear()
            if not alunos:
                lista_view.controls.append(ft.Text("Nenhum aluno cadastrado.", size=16))

            for index, aluno in enumerate(alunos):
                def excluir_aluno(e, idx=index):
                    nome_aluno = alunos[idx]["nome"]

                    def confirmar_exclusao(ev):
                        alunos.pop(idx)
                        salvar_dados(alunos)
                        fechar_dialogo(dialogo_confirmacao)
                        renderizar_alunos()

                    def cancelar_exclusao(ev):
                        fechar_dialogo(dialogo_confirmacao)

                    dialogo_confirmacao = ft.AlertDialog(
                        title=ft.Text("Excluir aluno"),
                        content=ft.Text(f"Deseja realmente excluir {nome_aluno}?"),
                        actions=[
                            ft.TextButton("Cancelar", on_click=cancelar_exclusao),
                            ft.TextButton("Excluir", on_click=confirmar_exclusao)
                        ]
                    )
                    mostrar_dialogo(dialogo_confirmacao)

                def editar_aluno(e, idx=index):
                    abrir_edicao(idx)

                def abrir_perfil(e, idx=index):
                    abrir_perfil_aluno(idx)

                status = classificar_avaliacao(aluno.get("proxima_avaliacao", ""))
                ativo = aluno.get("ativo", True)

                card = ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column(
                            controls=[
                                ft.Text(aluno["nome"], size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Altura: {aluno['altura']} m"),
                                ft.Text(f"Peso atual: {peso_atual_do(aluno)} kg"),
                                ft.Text(f"Foco: {aluno['foco']}"),
                                ft.Text(
                                    "Situação: Ativo" if ativo else "Situação: Inativo",
                                    size=12,
                                    color=ft.Colors.GREEN_400 if ativo else ft.Colors.GREY_400
                                ),
                                ft.Text(status, size=12, color=cor_status(status)),
                                ft.Row(
                                    controls=[
                                        ft.TextButton("Ver acompanhamento", icon=ft.Icons.INSIGHTS, on_click=abrir_perfil),
                                        ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=editar_aluno),
                                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Excluir", on_click=excluir_aluno)
                                    ],
                                    wrap=True
                                )
                            ]
                        )
                    )
                )
                lista_view.controls.append(card)

            page.update()

        # PERFIL DO ALUNO EM JANELA
        def abrir_perfil_aluno(index):
            aluno = alunos[index]

            conteudo_perfil = ft.Column(
                controls=[],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                width=380,
                height=420
            )

            def atualizar_perfil():
                avaliacoes_atualizadas = aluno.get("avaliacoes", [])
                conteudo_perfil.controls = [
                    ft.Text(f"Nome: {aluno['nome']}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Altura: {aluno['altura']} m"),
                    ft.Text(f"Objetivo: {aluno['foco']}"),
                    ft.Text(f"Situação: {'Ativo' if aluno.get('ativo', True) else 'Inativo'}"),
                    ft.Text(f"Peso inicial: {aluno.get('peso_inicial', aluno.get('peso', ''))} kg"),
                    ft.Text(f"Peso atual: {peso_atual_do(aluno)} kg"),
                    ft.Text(f"Início: {data_para_exibicao(aluno.get('data_inicio', ''))}"),
                    ft.Text(f"Próxima avaliação: {data_para_exibicao(aluno.get('proxima_avaliacao', ''))}"),
                    ft.Divider(),
                    ft.Text("Histórico de avaliações", weight=ft.FontWeight.BOLD)
                ]

                if not avaliacoes_atualizadas:
                    conteudo_perfil.controls.append(ft.Text("Nenhuma avaliação registrada."))
                else:
                    for avaliacao in reversed(avaliacoes_atualizadas):
                        conteudo_perfil.controls.extend([
                            ft.Text(f"Data: {data_para_exibicao(avaliacao.get('data', ''))}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Peso: {avaliacao.get('peso', '-')} kg"),
                            ft.Text(f"Cintura: {avaliacao.get('cintura') or '-'} cm | Abdômen: {avaliacao.get('abdomen') or '-'} cm"),
                            ft.Text(f"Quadril: {avaliacao.get('quadril') or '-'} cm | Braço: {avaliacao.get('braco') or '-'} cm"),
                            ft.Text(f"Coxa: {avaliacao.get('coxa') or '-'} cm"),
                            ft.Text(f"Observações: {avaliacao.get('observacoes') or '-'}"),
                            ft.Divider()
                        ])

            def abrir_nova_avaliacao(e):
                dialogo_perfil.open = False
                page.update()
                nova_avaliacao(index, atualizar_perfil, dialogo_perfil)

            atualizar_perfil()
            dialogo_perfil = ft.AlertDialog(
                title=ft.Text("Acompanhamento do aluno"),
                content=conteudo_perfil,
                actions=[
                    ft.TextButton("Nova avaliação", icon=ft.Icons.ADD, on_click=abrir_nova_avaliacao),
                    ft.TextButton("Fechar", on_click=lambda e: fechar_dialogo(dialogo_perfil))
                ]
            )
            mostrar_dialogo(dialogo_perfil)

        # ADICIONAR AVALIAÇÃO
        def nova_avaliacao(index, atualizar_perfil, dialogo_perfil):
            aluno = alunos[index]
            campo_data = ft.TextField(
                label="Data da avaliação (DD/MM/AAAA)",
                value=date.today().strftime("%d/%m/%Y"),
                width=350
            )
            campo_peso = ft.TextField(label="Peso (kg)", keyboard_type=ft.KeyboardType.NUMBER, width=350)
            campos_medidas = {
                nome: ft.TextField(label=rotulo, keyboard_type=ft.KeyboardType.NUMBER, width=350)
                for nome, rotulo in MEDIDAS
            }
            campo_observacoes = ft.TextField(label="Observações", multiline=True, min_lines=2, max_lines=3, width=350)
            campo_proxima = ft.TextField(
                label="Próxima avaliação (DD/MM/AAAA)",
                value=data_para_exibicao(aluno.get("proxima_avaliacao", "")) if aluno.get("proxima_avaliacao") else "",
                width=350
            )
            mensagem = ft.Text("", color=ft.Colors.RED_400, size=12)

            formulario = ft.Column(
                controls=[
                    campo_data, campo_peso, *campos_medidas.values(),
                    campo_observacoes, campo_proxima, mensagem
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                height=430,
                width=370
            )

            def salvar_avaliacao(e):
                try:
                    data_registro = datetime.strptime((campo_data.value or "").strip(), "%d/%m/%Y").date()
                    peso = converter_numero(campo_peso.value or "")
                    if peso <= 0:
                        raise ValueError
                    medidas = ler_medidas(campos_medidas)
                except ValueError:
                    mensagem.value = "Informe uma data válida e valores numéricos maiores que zero."
                    page.update()
                    return

                proxima_texto = (campo_proxima.value or "").strip()
                proxima_iso = aluno.get("proxima_avaliacao", "")
                if proxima_texto:
                    try:
                        proxima_iso = datetime.strptime(proxima_texto, "%d/%m/%Y").date().isoformat()
                    except ValueError:
                        mensagem.value = "Informe a próxima avaliação no formato DD/MM/AAAA."
                        page.update()
                        return
                else:
                    proxima_iso = ""

                registro = {
                    "data": data_registro.isoformat(),
                    "peso": str(peso),
                    "cintura": medidas["cintura"],
                    "abdomen": medidas["abdomen"],
                    "quadril": medidas["quadril"],
                    "braco": medidas["braco"],
                    "coxa": medidas["coxa"],
                    "observacoes": (campo_observacoes.value or "").strip()
                }
                aluno.setdefault("avaliacoes", []).append(registro)
                aluno["avaliacoes"].sort(key=lambda item: item.get("data", ""))
                # O peso atual sempre vem da avaliação mais recente
                aluno["peso"] = aluno["avaliacoes"][-1].get("peso", str(peso))
                aluno["proxima_avaliacao"] = proxima_iso
                salvar_dados(alunos)

                fechar_dialogo(dialogo_avaliacao)
                atualizar_perfil()
                renderizar_alunos()
                dialogo_perfil.open = True
                page.update()

            def cancelar(e):
                fechar_dialogo(dialogo_avaliacao)
                dialogo_perfil.open = True
                page.update()

            dialogo_avaliacao = ft.AlertDialog(
                title=ft.Text("Nova avaliação"),
                content=formulario,
                actions=[
                    ft.TextButton("Cancelar", on_click=cancelar),
                    ft.TextButton("Salvar avaliação", on_click=salvar_avaliacao)
                ]
            )
            mostrar_dialogo(dialogo_avaliacao)

        # EDITAR ALUNO
        def abrir_edicao(index):
            aluno = alunos[index]
            campo_nome = ft.TextField(label="Nome", value=aluno["nome"])
            campo_altura = ft.TextField(label="Altura (m)", value=aluno["altura"])
            campo_foco = ft.Dropdown(
                label="Foco de resultado",
                value=aluno["foco"],
                options=[ft.dropdown.Option(o) for o in OPCOES_FOCO]
            )
            campo_proxima = ft.TextField(
                label="Próxima avaliação (DD/MM/AAAA)",
                value=data_para_exibicao(aluno.get("proxima_avaliacao", "")) if aluno.get("proxima_avaliacao") else ""
            )
            campo_ativo = ft.Switch(label="Aluno ativo", value=aluno.get("ativo", True))
            mensagem = ft.Text("", color=ft.Colors.RED_400, size=12)

            def salvar_edicao(e):
                nome = (campo_nome.value or "").strip()
                altura = (campo_altura.value or "").strip()
                if not nome or not altura or not campo_foco.value:
                    mensagem.value = "Preencha todos os campos."
                    page.update()
                    return
                try:
                    altura_numero = converter_numero(altura)
                    if altura_numero <= 0:
                        raise ValueError
                except ValueError:
                    mensagem.value = "Informe uma altura válida."
                    page.update()
                    return

                proxima_texto = (campo_proxima.value or "").strip()
                proxima_iso = ""
                if proxima_texto:
                    try:
                        proxima_iso = datetime.strptime(proxima_texto, "%d/%m/%Y").date().isoformat()
                    except ValueError:
                        mensagem.value = "Informe a próxima avaliação no formato DD/MM/AAAA."
                        page.update()
                        return

                aluno["nome"] = nome
                aluno["altura"] = str(altura_numero)
                aluno["foco"] = campo_foco.value
                aluno["proxima_avaliacao"] = proxima_iso
                aluno["ativo"] = bool(campo_ativo.value)
                salvar_dados(alunos)
                fechar_dialogo(dialogo)
                renderizar_alunos()

            dialogo = ft.AlertDialog(
                title=ft.Text("Editar aluno"),
                content=ft.Column(
                    controls=[campo_nome, campo_altura, campo_foco, campo_proxima, campo_ativo, mensagem],
                    tight=True,
                    width=350
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo(dialogo)),
                    ft.TextButton("Salvar", on_click=salvar_edicao)
                ]
            )
            mostrar_dialogo(dialogo)

        page.add(
            ft.Row(
                controls=[
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Voltar", on_click=lambda e: tela_inicio()),
                    ft.Text("Alunos Cadastrados", size=24, weight=ft.FontWeight.BOLD)
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

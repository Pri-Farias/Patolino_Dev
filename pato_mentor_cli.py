# pato_mentor_cli.py

# Importações
import os
import google.generativeai as genai
import sys

# --- Importações para Formatação Bonita (Rich) ---
from rich.console import Console
from rich.markdown import Markdown
from rich.theme import Theme

# --- Definindo um tema mais suave para o Markdown ---
# Este tema afeta as cores DENTRO da resposta do Gemini (quando ele usa Markdown)
suave_theme = Theme({
    "markdown.code": "green",       # Blocos de código em verde
    "markdown.strong": "bold",      # Negrito continua negrito (sem cor extra)
    "markdown.emph": "italic",      # Itálico continua itálico (sem cor extra)
    "markdown.list_item": "default",# Itens de lista cor padrão do terminal
    "markdown.block_quote": "dim white", # Citações em branco fosco
})

# --- Configura a ferramenta de impressão bonita da Rich ---
console = Console(theme=suave_theme)

# --- Funções para Construir os Prompts do Patolino ---

# Definindo prefixos dos comandos (em minúsculas para comparação flexível)
PREFIXO_RESUMIR = "resumir:"
PREFIXO_ENSINAR = "ensinar:"
PREFIXO_DESAFIO = "desafio:"
# Comando de ajuda (não tem prefixo, é a palavra exata)
COMANDO_AJUDA = "ajuda"

def build_pato_prompt(command_type, user_input_argument, console_instance):
    """
    Constrói o prompt completo para enviar ao Google Gemini,
    incluindo a personalidade do Patolino Dev e a instrução
    específica baseada no tipo de comando.

    Args:
        command_type (str): O tipo de comando ('resumir', 'ensinar', 'desafio', 'general').
        user_input_argument (str): O texto que o usuário digitou após o comando, ou a pergunta geral.
        console_instance (Console): A instância do Console do rich para imprimir mensagens de validação interna.

    Returns:
        str: O prompt completo formatado para o Gemini.
        None: Se o argumento para um comando específico for vazio (mensagem de erro impressa internamente).
    """
    # Instrução base da personalidade do Patolino Dev
    pato_persona = """
Aja como um patinho mentor amigável, paciente e divertido para um estudante de tecnologia focado em front-end e que está aprendendo Python. Seu nome é Patolino Dev. Mantenha a personalidade do patinho e inclua 'Quack!' no início ou fim da sua resposta, de forma natural e não forçada. Use formatação Markdown (negrito, listas, blocos de código se for código) se apropriado.
"""

    prompt_especifico = ""

    if command_type == 'resumir':
        # Validar argumento para 'resumir'
        if not user_input_argument.strip():
            console_instance.print("[orange]Patolino Dev: Quack! Você quer que eu resuma o quê, Quack? Não tem texto depois de 'resumir:'.[/orange]")
            return None # Indica que o prompt não deve ser enviado

        prompt_especifico = f"""
{pato_persona}
Por favor, resuma o seguinte texto de forma clara e concisa para um estudante iniciante. Foque nos pontos principais.

Texto para resumir:
{user_input_argument}

Resumo do Patinho Dev:
"""
        # Mensagem de status - pensando
        console_instance.print("[italic yellow]Patolino Dev pensando no resumo... 🤔[/italic yellow]")

    elif command_type == 'ensinar':
        # Validar argumento para 'ensinar'
        if not user_input_argument.strip():
            console_instance.print("[orange]Patolino Dev: Quack! Quer aprender sobre o quê, Quack? Não tem tópico depois de 'ensinar:'.[/orange]")
            return None # Indica que o prompt não deve ser enviado

        prompt_especifico = f"""
{pato_persona}
Por favor, explique o conceito "{user_input_argument}" de forma extremamente simples, didática e clara para um estudante iniciante (imagine explicar para alguém que está começando). Use exemplos simples.

Explicação do Patinho Dev sobre {user_input_argument}:
"""
        # Mensagem de status - pensando
        console_instance.print(f"[italic yellow]Patolino Dev preparando a aula sobre '{user_input_argument}'... 🤔[/italic yellow]")

    elif command_type == 'desafio':
        # Validar argumento para 'desafio'
        if not user_input_argument.strip():
            console_instance.print("[orange]Patolino Dev: Quack! Quer um desafio sobre o quê, Quack? Não tem tema depois de 'desafio:'.[/orange]")
            return None # Indica que o prompt não deve ser enviado

        prompt_especifico = f"""
{pato_persona}
Por favor, crie um quiz rápido para testar o conhecimento do estudante sobre o tema "{user_input_argument}". O quiz deve ter 3 perguntas de múltipla escolha (com A, B, C, D) ou perguntas curtas e diretas. Use formatação Markdown para destacar perguntas e opções. Forneça as respostas corretas NO FINAL do quiz, separadas das perguntas (ex: Respostas: 1-A, 2-B, 3-C).

Quiz do Patinho Dev sobre {user_input_argument}:
"""
        # Mensagem de status - pensando
        console_instance.print(f"[italic yellow]Patolino Dev criando um desafio sobre '{user_input_argument}'... 🤔[/italic yellow]")

    elif command_type == 'general':
         prompt_especifico = f"""
{pato_persona}
Responda à seguinte pergunta ou pedido do estudante. Se for um pedido (como "resumir isso"), execute a tarefa mantendo a personalidade.

Pergunta/Pedido do estudante: {user_input_argument}

Resposta do Patinho Dev:
"""
         # Mensagem de status - pensando
         console_instance.print("[italic yellow]Patolino Dev pensando na sua pergunta geral... 🤔[/italic yellow]")

    # Retorna o prompt específico montado
    return prompt_especifico

def display_commands(console_instance):
    """Exibe a lista de comandos disponíveis no terminal."""
    console_instance.print("[yellow]Comandos disponíveis:[/yellow]")
    console_instance.print(f"  [bold yellow]{PREFIXO_RESUMIR}[/bold yellow] [white]texto para resumir[/white]")
    console_instance.print(f"  [bold yellow]{PREFIXO_ENSINAR}[/bold yellow] [white]tópico para aprender[/white]")
    console_instance.print(f"  [bold yellow]{PREFIXO_DESAFIO}[/bold yellow] [white]tema para desafio[/white]")
    console_instance.print(f"  [bold yellow]{COMANDO_AJUDA}[/bold yellow] [white](mostra esta lista)[/white]")
    console_instance.print(f"  [bold yellow]sair[/bold yellow] [white](para terminar)[/white]")


# --- Configuração Inicial da API ---
# Lemos a API Key da variável de ambiente GOOGLE_API_KEY
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    console.print("[bold red]Erro:[/bold red] A variável de ambiente GOOGLE_API_KEY não está configurada.")
    console.print("[orange]Por favor, configure-a seguindo as instruções da Fase 2.[/orange]")
    sys.exit(1)

try:
    genai.configure(api_key=api_key)
except Exception as e:
     console.print(f"[bold red]Erro ao configurar a API com a chave:[/bold red] {e}")
     console.print("[orange]Verifique se a sua GOOGLE_API_KEY está correta.[/orange]")
     sys.exit(1)

try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    console.print(f"[bold red]Erro ao carregar o modelo 'gemini-1.5-flash-latest':[/bold red] {e}")
    console.print("[orange]Verifique se o nome do modelo está correto e se ele aparece na sua lista de modelos disponíveis.[/orange]")
    sys.exit(1)

# --- Início da Interação ---

console.print("[bold yellow]Patolino Dev pronto! Quack![/bold yellow]")
display_commands(console) # Exibe os comandos usando a função
console.print("\n[yellow]Digite sua pergunta ou comando para o Patolino Dev:[/yellow]")

# --- Loop Principal de Conversa (Limpo e Chama Funções) ---

while True:
    sua_pergunta = input("Você: ")

    # --- Tratamento de comandos especiais (sair, ajuda) ---
    if sua_pergunta.lower() == 'sair':
        console.print("[bold yellow]Patolino Dev dizendo Tchau! Quack Quack![/bold yellow]")
        break

    if not sua_pergunta.strip():
        console.print("[orange]Patolino Dev: Quack! Você esqueceu de perguntar/comandar, Quack! Digite algo![/orange]")
        continue

    if sua_lower == COMANDO_AJUDA:
        display_commands(console)
        continue # Pula o resto do loop

    # --- Determina o tipo de comando e argumento ---
    command_type = 'general' # Tipo padrão
    user_input_argument = sua_pergunta # Argumento padrão (a pergunta inteira)
    sua_lower = sua_pergunta.lower() # Converte para minúsculas UMA VEZ para checar prefixes/comandos

    # Checa se é um comando conhecido baseado nos prefixos
    if sua_lower.startswith(PREFIXO_RESUMIR.lower()):
        command_type = 'resumir'
        user_input_argument = sua_pergunta[len(PREFIXO_RESUMIR):] # Pega o texto depois do prefixo
    elif sua_lower.startswith(PREFIXO_ENSINAR.lower()):
        command_type = 'ensinar'
        user_input_argument = sua_pergunta[len(PREFIXO_ENSINAR):]
    elif sua_lower.startswith(PREFIXO_DESAFIO.lower()):
        command_type = 'desafio'
        user_input_argument = sua_pergunta[len(PREFIXO_DESAFIO):]
    # Nota: O comando 'ajuda' já foi tratado acima

    # --- Constrói o prompt usando a função ---
    # A função build_pato_prompt também lida com a validação de argumentos e imprime erro se necessário
    prompt_a_enviar = build_pato_prompt(command_type, user_input_argument.strip(), console) # Passa argumento limpo

    # Se build_pato_prompt retornou None, significa que o argumento estava faltando para um comando específico
    if prompt_a_enviar is None:
        continue # Volta para o início do loop (a mensagem de erro já foi impressa na função)

    # --- Enviando o Prompt para o Gemini (e lidando com erros) ---
    # Este bloco é executado APENAS se prompt_a_enviar não for None
    try:
        response = model.generate_content(prompt_a_enviar)

        # --- VERIFICAÇÃO DE FILTROS DE SEGURANÇA (Adicionado!) ---
        # Checamos se a resposta tem feedback do prompt ou ratings de segurança
        # indicando que algo foi bloqueado pela API.
        if response.prompt_feedback or response.safety_ratings:
             # Podemos imprimir o feedback ou ratings para debug se quiser ver o motivo exato:
             # console.print(response.prompt_feedback)
             # console.print(response.safety_ratings)
             console.print("[orange]Patolino Dev: Quack! Opa! Parece que essa pergunta/resposta tocou em um assunto delicado e foi filtrada, Quack! Tente perguntar de outro jeito.[/orange]")
             continue # Pula o restante do bloco e volta para o input

        # --- Exibindo a Resposta do Patolino usando Rich ---
        # Esta parte só executa se não houve filtro de segurança E se response.text existe
        if response.text:
            console.print(Markdown(f"Patolino Dev: {response.text}"))
        else:
            # Esta mensagem seria para outros casos onde não vem texto (raro)
            console.print("[orange]Patolino Dev: Quack! Não consegui gerar uma resposta para isso, Quack! (Resposta vazia da API).[/orange]")


    except Exception as e:
        # Mensagem de erro na comunicação durante a conversa
        console.print(f"[bold red]Patolino Dev escorregou DURANTE A CONVERSA! Ocorreu um erro:[/bold red] {e}")
        console.print("[orange]Patolino Dev: Quack! Minha internet patinou ou algo deu errado na API. Tente perguntar de novo, Quack![/orange]")


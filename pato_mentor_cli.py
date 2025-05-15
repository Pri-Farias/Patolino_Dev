
import os
import google.generativeai as genai
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.theme import Theme

suave_theme = Theme({
    "markdown.code": "green",
    "markdown.strong": "bold",
    "markdown.emph": "italic",
    "markdown.list_item": "default",
    "markdown.block_quote": "dim white",
})

console = Console(theme=suave_theme)

PREFIXO_RESUMIR = "resumir:"
PREFIXO_ENSINAR = "ensinar:"
PREFIXO_DESAFIO = "desafio:"
COMANDO_AJUDA = "ajuda"
COMANDO_SAIR = "sair"

def build_pato_prompt(command_type, user_input_argument, console_instance):
    """
    Constrói o prompt completo para enviar ao Google Gemini.
    Inclui a personalidade do Patolino Dev e a instrução específica.
    Valida argumentos para comandos específicos e imprime mensagens internas.

    Args:
        command_type (str): O tipo de comando ('resumir', 'ensinar', 'desafio', 'general').
        user_input_argument (str): O texto que o usuário digitou após o comando, ou a pergunta geral.
        console_instance (Console): A instância do Console do rich.

    Returns:
        str: O prompt completo formatado para o Gemini.
        None: Se o argumento para um comando específico for inválido/vazio.
    """
    pato_persona = """
Aja como um patinho mentor amigável, paciente e divertido para um estudante de tecnologia focado em front-end e que está aprendendo Python. Seu nome é Patolino Dev. Mantenha a personalidade do patinho e inclua 'Quack!' no início ou fim da sua resposta, de forma natural e não forçada. Use formatação Markdown (negrito, listas, blocos de código se for código) se apropriado.
"""

    prompt_especifico = ""
    thinking_message = ""

    if command_type == 'resumir':
        if not user_input_argument.strip():
            console_instance.print(f"[orange]Patolino Dev: Quack! Você quer que eu resuma o quê, Quack? Não tem texto depois de '{PREFIXO_RESUMIR}'.[/orange]")
            return None
        prompt_especifico = f"""{pato_persona}\nPor favor, resuma o seguinte texto de forma clara e concisa para um estudante iniciante. Foque nos pontos principais.\n\nTexto para resumir:\n{user_input_argument}\n\nResumo do Patinho Dev:"""
        thinking_message = f"[italic yellow]Patolino Dev pensando no resumo... 🤔[/italic yellow]"

    elif command_type == 'ensinar':
        if not user_input_argument.strip():
            console_instance.print(f"[orange]Patolino Dev: Quack! Quer aprender sobre o quê, Quack? Não tem tópico depois de '{PREFIXO_ENSINAR}'.[/orange]")
            return None
        prompt_especifico = f"""{pato_persona}\nPor favor, explique o conceito "{user_input_argument}" de forma extremamente simples, didática e clara para um estudante iniciante (imagine explicar para alguém que está começando). Use exemplos simples.\n\nExplicação do Patinho Dev sobre {user_input_argument}:"""
        thinking_message = f"[italic yellow]Patolino Dev preparando a aula sobre '{user_input_argument}'... 🤔[/italic yellow]"

    elif command_type == 'desafio':
        if not user_input_argument.strip():
            console_instance.print(f"[orange]Patolino Dev: Quack! Quer um desafio sobre o quê, Quack? Não tem tema depois de '{PREFIXO_DESAFIO}'.[/orange]")
            return None
        prompt_especifico = f"""{pato_persona}\nPor favor, crie um quiz rápido para testar o conhecimento do estudante sobre o tema "{user_input_argument}". O quiz deve ter 3 perguntas de múltipla escolha (com A, B, C, D) ou perguntas curtas e diretas. Use formatação Markdown para destacar perguntas e opções. Forneça as respostas corretas NO FINAL do quiz, separadas das perguntas (ex: Respostas: 1-A, 2-B, 3-C)."""
        thinking_message = f"[italic yellow]Patolino Dev criando um desafio sobre '{user_input_argument}'... 🤔[/italic yellow]"

    elif command_type == 'general':
         prompt_especifico = f"""{pato_persona}\nResponda à seguinte pergunta ou pedido do estudante. Se for um pedido (como "resumir isso"), execute a tarefa mantendo a personalidade.\n\nPergunta/Pedido do estudante: {user_input_argument}\n\nResposta do Patinho Dev:"""
         thinking_message = "[italic yellow]Patolino Dev pensando na sua pergunta geral... 🤔[/italic yellow]"

    console_instance.print(thinking_message)
    return prompt_especifico

def display_commands(console_instance):
    """Exibe a lista de comandos disponíveis no terminal."""
    console_instance.print("[yellow]Comandos disponíveis:[/yellow]")
    console_instance.print(f"  [bold yellow]{PREFIXO_RESUMIR}[/bold yellow] [white]texto para resumir[/white]")
    console_instance.print(f"  [bold yellow]{PREFIXO_ENSINAR}[/bold yellow] [white]tópico para aprender[/white]")
    console_instance.print(f"  [bold yellow]{PREFIXO_DESAFIO}[/bold yellow] [white]tema para desafio[/white]")
    console_instance.print(f"  [bold yellow]{COMANDO_AJUDA}[/bold yellow] [white](mostra esta lista)[/white]")
    console_instance.print(f"  [bold yellow]{COMANDO_SAIR}[/bold yellow] [white](para terminar)[/white]")


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

console.print("[bold yellow]Patolino Dev pronto! Quack![/bold yellow]")
display_commands(console)
console.print("\n[yellow]Digite sua pergunta ou comando para o Patolino Dev:[/yellow]")

while True:
    sua_pergunta = input("Você: ")

   
    sua_lower = sua_pergunta.lower()

    if sua_lower == COMANDO_SAIR.lower():
        console.print("[bold yellow]Patolino Dev dizendo Tchau! Quack Quack![/bold yellow]")
        break

    if not sua_pergunta.strip():
        console.print("[orange]Patolino Dev: Quack! Você esqueceu de perguntar/comandar, Quack! Digite algo![/orange]")
        continue

    if sua_lower == COMANDO_AJUDA.lower():
        display_commands(console)
        continue


    command_type = 'general'
    user_input_argument = sua_pergunta

    if sua_lower.startswith(PREFIXO_RESUMIR.lower()):
        command_type = 'resumir'
        user_input_argument = sua_pergunta[len(PREFIXO_RESUMIR):]
    elif sua_lower.startswith(PREFIXO_ENSINAR.lower()):
        command_type = 'ensinar'
        user_input_argument = sua_pergunta[len(PREFIXO_ENSINAR):]
    elif sua_lower.startswith(PREFIXO_DESAFIO.lower()):
        command_type = 'desafio'
        user_input_argument = sua_pergunta[len(PREFIXO_DESAFIO):]

   
    prompt_a_enviar = build_pato_prompt(command_type, user_input_argument.strip(), console)

   
    if prompt_a_enviar is None:
        continue

    try:
       
        response = model.generate_content(prompt_a_enviar)

        if response.text:
            console.print(Markdown(f"Patolino Dev: {response.text}"))
        else:
     
             safety_info = getattr(response, 'safety_ratings', None)
             feedback_info = getattr(response, 'prompt_feedback', None)

             if safety_info is not None or feedback_info is not None:
                
                 console.print("[orange]Patolino Dev: Quack! Opa! Parece que essa pergunta/resposta tocou em um assunto delicado e foi filtrada, Quack! Tente perguntar de outro jeito.[/orange]")
             else:
                 
                 console.print("[orange]Patolino Dev: Quack! Não consegui gerar uma resposta para isso, Quack! (Resposta vazia ou erro inesperado da API).[/orange]")


    except Exception as e:
        console.print(f"[bold red]Patolino Dev escorregou DURANTE A CONVERSA! Ocorreu um erro:[/bold red] {e}")
        console.print("[orange]Patolino Dev: Quack! Minha internet patinou ou algo deu errado na API. Tente perguntar de novo, Quack![/orange]")


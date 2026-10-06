import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from app.graph.workflow import run_medicine_assistant
from app.mcp.tools.check_interaction import check_drug_interaction
from app.mcp.tools.find_generic import find_generic_equivalent
from evaluation.eval_runner import run_evaluation_suite

# Force UTF-8 encoding
sys.stdout.reconfigure(encoding="utf-8")
console = Console()

def display_banner():
    banner_text = """
 [bold cyan]╔══════════════════════════════════════════════════════════════════════╗[/bold cyan]
 [bold cyan]║[/bold cyan]  [bold white]🏥 MEDICINE & SYMPTOM INFORMATION ASSISTANT (LangGraph + MCP)[/bold white]  [bold cyan]║[/bold cyan]
 [bold cyan]║[/bold cyan]  [dim white]Domain: Healthcare (Informational, Non-Diagnostic)               [/dim white]  [bold cyan]║[/bold cyan]
 [bold cyan]╚══════════════════════════════════════════════════════════════════════╝[/bold cyan]
"""
    console.print(banner_text)
    console.print("[dim]Type your question, or use commands: [bold green]/eval[/bold green], [bold yellow]/interact[/bold yellow], [bold magenta]/generic[/bold magenta], [bold red]/emergency[/bold red], [bold blue]/help[/bold blue], [bold red]/quit[/bold red][/dim]\n")

def display_help():
    table = Table(title="Available Interactive Commands", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="bold green", width=15)
    table.add_column("Description", style="white")
    table.add_row("/help", "Show this help and command manual")
    table.add_row("/eval", "Run the 28-query safety and guardrail benchmark suite")
    table.add_row("/interact", "Interactive multi-drug interaction matrix tool")
    table.add_row("/generic", "Search generic alternatives & calculate cost savings")
    table.add_row("/emergency", "Display critical red-flag emergency hotlines and guide")
    table.add_row("/quit or /exit", "Exit the assistant")
    console.print(table)

def handle_direct_interaction():
    console.print("[bold yellow]Enter 2 or more medicines separated by commas (e.g. ibuprofen, lisinopril):[/bold yellow]")
    inp = Prompt.ask("[bold yellow]Medications[/bold yellow]")
    drugs = [d.strip() for d in inp.split(",") if d.strip()]
    if len(drugs) < 2:
        console.print("[red]Please enter at least 2 medications.[/red]")
        return
    res = check_drug_interaction(drugs)
    console.print("\n" + res.get("summary", "") + "\n")
    for item in res.get("results", []):
        sev_color = "red" if "High" in item["severity"] or "Severe" in item["severity"] else ("yellow" if "Moderate" in item["severity"] else "green")
        panel_content = f"""[bold]Pair[/bold]: {' ↔️ '.join(item['drug_pair'])}
[bold]Severity[/bold]: [{sev_color}]{item['severity']}[/{sev_color}]
[bold]Clinical Effect[/bold]: {item['clinical_effect']}
[bold]Mechanism[/bold]: {item['mechanism']}
[bold]Management[/bold]: {item['clinical_management']}
[bold]Alternative[/bold]: {item.get('alternative_recommendation', 'N/A')}"""
        console.print(Panel(panel_content, title=f"[{sev_color}]Interaction Alert[/{sev_color}]", border_style=sev_color))

def handle_direct_generic():
    inp = Prompt.ask("[bold magenta]Enter branded medicine (e.g. Lipitor, Tylenol, Advil)[/bold magenta]")
    res = find_generic_equivalent(inp)
    if res.get("found"):
        panel_content = f"""[bold]Brand[/bold]: {res.get('brand_name')}
[bold]Generic Active Ingredient[/bold]: [bold green]{res.get('generic_name')}[/bold green]
[bold]Active Chemical[/bold]: {res.get('active_ingredient')}
[bold]Equivalence Rating[/bold]: {res.get('therapeutic_equivalence')}
[bold]Estimated Cost Savings[/bold]: [bold yellow]{res.get('average_cost_savings')}[/bold yellow]
[bold]Forms Available[/bold]: {', '.join(res.get('common_forms', []))}
[bold]Access Category[/bold]: {res.get('otc_availability')}
[bold]Switching Advice[/bold]: {res.get('switching_guidance')}"""
        console.print(Panel(panel_content, title="[bold green]Generic Medicine Alternative[/bold green]", border_style="green"))
    else:
        console.print(f"[red]{res.get('message')}[/red]")

def handle_emergency_guide():
    guide = """[bold red]🚨 CRITICAL EMERGENCY RED FLAGS & HOTLINES[/bold red]

[bold white]IMMEDIATE DISPATCH NUMBERS:[/bold white]
• 🇺🇸 US & Canada: [bold red]911[/bold red]
• 🇪🇺 Europe & International: [bold red]112[/bold red]
• 🇬🇧 United Kingdom: [bold red]999[/bold red]
• 🇦🇺 Australia: [bold red]000[/bold red]
• 🧪 US Poison Help: [bold yellow]1-800-222-1222[/bold yellow]
• 🎗️ Suicide & Crisis Lifeline: [bold cyan]988[/bold cyan]

[bold white]CALL IMMEDIATELY FOR:[/bold white]
1. [bold]Chest Pain / Pressure[/bold] (crushing pain radiating to left arm or jaw, shortness of breath)
2. [bold]FAST Stroke Signs[/bold] (Face droop, Arm weakness, Slurred speech)
3. [bold]Severe Allergic Anaphylaxis[/bold] (throat swelling, difficulty breathing, wide hives)
4. [bold]Acute Poisoning / Overdose[/bold] (ingestion of chemicals, massive pill intake)
5. [bold]Uncontrolled Arterial Bleeding[/bold] or loss of consciousness"""
    console.print(Panel(guide, title="[bold red]Emergency First Aid Reference[/bold red]", border_style="red"))

def interactive_loop():
    display_banner()
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]👤 Your Query[/bold cyan]").strip()
            if not user_input:
                continue
                
            cmd = user_input.lower()
            if cmd in ["/quit", "/exit", "exit", "quit"]:
                console.print("[dim cyan]Thank you for using the Healthcare Information Assistant. Stay safe![/dim cyan]")
                break
            elif cmd == "/help":
                display_help()
                continue
            elif cmd == "/eval":
                console.print("[dim]Executing 28-query automated evaluation benchmark...[/dim]")
                res = run_evaluation_suite()
                console.print(f"[bold green]Evaluation complete![/bold green] Emergency Recall: {res['emergency_detection']['recall']}%, Policy Accuracy: {res['policy_adherence_accuracy_percent']}%")
                continue
            elif cmd == "/interact":
                handle_direct_interaction()
                continue
            elif cmd == "/generic":
                handle_direct_generic()
                continue
            elif cmd == "/emergency":
                handle_emergency_guide()
                continue

            # Run through LangGraph pipeline
            with console.status("[bold cyan]Processing through Guardrail & Agent Workflow...[/bold cyan]"):
                state = run_medicine_assistant(user_input)

            response_md = state.get("response_text", "No response generated.")
            intent = state.get("intent", "GENERAL")
            is_emergency = state.get("escalation_triggered", False)

            border_color = "red" if is_emergency else ("yellow" if intent == "INTERACTION_CHECK" else "cyan")
            title_text = "🚨 EMERGENCY ESCALATION" if is_emergency else f"🤖 Assistant Response [{intent}]"

            console.print(Panel(Markdown(response_md), title=title_text, border_style=border_color))

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim cyan]Session ended.[/dim cyan]")
            break

if __name__ == "__main__":
    interactive_loop()

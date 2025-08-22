import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from pathlib import Path
import json

from agent.core import AgentCore
from utils.logger import get_logger

app = typer.Typer(name="agent", help="Enterprise AI Agent CLI")
console = Console()
logger = get_logger(__name__)

# Global agent instance
agent = None

@app.command()
def start():
    """Start the agent with initialization"""
    async def _start():
        global agent
        try:
            agent = AgentCore()
            success = await agent.initialize()
            if success:
                rprint("✅ [green]Agent started successfully[/green]")
                rprint(f"Agent ID: {agent.agent_id}")
                rprint(f"Session ID: {agent.session_id}")
            else:
                rprint("❌ [red]Agent failed to start[/red]")
        except Exception as e:
            rprint(f"❌ [red]Error starting agent: {e}[/red]")
    
    asyncio.run(_start())

@app.command()
def status():
    """Show agent status and health metrics"""
    async def _status():
        global agent
        if not agent:
            rprint("❌ [red]Agent not running[/red]")
            return
        
        try:
            status_data = await agent.get_status()
            
            table = Table(title="Agent Status")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in status_data.items():
                table.add_row(key, str(value))
            
            console.print(table)
            
        except Exception as e:
            rprint(f"❌ [red]Error getting status: {e}[/red]")
    
    asyncio.run(_status())

@app.command()
def chat(message: str):
    """Send a message to the agent"""
    async def _chat():
        global agent
        if not agent or not agent.is_running:
            rprint("❌ [red]Agent not running. Start it first with 'agent start'[/red]")
            return
        
        try:
            rprint(f"🤖 Processing: {message}")
            result = await agent.process_request(message)
            
            if result['status'] == 'success':
                rprint(f"✅ [green]Response:[/green] {result['response']}")
            else:
                rprint(f"❌ [red]Error:[/red] {result.get('error_type', 'Unknown error')}")
                
        except Exception as e:
            rprint(f"❌ [red]Error processing message: {e}[/red]")
    
    asyncio.run(_chat())

@app.command()
def logs():
    """Show recent logs"""
    try:
        from config.settings import settings
        log_file = settings.log_file
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-20:]:  # Show last 20 lines
                    try:
                        log_data = json.loads(line.strip())
                        timestamp = log_data.get('timestamp', '')
                        level = log_data.get('level', 'INFO')
                        message = log_data.get('event', '')
                        rprint(f"[dim]{timestamp}[/dim] [{level}] {message}")
                    except:
                        rprint(line.strip())
        else:
            rprint("📝 No logs found")
            
    except Exception as e:
        rprint(f"❌ [red]Error reading logs: {e}[/red]")

@app.command()
def stop():
    """Stop the agent gracefully"""
    async def _stop():
        global agent
        if not agent:
            rprint("ℹ️ Agent not running")
            return
        
        try:
            await agent.cleanup()
            agent = None
            rprint("✅ [green]Agent stopped gracefully[/green]")
        except Exception as e:
            rprint(f"❌ [red]Error stopping agent: {e}[/red]")
    
    asyncio.run(_stop())

if __name__ == "__main__":
    app()

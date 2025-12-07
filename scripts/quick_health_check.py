"""
Quick Health Check Script

Performs rapid health checks on running services without deep testing.
Use this for quick verification that services are up and responding.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
from rich.console import Console
from rich.live import Live
from rich.table import Table

console = Console()


async def check_service(name: str, url: str, timeout: float = 5.0) -> tuple[bool, str]:
    """Check if a service is responding"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return True, f"✓ {response.status_code}"
            else:
                return False, f"✗ {response.status_code}"
    except httpx.ConnectError:
        return False, "✗ Connection refused"
    except httpx.TimeoutException:
        return False, "✗ Timeout"
    except Exception as e:
        return False, f"✗ {str(e)[:30]}"


async def quick_health_check():
    """Perform quick health check on all services"""
    console.print("\n[bold cyan]🏥 Quick Health Check[/bold cyan]\n")

    services = [
        ("FastAPI App", "http://localhost:8000/health"),
        ("FastAPI App (Alt)", "http://localhost:8001/health"),
        ("Admin React", "http://localhost:5173"),
        ("PostgreSQL", "http://localhost:5432"),  # Will fail with connection error if not running
        ("Redis", "http://localhost:6379"),  # Will fail with connection error if not running
        ("Celery Flower", "http://localhost:5555"),
        ("Prometheus", "http://localhost:9091"),
        ("Grafana", "http://localhost:3000"),
    ]

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Service", style="cyan", width=20)
    table.add_column("URL", style="blue", width=40)
    table.add_column("Status", width=20)

    results = []
    for name, url in services:
        status, message = await check_service(name, url)
        results.append((name, url, status, message))

        status_display = "[green]" + message + "[/green]" if status else "[red]" + message + "[/red]"
        table.add_row(name, url, status_display)

    console.print(table)

    # Summary
    up_count = sum(1 for _, _, status, _ in results if status)
    total_count = len(results)

    console.print(f"\n[bold]Services Status:[/bold] {up_count}/{total_count} UP\n")

    if up_count == 0:
        console.print("[red]❌ No services are running. Start them with:[/red]")
        console.print("[yellow]  docker-compose up -d[/yellow]\n")
    elif up_count < total_count:
        console.print("[yellow]⚠️  Some services are down. Check logs:[/yellow]")
        console.print("[yellow]  docker-compose logs[/yellow]\n")
    else:
        console.print("[green]✅ All services are running![/green]\n")


if __name__ == "__main__":
    try:
        asyncio.run(quick_health_check())
    except KeyboardInterrupt:
        console.print("\n[yellow]Check interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")

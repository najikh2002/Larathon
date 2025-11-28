import typer
import subprocess
from vendor.Illuminate.Console import generators, database

app = typer.Typer(help="✨ Laravel-like Artisan CLI for FastAPI")

# -------------------------------
# Make Commands
# -------------------------------
@app.command("make:controller")
def make_controller(name: str, resource: bool = typer.Option(False, "--resource")):
    generators.make_controller(name, resource)

@app.command("make:model")
def make_model(
    name: str,
    m: bool = typer.Option(False, "-m", help="Create migration"),
    r: bool = typer.Option(False, "-r", help="Create resource controller")
):
    """Create a new model (optionally with migration and resource controller)."""
    # biarkan generator handle print
    generators.make_model(name)

    if m:
        migration_name = f"create_{name.lower()}s_table"
        generators.make_migration(migration_name)

    if r:
        controller_name = f"{name}Controller"
        generators.make_controller(controller_name, resource=True)

@app.command("make:migration")
def make_migration(name: str):
    generators.make_migration(name)

@app.command("make:seeder")
def make_seeder(name: str):
    generators.make_seeder(name)

@app.command("make:factory")
def make_factory(name: str):
    generators.make_factory(name)

# -------------------------------
# Database Commands
# -------------------------------
@app.command("migrate")
def migrate():
    database.migrate()

@app.command("db:seed")
def db_seed():
    database.run_seeders()

@app.command("migrate:fresh")
def migrate_fresh(seed: bool = typer.Option(False, "--seed")):
    database.fresh_migrate(seed)

# -------------------------------
# Serve Command
# -------------------------------
@app.command("serve")
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Run FastAPI server (like php artisan serve)."""
    cmd = ["uvicorn", "bootstrap.app:app", f"--host={host}", f"--port={port}"]
    if reload:
        cmd.append("--reload")
    subprocess.run(cmd)

# -------------------------------
# Build Command
# -------------------------------
@app.command("build")
def build():
    """Build application for Vercel serverless deployment."""
    import os
    from pathlib import Path
    from vendor.Illuminate.Console.bundler import bundle_application

    typer.echo("🔨 Building Larathon for Vercel deployment...\n")

    # Run bundler to create single file
    try:
        output_path = bundle_application(".")
        typer.echo("")
    except Exception as e:
        typer.echo(f"❌ Build failed: {e}", err=True)
        raise typer.Exit(code=1)

    # Create vercel.json if not exists
    vercel_config = '''{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "APP_ENV": "production"
  }
}'''

    vercel_path = Path("vercel.json")
    if not vercel_path.exists():
        with open(vercel_path, "w") as f:
            f.write(vercel_config)
        typer.echo(f"✅ Created {vercel_path}")
    else:
        typer.echo(f"ℹ️  {vercel_path} already exists")

    # Create .vercelignore if not exists
    vercelignore_content = '''# Dependencies
env/
.env
node_modules/

# Python
*.pyc
__pycache__/
*.pyo
*.pyd

# Development files
.git/
.gitignore
.vscode/
.idea/
*.sqlite
database.sqlite

# Source files (already bundled)
app/
config/
bootstrap/
vendor/
database/
routes/
artisan.py
tests/

# Keep only
!api/
!vercel.json
!requirements.txt
'''

    vercelignore_path = Path(".vercelignore")
    if not vercelignore_path.exists():
        with open(vercelignore_path, "w") as f:
            f.write(vercelignore_content)
        typer.echo(f"✅ Created {vercelignore_path}")
    else:
        typer.echo(f"ℹ️  {vercelignore_path} already exists")

    typer.echo("\n" + "="*60)
    typer.echo("📦 Build completed successfully!")
    typer.echo("="*60)
    typer.echo("\n📋 Next steps for deployment:")
    typer.echo("\n1. Install Vercel CLI (if not installed):")
    typer.echo("   npm i -g vercel")
    typer.echo("\n2. Login to Vercel:")
    typer.echo("   vercel login")
    typer.echo("\n3. Set environment variables in Vercel:")
    typer.echo("   - DB_CONNECTION=pgsql")
    typer.echo("   - DB_HOST=<your-supabase-host>")
    typer.echo("   - DB_PORT=6543")
    typer.echo("   - DB_DATABASE=postgres")
    typer.echo("   - DB_USERNAME=<your-supabase-username>")
    typer.echo("   - DB_PASSWORD=<your-supabase-password>")
    typer.echo("   - SECRET_KEY=<your-secret-key>")
    typer.echo("\n4. Deploy to production:")
    typer.echo("   vercel --prod")
    typer.echo("\n💡 Tip: All your code is now bundled in api/index.py")
    typer.echo("="*60 + "\n")


if __name__ == "__main__":
    app()

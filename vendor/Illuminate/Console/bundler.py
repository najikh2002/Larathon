"""
Larathon Build Bundler
Bundles all application code into a single file for Vercel deployment
"""
import os
import re
import ast
import shutil
from pathlib import Path
from typing import Set, List, Dict


class PythonBundler:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.processed_files: Set[str] = set()
        self.bundle_content: List[str] = []
        self.external_imports: Set[str] = set()

        # Directories to include in bundle
        self.include_dirs = ['app', 'config', 'bootstrap', 'vendor', 'database', 'routes']

        # Files to exclude
        self.exclude_patterns = [
            '__pycache__',
            '.pyc',
            'tests/',
            'artisan.py',
            'bundler.py',
            'generators.py',
            'vendor/Illuminate/Console/database.py',  # Only exclude the Console database.py
            'vendor/Illuminate/Support/Facades/Route.py',  # Use ImprovedRoute directly, not Facade
            'Commands/',
            'migrations/',
            'seeders/',
        ]

    def should_include_file(self, filepath: str) -> bool:
        """Check if file should be included in bundle"""
        filepath_str = str(filepath)

        # Exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in filepath_str:
                return False

        # Only include files from specified directories
        relative_path = Path(filepath).relative_to(self.project_root)
        first_dir = str(relative_path.parts[0]) if relative_path.parts else ""

        return first_dir in self.include_dirs

    def extract_imports(self, content: str) -> tuple:
        """Extract import statements and categorize them"""
        local_imports = []
        external_imports = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        if module_name in self.include_dirs:
                            local_imports.append(ast.unparse(node))
                        else:
                            import_stmt = ast.unparse(node)
                            external_imports.append(import_stmt)
                            self.external_imports.add(import_stmt)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        if module_name in self.include_dirs:
                            local_imports.append(ast.unparse(node))
                        else:
                            import_stmt = ast.unparse(node)
                            external_imports.append(import_stmt)
                            self.external_imports.add(import_stmt)
                    else:
                        # Handle relative imports
                        import_stmt = ast.unparse(node)
                        external_imports.append(import_stmt)
                        self.external_imports.add(import_stmt)
        except:
            # Fallback to regex if AST parsing fails
            import_pattern = r'^(?:from\s+[\w.]+\s+)?import\s+.+$'
            for line in content.split('\n'):
                if re.match(import_pattern, line.strip()):
                    if any(d in line for d in self.include_dirs):
                        local_imports.append(line.strip())
                    else:
                        external_imports.append(line.strip())
                        self.external_imports.add(line.strip())

        return local_imports, external_imports

    def remove_all_imports(self, content: str) -> str:
        """Remove all import statements from content"""
        lines = content.split('\n')
        result = []
        in_multiline_import = False

        for line in lines:
            stripped = line.strip()

            # Skip import lines
            if stripped.startswith('import ') or stripped.startswith('from '):
                if '(' in line and ')' not in line:
                    in_multiline_import = True
                elif ')' in line:
                    in_multiline_import = False
                continue

            if in_multiline_import:
                if ')' in line:
                    in_multiline_import = False
                continue

            result.append(line)

        return '\n'.join(result)

    def process_file(self, filepath: Path) -> str:
        """Process a single Python file"""
        if str(filepath) in self.processed_files:
            return ""

        self.processed_files.add(str(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract imports first to collect external dependencies
        local_imports, external_imports = self.extract_imports(content)

        # Remove all imports (both local and external)
        content = self.remove_all_imports(content)

        # Remove empty lines at start/end
        content = content.strip()

        if not content:
            return ""

        # Add file header comment
        relative_path = filepath.relative_to(self.project_root)
        header = f"\n# {'=' * 80}\n# File: {relative_path}\n# {'=' * 80}\n"

        return header + content + "\n"

    def collect_files(self) -> List[Path]:
        """Collect all Python files to bundle"""
        files = []

        for include_dir in self.include_dirs:
            dir_path = self.project_root / include_dir
            if dir_path.exists():
                for py_file in dir_path.rglob('*.py'):
                    if self.should_include_file(py_file):
                        files.append(py_file)

        # Sort files by dependency order (basic heuristic)
        def sort_key(filepath: Path):
            filepath_str = str(filepath)
            parts = filepath.parts
            
            # Process in order: config, vendor, database, app, routes, bootstrap
            # Bootstrap MUST be last because it calls register_providers and create_app
            order = {
                'config': 0,
                'vendor': 1,
                'database': 2,
                'app': 3,
                'routes': 4,
                'bootstrap': 5,  # Bootstrap last!
            }
            first_dir = parts[-len(filepath.relative_to(self.project_root).parts)]
            dir_order = order.get(first_dir, 99)
            
            # Special handling for base classes and middleware - always process first within their directory
            base_classes = [
                'app/Http/Controllers/Controller.py',
                'app/Models/Model.py',
                'vendor/Illuminate/Database/Model.py',
                'vendor/Illuminate/Database/Migration.py',
            ]
            
            # Middleware must be processed before controllers that use them
            middleware_files = [
                'app/Http/Middleware/AuthMiddleware.py',
                'app/Http/Middleware/MethodOverrideMiddleware.py',
            ]
            
            # Routing files order: RouteGroup.py (PendingRoute) BEFORE ImprovedRouter.py (ImprovedRoute)
            # Because ImprovedRoute uses PendingRoute class
            if filepath_str.endswith('vendor/Illuminate/Routing/RouteGroup.py'.replace('/', os.sep)):
                return (dir_order, 0, str(filepath))  # RouteGroup first (has PendingRoute)
            elif filepath_str.endswith('vendor/Illuminate/Routing/ImprovedRouter.py'.replace('/', os.sep)):
                return (dir_order, 1, str(filepath))  # ImprovedRouter second (uses PendingRoute)
            
            # Bootstrap files order is critical: providers.py BEFORE app.py
            # Because app.py's create_app() calls register_providers() from providers.py
            if filepath_str.endswith('bootstrap/providers.py'.replace('/', os.sep)):
                return (dir_order, 0, str(filepath))  # Providers first
            elif filepath_str.endswith('bootstrap/app.py'.replace('/', os.sep)):
                return (dir_order, 1, str(filepath))  # App second
            
            # Check if this is a base class (highest priority)
            for base_class in base_classes:
                if filepath_str.endswith(base_class.replace('/', os.sep)):
                    # Give base classes highest priority (lower number)
                    return (dir_order, 0, str(filepath))
            
            # Check if this is middleware (second priority)
            for middleware in middleware_files:
                if filepath_str.endswith(middleware.replace('/', os.sep)):
                    # Give middleware second priority
                    return (dir_order, 1, str(filepath))
            
            # Regular files (lowest priority)
            return (dir_order, 2, str(filepath))

        files.sort(key=sort_key)
        return files

    def copy_resources(self, output_dir: Path):
        """Copy resources directory to output directory"""
        source_resources = self.project_root / "resources"
        dest_resources = output_dir / "resources"

        if source_resources.exists():
            # Remove existing resources in output if exists
            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            
            # Copy entire resources directory
            shutil.copytree(source_resources, dest_resources)
            print(f"✅ Copied resources/ to {dest_resources}")
        else:
            print("⚠️  No resources/ directory found")

    def copy_static_files(self, output_dir: Path):
        """Copy public/static directory to output directory"""
        source_static = self.project_root / "public" / "static"
        dest_static = output_dir / "public" / "static"

        if source_static.exists():
            # Remove existing static in output if exists
            if dest_static.exists():
                shutil.rmtree(dest_static)
            
            # Create public directory
            dest_static.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy static directory
            shutil.copytree(source_static, dest_static)
            print(f"✅ Copied public/static/ to {dest_static}")
        else:
            print("⚠️  No public/static/ directory found")

    def build(self, output_file: str = "api/index.py"):
        """Build the bundle"""
        print("🔨 Starting Larathon bundler...")

        # Collect all files
        files = self.collect_files()
        print(f"📦 Found {len(files)} files to bundle")

        # Process each file
        for filepath in files:
            content = self.process_file(filepath)
            if content:
                self.bundle_content.append(content)

        # Build final bundle
        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write('"""\n')
            f.write('Larathon Application Bundle\n')
            f.write('Auto-generated by: python artisan.py build\n')
            f.write('DO NOT EDIT THIS FILE MANUALLY\n')
            f.write('"""\n\n')

            # Write external imports
            f.write("# External Dependencies\n")
            for imp in sorted(self.external_imports):
                f.write(f"{imp}\n")
            f.write("\n")

            # Write bundled code
            for content in self.bundle_content:
                f.write(content)

            # Write application entry point
            f.write("\n# " + "=" * 80 + "\n")
            f.write("# Application Entry Point for Vercel\n")
            f.write("# " + "=" * 80 + "\n\n")
            f.write("# Create app instance (all dependencies should be loaded by now)\n")
            f.write("app = create_app()\n")

        print(f"✅ Bundle created: {output_path}")
        print(f"📊 Total files bundled: {len(self.processed_files)}")
        print(f"📦 Bundle size: {os.path.getsize(output_path) / 1024:.2f} KB")

        # Copy resources and static files
        output_dir = output_path.parent
        self.copy_resources(output_dir)
        self.copy_static_files(output_dir)
        self.copy_requirements(output_dir)

        return output_path
    
    def copy_requirements(self, output_dir: Path):
        """Copy requirements.txt to output directory"""
        source_req = self.project_root / "requirements.txt"
        dest_req = output_dir / "requirements.txt"

        if source_req.exists():
            import shutil
            shutil.copy2(source_req, dest_req)
            print(f"✅ Copied requirements.txt to {dest_req}")
        else:
            print("⚠️  No requirements.txt found")


def bundle_application(project_root: str = "."):
    """Main function to bundle the application"""
    bundler = PythonBundler(project_root)
    return bundler.build()

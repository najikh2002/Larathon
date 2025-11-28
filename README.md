# Getting Started with Larathon

Larathon is a lightweight, Laravel-inspired web framework built with Python and FastAPI, designed to streamline modern web application development using familiar conventions.

## Requirements

* Python 3.11.3
* pip (Python package manager)

---

## 1. Create a Virtual Environment

Initialize a virtual environment using Python 3.11.3:

```bash
python3 -m venv env
````

This will create an `env/` directory containing the isolated environment.

---

## 2. Activate the Environment

Activate the virtual environment based on your OS:

**macOS / Linux**

```bash
source env/bin/activate
```

**Windows (CMD)**

```cmd
env\Scripts\activate
```

**Windows (PowerShell)**

```powershell
.\env\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

Once the environment is active, install all required packages:

```bash
pip install -r requirements.txt
```

---

## 4. Configure Database

Larathon supports three database engines: **SQLite**, **MySQL**, and **PostgreSQL**.

### Database Configuration

Edit your `.env` file and set the `DB_CONNECTION` variable:

**SQLite** (default - no additional setup required):
```env
DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite
```

**MySQL**:
```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=larathon
DB_USERNAME=root
DB_PASSWORD=your-password
```

**PostgreSQL**:
```env
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=larathon
DB_USERNAME=postgres
DB_PASSWORD=your-password
```

---

## 5. Run Database Migrations

Larathon uses an artisan-style CLI tool for managing the project. To apply all database migrations:

```bash
python artisan.py migrate
```

---

## 6. Generate a Model (Optional)

To generate a model, resource-style controller, and a migration file, run:

```bash
python artisan.py make:model ModelName -r -m
```

Replace `ModelName` with your desired class name.

---

## 7. Define Your Routes

HTTP routes are defined in:

```text
routes/web.py
```

Example:

```python
from vendor.Illuminate.Support.Facades.Route import Route
from app.Http.Controllers.WelcomeController import WelcomeController

Route.get("/", WelcomeController.index)
```

---

## 8. Start the Development Server

Launch the built-in development server:

```bash
python artisan.py serve
```

The application will be available at:

```
http://127.0.0.1:8000
```

---

## 9. Deployment to Vercel

Larathon can be easily deployed to Vercel with Supabase as the database backend.

### Prerequisites

1. A [Vercel](https://vercel.com) account
2. A [Supabase](https://supabase.com) project
3. Vercel CLI installed: `npm i -g vercel`

### Step-by-Step Deployment

#### 1. Setup Supabase Database

1. Create a new project on [Supabase](https://supabase.com)
2. Go to **Project Settings** → **Database**
3. Copy your database credentials:
   - Host (Connection pooling recommended)
   - Port
   - Database name
   - Username
   - Password

#### 2. Build Your Application

Run the build command to bundle all your code into a single file:

```bash
python artisan.py build
```

**What happens during build:**
1. **Code Bundling**: All Python files from `app/`, `config/`, `bootstrap/`, `vendor/`, `database/`, and `routes/` are combined into a single `api/index.py` file
2. **Import Resolution**: All local imports are resolved and external dependencies are preserved
3. **Configuration Files**: Generates `vercel.json` and `.vercelignore` for deployment

This creates:
- `api/index.py` - Single bundled file containing all your application code (ready for Vercel)
- `vercel.json` - Vercel serverless configuration
- `.vercelignore` - Excludes source files (only bundled file is deployed)

**Why bundling?**
Vercel's serverless functions have limitations with local module imports. Bundling ensures all your code is in one file, eliminating import issues.

#### 3. Configure Environment Variables

Create environment variables in your Vercel project:

```bash
# Option 1: Via Vercel Dashboard
# Go to your project → Settings → Environment Variables

# Option 2: Via CLI during deployment
vercel env add DB_CONNECTION
vercel env add DB_HOST
vercel env add DB_PORT
vercel env add DB_DATABASE
vercel env add DB_USERNAME
vercel env add DB_PASSWORD
vercel env add SECRET_KEY
```

Example values for Supabase:
```
DB_CONNECTION=pgsql
DB_HOST=db.xxxxxxxxxxxxx.supabase.co
DB_PORT=6543
DB_DATABASE=postgres
DB_USERNAME=postgres.xxxxxxxxxxxxx
DB_PASSWORD=your-password
SECRET_KEY=your-secret-key
```

**Important:** Use Connection Pooling host from Supabase (port 6543) for serverless functions!

#### 4. Deploy to Vercel

```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

#### 5. Run Migrations

After deployment, you need to run migrations manually:

```bash
# Connect to your Supabase database and run migrations locally
# Make sure your .env points to Supabase
python artisan.py migrate
```

Alternatively, you can run migrations directly in Supabase SQL Editor using the migration files.

### Updating Your Deployment

```bash
# Make your changes
git add .
git commit -m "Your changes"

# Deploy updates
vercel --prod
```

---

## 10. Contributing

We welcome contributions from the community!

### Forking and Setup

1. Fork the repository on GitHub.
2. Clone your forked repository:

   ```bash
   git clone https://github.com/najikh2002/Larathon.git
   cd Larathon
   ```
3. Add the upstream repository:

   ```bash
   git remote add upstream https://github.com/najikh2002/Larathon.git
   ```
4. Create a new feature branch before making changes:

   ```bash
   git checkout -b feature/<feature-name>
   ```
5. After making your changes, commit and push:

   ```bash
   git commit -m "Add <feature-name>"
   git push origin feature/<feature-name>
   ```
6. Open a Pull Request (PR) to the main repository.

---

## 11. Development Progress

| Feature                             | Status        |
| ----------------------------------- | ------------- |
| Format Layout Viewers               | ☐ In Progress |
| `[page].blade.py` Dynamic Templates | ☐ In Progress |
| Middleware Route Support            | ☐ In Progress |
| Named Routes                        | ☐ In Progress |
| Authentication Templates            | ☐ In Progress |

> ✅ = Done  ☐ = In Progress  🚧 = Planned

---

## 12. License

Larathon is open-source and distributed under the **MIT License**.

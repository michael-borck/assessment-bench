// Simplified database operations for testing
use anyhow::Result;
use sqlx::{sqlite::SqlitePool, Row};
// Remove unused import

#[derive(Clone)]
pub struct SimpleDatabase {
    pool: SqlitePool,
}

impl SimpleDatabase {
    pub async fn new() -> Result<Self> {
        // Use a temporary directory for development to avoid permission issues
        let db_dir = std::env::temp_dir().join("assessment-bench");
        std::fs::create_dir_all(&db_dir)?;
        
        let db_path = db_dir.join("assessment_bench.db");
        let database_url = format!("sqlite:{}", db_path.display());
        log::info!("Connecting to database: {}", database_url);
        
        let pool = SqlitePool::connect(&database_url).await?;
        
        Ok(Self { pool })
    }

    pub async fn new_in_memory() -> Result<Self> {
        let database_url = "sqlite::memory:";
        log::info!("Creating in-memory database: {}", database_url);
        
        let pool = SqlitePool::connect(database_url).await?;
        let db = Self { pool };
        
        // Run migrations immediately for in-memory database
        db.migrate().await?;
        
        Ok(db)
    }

    pub async fn migrate(&self) -> Result<()> {
        log::info!("Running database migrations...");
        
        // Create projects table
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                config TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // Create LLM providers table
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS llm_providers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                provider_type TEXT NOT NULL,
                config TEXT NOT NULL
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // Create submissions table
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS submissions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_type TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                status TEXT NOT NULL,
                extracted_text TEXT,
                analysis_cache TEXT,
                imported_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        log::info!("Database migrations completed");
        Ok(())
    }

    pub async fn test_connection(&self) -> Result<()> {
        let row = sqlx::query("SELECT 1 as test")
            .fetch_one(&self.pool)
            .await?;
        
        let test_value: i32 = row.get("test");
        if test_value == 1 {
            log::info!("Database connection test successful");
            Ok(())
        } else {
            Err(anyhow::anyhow!("Database connection test failed"))
        }
    }

    pub async fn create_project_simple(
        &self,
        name: String,
        description: Option<String>,
    ) -> Result<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let now = chrono::Utc::now().to_rfc3339();
        let config = serde_json::json!({
            "tiers_enabled": ["basic"],
            "repetitions": 1,
            "providers": []
        }).to_string();

        sqlx::query(
            r#"
            INSERT INTO projects (id, name, description, config, created_at, updated_at)
            VALUES (?1, ?2, ?3, ?4, ?5, ?6)
            "#,
        )
        .bind(&id)
        .bind(&name)
        .bind(&description)
        .bind(&config)
        .bind(&now)
        .bind(&now)
        .execute(&self.pool)
        .await?;

        log::info!("Created project: {} ({})", name, id);
        Ok(id)
    }

    pub async fn list_projects(&self) -> Result<Vec<(String, String)>> {
        let rows = sqlx::query("SELECT id, name FROM projects ORDER BY created_at DESC")
            .fetch_all(&self.pool)
            .await?;

        let mut projects = Vec::new();
        for row in rows {
            let id: String = row.get("id");
            let name: String = row.get("name");
            projects.push((id, name));
        }

        Ok(projects)
    }

    pub async fn add_provider_simple(
        &self,
        name: String,
        provider_type: String,
        model: String,
    ) -> Result<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let config = serde_json::json!({
            "model": model,
            "temperature": 0.7,
            "max_tokens": 1000
        }).to_string();

        sqlx::query(
            "INSERT INTO llm_providers (id, name, provider_type, config) VALUES (?1, ?2, ?3, ?4)"
        )
        .bind(&id)
        .bind(&name)
        .bind(&provider_type)
        .bind(&config)
        .execute(&self.pool)
        .await?;

        log::info!("Added provider: {} ({}) - {}", name, provider_type, id);
        Ok(id)
    }

    pub async fn list_providers(&self) -> Result<Vec<(String, String, String)>> {
        let rows = sqlx::query("SELECT id, name, provider_type FROM llm_providers ORDER BY name")
            .fetch_all(&self.pool)
            .await?;

        let mut providers = Vec::new();
        for row in rows {
            let id: String = row.get("id");
            let name: String = row.get("name");
            let provider_type: String = row.get("provider_type");
            providers.push((id, name, provider_type));
        }

        Ok(providers)
    }
}
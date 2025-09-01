use anyhow::Result;
use sqlx::{sqlite::SqlitePool, Pool, Sqlite};

pub mod models;
pub mod migrations;

use models::*;

#[derive(Clone)]
pub struct Database {
    pool: Pool<Sqlite>,
}

impl Database {
    pub async fn new() -> Result<Self> {
        // Create database in current directory for now
        let database_url = "sqlite:assessment_bench.db";
        log::info!("Opening database at: {}", database_url);
        
        let pool = SqlitePool::connect(database_url).await?;
        
        Ok(Self { pool })
    }

    pub async fn migrate(&self) -> Result<()> {
        migrations::run_migrations(&self.pool).await
    }

    // Project operations
    pub async fn create_project(
        &self,
        name: String,
        description: Option<String>,
        config: serde_json::Value,
    ) -> Result<Project> {
        let id = uuid::Uuid::new_v4();
        let now = chrono::Utc::now();
        
        let project = sqlx::query_as!(
            Project,
            r#"
            INSERT INTO projects (id, name, description, config, created_at, updated_at)
            VALUES (?1, ?2, ?3, ?4, ?5, ?6)
            RETURNING id, name, description, config, created_at, updated_at
            "#,
            id,
            name,
            description,
            config,
            now,
            now
        )
        .fetch_one(&self.pool)
        .await?;

        Ok(project)
    }

    pub async fn get_projects(&self) -> Result<Vec<Project>> {
        let projects = sqlx::query_as!(
            Project,
            "SELECT id, name, description, config, created_at, updated_at FROM projects ORDER BY created_at DESC"
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(projects)
    }

    pub async fn get_project(&self, id: uuid::Uuid) -> Result<Option<Project>> {
        let project = sqlx::query_as!(
            Project,
            "SELECT id, name, description, config, created_at, updated_at FROM projects WHERE id = ?",
            id
        )
        .fetch_optional(&self.pool)
        .await?;

        Ok(project)
    }

    pub async fn delete_project(&self, id: uuid::Uuid) -> Result<bool> {
        let result = sqlx::query!("DELETE FROM projects WHERE id = ?", id)
            .execute(&self.pool)
            .await?;

        Ok(result.rows_affected() > 0)
    }

    // Provider operations
    pub async fn add_provider(&self, provider: LLMProvider) -> Result<LLMProvider> {
        let provider_json = serde_json::to_value(&provider)?;
        
        sqlx::query!(
            "INSERT INTO llm_providers (id, name, provider_type, config) VALUES (?1, ?2, ?3, ?4)",
            provider.id,
            provider.name,
            provider.provider_type,
            provider_json
        )
        .execute(&self.pool)
        .await?;

        Ok(provider)
    }

    pub async fn get_providers(&self) -> Result<Vec<LLMProvider>> {
        let rows = sqlx::query!(
            "SELECT id, name, provider_type, config FROM llm_providers ORDER BY name"
        )
        .fetch_all(&self.pool)
        .await?;

        let mut providers = Vec::new();
        for row in rows {
            if let Ok(provider) = serde_json::from_value(row.config) {
                providers.push(provider);
            }
        }

        Ok(providers)
    }

    pub async fn delete_provider(&self, id: &str) -> Result<bool> {
        let result = sqlx::query!("DELETE FROM llm_providers WHERE id = ?", id)
            .execute(&self.pool)
            .await?;

        Ok(result.rows_affected() > 0)
    }

    // Submission operations
    pub async fn create_submission(&self, submission: Submission) -> Result<Submission> {
        let submission_json = serde_json::to_value(&submission)?;
        
        sqlx::query!(
            r#"
            INSERT INTO submissions (
                id, project_id, original_filename, file_hash, 
                file_type, word_count, status, extracted_text, 
                analysis_cache, imported_at
            ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)
            "#,
            submission.id,
            submission.project_id,
            submission.original_filename,
            submission.file_hash,
            submission.file_type,
            submission.word_count,
            submission.status,
            submission.extracted_text,
            submission_json,
            submission.imported_at
        )
        .execute(&self.pool)
        .await?;

        Ok(submission)
    }

    pub async fn get_submissions(&self, project_id: uuid::Uuid) -> Result<Vec<Submission>> {
        let rows = sqlx::query!(
            r#"
            SELECT id, project_id, original_filename, file_hash, 
                   file_type, word_count, status, extracted_text, 
                   analysis_cache, imported_at
            FROM submissions 
            WHERE project_id = ? 
            ORDER BY imported_at DESC
            "#,
            project_id
        )
        .fetch_all(&self.pool)
        .await?;

        let mut submissions = Vec::new();
        for row in rows {
            if let Ok(submission_data) = serde_json::from_value::<serde_json::Value>(row.analysis_cache) {
                // Reconstruct submission from database row
                let submission = Submission {
                    id: uuid::Uuid::parse_str(&row.id).unwrap_or_default(),
                    project_id: uuid::Uuid::parse_str(&row.project_id).unwrap_or_default(),
                    original_filename: row.original_filename,
                    file_hash: row.file_hash,
                    file_type: row.file_type,
                    word_count: row.word_count,
                    status: row.status,
                    extracted_text: row.extracted_text,
                    analysis_cache: None, // TODO: Deserialize properly
                    imported_at: chrono::DateTime::parse_from_rfc3339(&row.imported_at)
                        .unwrap()
                        .with_timezone(&chrono::Utc()),
                };
                submissions.push(submission);
            }
        }

        Ok(submissions)
    }
}
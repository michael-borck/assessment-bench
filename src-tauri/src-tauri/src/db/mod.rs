use anyhow::Result;
use sqlx::{sqlite::SqlitePool, Pool, Sqlite, Row};

pub mod models;
pub mod migrations;
pub mod simple;
pub mod test;

use models::*;
pub use simple::SimpleDatabase;

#[derive(Clone)]
pub struct Database {
    pool: Pool<Sqlite>,
}

#[allow(dead_code)]
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
        
        let id_str = id.to_string();
        let now_str = now.to_rfc3339();
        let config_str = config.to_string();
        
        sqlx::query(
            r#"
            INSERT INTO projects (id, name, description, config, created_at, updated_at)
            VALUES (?1, ?2, ?3, ?4, ?5, ?6)
            "#
        )
        .bind(&id_str)
        .bind(&name)
        .bind(&description)
        .bind(&config_str)
        .bind(&now_str)
        .bind(&now_str)
        .execute(&self.pool)
        .await?;

        let project = Project {
            id,
            name,
            description,
            config,
            created_at: now,
            updated_at: now,
        };

        Ok(project)
    }

    pub async fn get_projects(&self) -> Result<Vec<Project>> {
        let rows = sqlx::query(
            "SELECT id, name, description, config, created_at, updated_at FROM projects ORDER BY created_at DESC"
        )
        .fetch_all(&self.pool)
        .await?;

        let mut projects = Vec::new();
        for row in rows {
            let id: String = row.get(0);
            let name: String = row.get(1);
            let description: Option<String> = row.get(2);
            let config_str: String = row.get(3);
            let created_at_str: String = row.get(4);
            let updated_at_str: String = row.get(5);
            
            if let (Ok(id), Ok(created_at), Ok(updated_at), Ok(config)) = (
                uuid::Uuid::parse_str(&id),
                chrono::DateTime::parse_from_rfc3339(&created_at_str).map(|dt| dt.with_timezone(&chrono::Utc)),
                chrono::DateTime::parse_from_rfc3339(&updated_at_str).map(|dt| dt.with_timezone(&chrono::Utc)),
                serde_json::from_str::<serde_json::Value>(&config_str),
            ) {
                projects.push(Project {
                    id,
                    name,
                    description,
                    config,
                    created_at,
                    updated_at,
                });
            }
        }

        Ok(projects)
    }

    pub async fn get_project(&self, id: uuid::Uuid) -> Result<Option<Project>> {
        let id_str = id.to_string();
        let row = sqlx::query(
            "SELECT id, name, description, config, created_at, updated_at FROM projects WHERE id = ?"
        )
        .bind(&id_str)
        .fetch_optional(&self.pool)
        .await?;

        if let Some(row) = row {
            let id_str: String = row.get(0);
            let name: String = row.get(1);
            let description: Option<String> = row.get(2);
            let config_str: String = row.get(3);
            let created_at_str: String = row.get(4);
            let updated_at_str: String = row.get(5);
            
            if let (Ok(id), Ok(created_at), Ok(updated_at), Ok(config)) = (
                uuid::Uuid::parse_str(&id_str),
                chrono::DateTime::parse_from_rfc3339(&created_at_str).map(|dt| dt.with_timezone(&chrono::Utc)),
                chrono::DateTime::parse_from_rfc3339(&updated_at_str).map(|dt| dt.with_timezone(&chrono::Utc)),
                serde_json::from_str::<serde_json::Value>(&config_str),
            ) {
                return Ok(Some(Project {
                    id,
                    name,
                    description,
                    config,
                    created_at,
                    updated_at,
                }));
            }
        }

        Ok(None)
    }

    pub async fn delete_project(&self, id: uuid::Uuid) -> Result<bool> {
        let id_str = id.to_string();
        let result = sqlx::query("DELETE FROM projects WHERE id = ?")
            .bind(&id_str)
            .execute(&self.pool)
            .await?;

        Ok(result.rows_affected() > 0)
    }

    // Provider operations
    pub async fn add_provider(&self, provider: LLMProvider) -> Result<LLMProvider> {
        let config_json = serde_json::to_string(&provider.config)?;
        
        sqlx::query(
            "INSERT INTO llm_providers (id, name, provider_type, config) VALUES (?1, ?2, ?3, ?4)"
        )
        .bind(&provider.id)
        .bind(&provider.name)
        .bind(&provider.provider_type)
        .bind(&config_json)
        .execute(&self.pool)
        .await?;

        Ok(provider)
    }

    pub async fn get_providers(&self) -> Result<Vec<LLMProvider>> {
        let rows = sqlx::query(
            "SELECT id, name, provider_type, config FROM llm_providers ORDER BY name"
        )
        .fetch_all(&self.pool)
        .await?;

        let mut providers = Vec::new();
        for row in rows {
            let id: String = row.get(0);
            let name: String = row.get(1);
            let provider_type: String = row.get(2);
            let config_str: String = row.get(3);
            
            if let Ok(config) = serde_json::from_str(&config_str) {
                providers.push(LLMProvider {
                    id,
                    name,
                    provider_type,
                    config,
                });
            }
        }

        Ok(providers)
    }

    pub async fn delete_provider(&self, id: &str) -> Result<bool> {
        let result = sqlx::query("DELETE FROM llm_providers WHERE id = ?")
            .bind(id)
            .execute(&self.pool)
            .await?;

        Ok(result.rows_affected() > 0)
    }

    // Submission operations
    pub async fn create_submission(&self, submission: Submission) -> Result<Submission> {
        let analysis_cache_json = if let Some(cache) = &submission.analysis_cache {
            serde_json::to_string(cache)?
        } else {
            "null".to_string()
        };
        
        sqlx::query(
            r#"
            INSERT INTO submissions (
                id, project_id, original_filename, file_hash, 
                file_type, word_count, status, extracted_text, 
                analysis_cache, imported_at
            ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)
            "#
        )
        .bind(submission.id.to_string())
        .bind(submission.project_id.to_string())
        .bind(&submission.original_filename)
        .bind(&submission.file_hash)
        .bind(&submission.file_type)
        .bind(submission.word_count as i64)
        .bind(&submission.status)
        .bind(&submission.extracted_text)
        .bind(&analysis_cache_json)
        .bind(submission.imported_at.to_rfc3339())
        .execute(&self.pool)
        .await?;

        Ok(submission)
    }

    pub async fn get_submissions(&self, project_id: uuid::Uuid) -> Result<Vec<Submission>> {
        let rows = sqlx::query(
            r#"
            SELECT id, project_id, original_filename, file_hash, 
                   file_type, word_count, status, extracted_text, 
                   analysis_cache, imported_at
            FROM submissions 
            WHERE project_id = ? 
            ORDER BY imported_at DESC
            "#
        )
        .bind(project_id.to_string())
        .fetch_all(&self.pool)
        .await?;

        let mut submissions = Vec::new();
        for row in rows {
            let id_str: String = row.get(0);
            let project_id_str: String = row.get(1);
            let original_filename: String = row.get(2);
            let file_hash: String = row.get(3);
            let file_type: String = row.get(4);
            let word_count: i64 = row.get(5);
            let status: String = row.get(6);
            let extracted_text: Option<String> = row.get(7);
            let analysis_cache_str: String = row.get(8);
            let imported_at_str: String = row.get(9);
            
            if let (Ok(id), Ok(project_id), Ok(imported_at)) = (
                uuid::Uuid::parse_str(&id_str),
                uuid::Uuid::parse_str(&project_id_str),
                chrono::DateTime::parse_from_rfc3339(&imported_at_str).map(|dt| dt.with_timezone(&chrono::Utc))
            ) {
                let analysis_cache = if analysis_cache_str != "null" {
                    serde_json::from_str(&analysis_cache_str).ok()
                } else {
                    None
                };
                
                let submission = Submission {
                    id,
                    project_id,
                    original_filename,
                    file_hash,
                    file_type,
                    word_count: word_count as u32,
                    status,
                    extracted_text,
                    analysis_cache,
                    imported_at,
                };
                submissions.push(submission);
            }
        }

        Ok(submissions)
    }
}
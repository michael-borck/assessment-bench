use anyhow::Result;
use sqlx::{Pool, Sqlite};

pub async fn run_migrations(pool: &Pool<Sqlite>) -> Result<()> {
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
    .execute(pool)
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
    .execute(pool)
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
    .execute(pool)
    .await?;

    // Create grading results table
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS grading_results (
            id TEXT PRIMARY KEY,
            submission_id TEXT NOT NULL,
            provider_id TEXT NOT NULL,
            tier TEXT NOT NULL,
            run_number INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            raw_response TEXT NOT NULL,
            overall_grade TEXT,
            total_points REAL,
            rubric_scores TEXT NOT NULL,
            summary_feedback TEXT,
            strengths TEXT NOT NULL,
            improvements TEXT NOT NULL,
            validation_result TEXT NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE,
            FOREIGN KEY (provider_id) REFERENCES llm_providers (id) ON DELETE CASCADE
        )
        "#,
    )
    .execute(pool)
    .await?;

    // Create rubrics table
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS rubrics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            criteria TEXT NOT NULL,
            total_points REAL NOT NULL
        )
        "#,
    )
    .execute(pool)
    .await?;

    // Create indexes for better performance
    sqlx::query(
        r#"
        CREATE INDEX IF NOT EXISTS idx_submissions_project_id 
        ON submissions (project_id)
        "#,
    )
    .execute(pool)
    .await?;

    sqlx::query(
        r#"
        CREATE INDEX IF NOT EXISTS idx_grading_results_submission_id 
        ON grading_results (submission_id)
        "#,
    )
    .execute(pool)
    .await?;

    sqlx::query(
        r#"
        CREATE INDEX IF NOT EXISTS idx_grading_results_provider_tier 
        ON grading_results (provider_id, tier)
        "#,
    )
    .execute(pool)
    .await?;

    log::info!("Database migrations completed successfully");
    Ok(())
}
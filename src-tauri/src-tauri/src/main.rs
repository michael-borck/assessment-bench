// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod db;
mod document;
mod document_analysis;
mod grading;
mod llm;
mod analysis;

use commands::*;
use db::{SimpleDatabase, test::run_database_tests};

#[tokio::main]
async fn main() {
    env_logger::init();

    // Run database tests during development (non-blocking)
    if std::env::var("SKIP_DB_TESTS").is_err() {
        println!("🚀 Starting AssessmentBench...");
        if let Err(e) = run_database_tests().await {
            eprintln!("⚠️  Database tests failed (non-blocking): {}", e);
            eprintln!("   Continuing with application startup...");
        }
    }

    // Initialize database with graceful error handling
    let database = match SimpleDatabase::new().await {
        Ok(db) => {
            if let Err(e) = db.migrate().await {
                eprintln!("⚠️  Database migration failed: {}", e);
            }
            db
        }
        Err(e) => {
            eprintln!("⚠️  Database initialization failed: {}", e);
            eprintln!("   Using fallback in-memory database for development...");
            SimpleDatabase::new_in_memory().await.expect("Failed to create in-memory database")
        }
    };

    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_sql::Builder::default().build())
        .manage(database)
        .invoke_handler(tauri::generate_handler![
            // Simple project management (working commands)
            create_project_simple,
            list_projects_simple,
            delete_project_simple,
            add_provider_simple,
            list_providers_simple,
            test_llm_provider,
            test_basic_grading,
            test_multiple_grading_runs,
            
            // Original project management (for future)
            create_project,
            get_projects,
            get_project,
            delete_project,
            
            // Provider management
            add_provider,
            get_providers,
            update_provider,
            delete_provider,
            
            // Document processing
            import_documents,
            get_submissions,
            
            // Grading
            start_grading,
            get_grading_status,
            get_results,
            
            // Analysis
            get_aggregated_results,
            export_results,
            analyze_document_with_lens,
            test_documentlens_integration
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
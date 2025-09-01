// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod db;
mod document;
mod grading;
mod llm;
mod analysis;

use commands::*;
use db::{SimpleDatabase, test::run_database_tests};

#[tokio::main]
async fn main() {
    env_logger::init();

    // Run database tests during development
    if std::env::var("SKIP_DB_TESTS").is_err() {
        println!("🚀 Starting AssessmentBench...");
        if let Err(e) = run_database_tests().await {
            eprintln!("❌ Database tests failed: {}", e);
            std::process::exit(1);
        }
    }

    // Initialize database
    let database = SimpleDatabase::new().await.expect("Failed to initialize database");
    database.migrate().await.expect("Failed to run migrations");

    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
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
            export_results
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
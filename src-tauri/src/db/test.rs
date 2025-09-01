// Database tests
#[cfg(test)]
mod tests {
    use super::simple::SimpleDatabase;

    #[tokio::test]
    async fn test_database_connection() {
        let db = SimpleDatabase::new().await.expect("Failed to create database");
        db.migrate().await.expect("Failed to run migrations");
        db.test_connection().await.expect("Database connection test failed");
    }

    #[tokio::test]
    async fn test_create_project() {
        let db = SimpleDatabase::new().await.expect("Failed to create database");
        db.migrate().await.expect("Failed to run migrations");
        
        let project_id = db.create_project_simple(
            "Test Project".to_string(),
            Some("A test project for database testing".to_string())
        ).await.expect("Failed to create project");

        assert!(!project_id.is_empty());
        
        let projects = db.list_projects().await.expect("Failed to list projects");
        assert!(!projects.is_empty());
        
        let found = projects.iter().any(|(id, name)| id == &project_id && name == "Test Project");
        assert!(found, "Created project not found in list");
    }

    #[tokio::test]
    async fn test_add_provider() {
        let db = SimpleDatabase::new().await.expect("Failed to create database");
        db.migrate().await.expect("Failed to run migrations");
        
        let provider_id = db.add_provider_simple(
            "Test OpenAI".to_string(),
            "openai".to_string(),
            "gpt-4".to_string()
        ).await.expect("Failed to add provider");

        assert!(!provider_id.is_empty());
        
        let providers = db.list_providers().await.expect("Failed to list providers");
        assert!(!providers.is_empty());
        
        let found = providers.iter().any(|(id, name, ptype)| {
            id == &provider_id && name == "Test OpenAI" && ptype == "openai"
        });
        assert!(found, "Created provider not found in list");
    }
}

// Standalone test functions that can be called from main
pub async fn run_database_tests() -> anyhow::Result<()> {
    println!("🔧 Running database tests...");
    
    // Test 1: Connection and Migration
    println!("  Testing database connection and migrations...");
    let db = SimpleDatabase::new().await?;
    db.migrate().await?;
    db.test_connection().await?;
    println!("  ✅ Database connection and migrations successful");
    
    // Test 2: Create Project
    println!("  Testing project creation...");
    let project_id = db.create_project_simple(
        "Sample Research Project".to_string(),
        Some("Testing the three-tier grading system".to_string())
    ).await?;
    
    let projects = db.list_projects().await?;
    assert!(!projects.is_empty());
    println!("  ✅ Project creation successful (ID: {})", project_id);
    
    // Test 3: Add Provider
    println!("  Testing provider management...");
    let provider_id = db.add_provider_simple(
        "OpenAI GPT-4".to_string(),
        "openai".to_string(),
        "gpt-4".to_string()
    ).await?;
    
    let providers = db.list_providers().await?;
    assert!(!providers.is_empty());
    println!("  ✅ Provider management successful (ID: {})", provider_id);
    
    // Test 4: List Data
    println!("  Current database contents:");
    println!("    Projects:");
    for (id, name) in projects {
        println!("      - {} ({})", name, id);
    }
    
    println!("    Providers:");
    for (id, name, ptype) in providers {
        println!("      - {} [{}] ({})", name, ptype, id);
    }
    
    println!("🎉 All database tests passed!");
    Ok(())
}
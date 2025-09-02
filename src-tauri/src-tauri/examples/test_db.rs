// Simple database test binary
use anyhow::Result;
use assessment_bench::db::{SimpleDatabase, test::run_database_tests};

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    
    println!("🧪 Testing AssessmentBench Database...");
    run_database_tests().await?;
    println!("✨ Database tests completed successfully!");
    
    Ok(())
}
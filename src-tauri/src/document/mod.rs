use std::path::Path;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Document {
    pub path: String,
    pub content: String,
    pub file_type: DocumentType,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum DocumentType {
    Word,
    Pdf,
    Text,
}

pub fn read_document(path: &Path) -> Result<Document, Box<dyn std::error::Error>> {
    // TODO: Implement document reading logic
    Ok(Document {
        path: path.to_string_lossy().to_string(),
        content: "Document content placeholder".to_string(),
        file_type: DocumentType::Word,
    })
}
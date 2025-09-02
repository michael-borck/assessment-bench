use anyhow::Result;
use std::path::Path;

pub struct DocumentData {
    pub filename: String,
    pub text: String,
    pub file_type: String,
    pub word_count: u32,
    pub hash: String,
}

pub async fn process_document(file_path: &str) -> Result<DocumentData> {
    let path = Path::new(file_path);
    let filename = path
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .to_string();

    let extension = path
        .extension()
        .unwrap_or_default()
        .to_string_lossy()
        .to_lowercase();

    let text = match extension.as_str() {
        "pdf" => extract_pdf_text(path).await?,
        "docx" => extract_docx_text(path).await?,
        "txt" | "md" => extract_text_file(path).await?,
        _ => return Err(anyhow::anyhow!("Unsupported file type: {}", extension)),
    };

    let word_count = count_words(&text);
    let hash = calculate_hash(&text);

    Ok(DocumentData {
        filename,
        text,
        file_type: extension,
        word_count,
        hash,
    })
}

async fn extract_pdf_text(path: &Path) -> Result<String> {
    let _file = std::fs::File::open(path)?;
    let text = pdf_extract::extract_text_from_mem(&std::fs::read(path)?)?;
    Ok(text)
}

async fn extract_docx_text(_path: &Path) -> Result<String> {
    // TODO: Implement DOCX extraction using docx-rs
    // For now, return placeholder
    Ok("DOCX text extraction not yet implemented".to_string())
}

async fn extract_text_file(path: &Path) -> Result<String> {
    let content = tokio::fs::read_to_string(path).await?;
    Ok(content)
}

fn count_words(text: &str) -> u32 {
    text.split_whitespace().count() as u32
}

fn calculate_hash(text: &str) -> String {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut hasher = DefaultHasher::new();
    text.hash(&mut hasher);
    format!("{:x}", hasher.finish())
}
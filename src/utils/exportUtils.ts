import { invoke } from '@tauri-apps/api/core';

export interface ExportData {
  results: any[];
  summary: {
    totalAssessments: number;
    averageScore: number;
    averageReliability: number;
    consistencyRate: number;
    providerBreakdown: { [key: string]: number };
    gradeDistribution: { [key: string]: number };
  };
  metadata: {
    exportDate: string;
    dateRange: string;
    filters: string[];
  };
}

// CSV Export
export const exportToCSV = async (data: ExportData): Promise<void> => {
  try {
    const csvContent = generateCSVContent(data);
    const filename = `grading_results_${new Date().toISOString().split('T')[0]}.csv`;
    
    await invoke('write_file', {
      filename,
      content: csvContent,
      directory: 'exports'
    });
    
    console.log(`Exported to ${filename}`);
  } catch (error) {
    console.error('Failed to export CSV:', error);
    // Fallback to browser download
    downloadCSV(data);
  }
};

const generateCSVContent = (data: ExportData): string => {
  const headers = [
    'ID',
    'Provider',
    'Model', 
    'Grade',
    'Score',
    'Reliability',
    'Consistency',
    'Timestamp',
    'Strengths',
    'Improvements'
  ].join(',');

  const rows = data.results.map(result => [
    result.id,
    result.provider,
    result.model || '',
    result.grade || '',
    result.score || '',
    result.reliability || '',
    result.consistency || '',
    result.timestamp,
    `"${(result.strengths || []).join('; ')}"`,
    `"${(result.improvements || []).join('; ')}"`,
  ].join(','));

  return [headers, ...rows].join('\n');
};

const downloadCSV = (data: ExportData): void => {
  const csvContent = generateCSVContent(data);
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `grading_results_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

// JSON Export
export const exportToJSON = async (data: ExportData): Promise<void> => {
  try {
    const jsonContent = JSON.stringify(data, null, 2);
    const filename = `grading_results_${new Date().toISOString().split('T')[0]}.json`;
    
    await invoke('write_file', {
      filename,
      content: jsonContent,
      directory: 'exports'
    });
    
    console.log(`Exported to ${filename}`);
  } catch (error) {
    console.error('Failed to export JSON:', error);
    // Fallback to browser download
    downloadJSON(data);
  }
};

const downloadJSON = (data: ExportData): void => {
  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `grading_results_${new Date().toISOString().split('T')[0]}.json`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

// PDF Export (using browser print for now)
export const exportToPDF = async (data: ExportData): Promise<void> => {
  try {
    // Create a detailed HTML report
    const htmlContent = generateHTMLReport(data);
    
    // Open in new window for printing
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(htmlContent);
      printWindow.document.close();
      printWindow.focus();
      
      // Auto-trigger print dialog
      setTimeout(() => {
        printWindow.print();
      }, 250);
    }
  } catch (error) {
    console.error('Failed to export PDF:', error);
    alert('PDF export failed. Please try again.');
  }
};

const generateHTMLReport = (data: ExportData): string => {
  const { results, summary, metadata } = data;
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>AssessmentBench Grading Report</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
        .header { border-bottom: 2px solid #3B82F6; padding-bottom: 20px; margin-bottom: 30px; }
        .title { font-size: 24px; font-weight: bold; color: #1F2937; margin: 0; }
        .subtitle { font-size: 14px; color: #6B7280; margin-top: 5px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #F9FAFB; padding: 15px; border-radius: 8px; border: 1px solid #E5E7EB; }
        .summary-card h3 { margin: 0 0 10px 0; font-size: 14px; color: #6B7280; text-transform: uppercase; }
        .summary-card .value { font-size: 24px; font-weight: bold; color: #1F2937; }
        .section { margin-bottom: 30px; }
        .section h2 { font-size: 18px; font-weight: bold; color: #1F2937; margin-bottom: 15px; border-bottom: 1px solid #E5E7EB; padding-bottom: 5px; }
        .table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .table th, .table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #E5E7EB; }
        .table th { background: #F9FAFB; font-weight: 600; color: #374151; }
        .grade { padding: 4px 8px; border-radius: 4px; font-weight: 500; }
        .grade-a { background: #D1FAE5; color: #065F46; }
        .grade-b { background: #DBEAFE; color: #1E40AF; }
        .grade-c { background: #FEF3C7; color: #92400E; }
        .grade-d { background: #FED7AA; color: #9A3412; }
        .grade-f { background: #FEE2E2; color: #991B1B; }
        .metadata { background: #F3F4F6; padding: 15px; border-radius: 8px; font-size: 12px; color: #6B7280; }
        @media print { body { margin: 0; } .header { page-break-after: avoid; } }
      </style>
    </head>
    <body>
      <div class="header">
        <h1 class="title">AssessmentBench Grading Report</h1>
        <p class="subtitle">Generated on ${metadata.exportDate}</p>
      </div>

      <div class="summary">
        <div class="summary-card">
          <h3>Total Assessments</h3>
          <div class="value">${summary.totalAssessments}</div>
        </div>
        <div class="summary-card">
          <h3>Average Score</h3>
          <div class="value">${summary.averageScore.toFixed(1)}%</div>
        </div>
        <div class="summary-card">
          <h3>Average Reliability</h3>
          <div class="value">${(summary.averageReliability * 100).toFixed(1)}%</div>
        </div>
        <div class="summary-card">
          <h3>Consistency Rate</h3>
          <div class="value">${summary.consistencyRate.toFixed(1)}%</div>
        </div>
      </div>

      <div class="section">
        <h2>Grade Distribution</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
          ${Object.entries(summary.gradeDistribution).map(([grade, count]) => `
            <div style="text-align: center;">
              <div class="grade grade-${grade.toLowerCase()}">${grade}</div>
              <div style="margin-top: 5px; font-weight: bold;">${count}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="section">
        <h2>Provider Performance</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
          ${Object.entries(summary.providerBreakdown).map(([provider, count]) => `
            <div style="text-align: center; background: #F9FAFB; padding: 10px; border-radius: 8px;">
              <div style="font-weight: bold; color: #1F2937;">${provider}</div>
              <div style="margin-top: 5px; color: #6B7280;">${count} assessments</div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="section">
        <h2>Recent Results</h2>
        <table class="table">
          <thead>
            <tr>
              <th>Provider</th>
              <th>Grade</th>
              <th>Score</th>
              <th>Reliability</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            ${results.slice(0, 20).map(result => `
              <tr>
                <td>${result.provider}</td>
                <td><span class="grade grade-${(result.grade || 'f').toLowerCase()}">${result.grade || 'N/A'}</span></td>
                <td>${result.score ? result.score + '%' : 'N/A'}</td>
                <td>${result.reliability ? (result.reliability * 100).toFixed(0) + '%' : 'N/A'}</td>
                <td>${new Date(result.timestamp).toLocaleString()}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="metadata">
        <strong>Export Details:</strong><br>
        Date Range: ${metadata.dateRange}<br>
        Filters Applied: ${metadata.filters.length > 0 ? metadata.filters.join(', ') : 'None'}<br>
        Generated by AssessmentBench v0.1.0
      </div>
    </body>
    </html>
  `;
};

// Enhanced export with filtering options
export interface ExportOptions {
  format: 'csv' | 'json' | 'pdf';
  dateRange?: {
    start: Date;
    end: Date;
  };
  providers?: string[];
  grades?: string[];
  includeRawResponses?: boolean;
}

export const exportResults = async (results: any[], options: ExportOptions): Promise<void> => {
  // Filter results based on options
  let filteredResults = [...results];
  
  if (options.dateRange) {
    filteredResults = filteredResults.filter(result => {
      const resultDate = new Date(result.timestamp);
      return resultDate >= options.dateRange!.start && resultDate <= options.dateRange!.end;
    });
  }
  
  if (options.providers && options.providers.length > 0) {
    filteredResults = filteredResults.filter(result => 
      options.providers!.includes(result.provider)
    );
  }
  
  if (options.grades && options.grades.length > 0) {
    filteredResults = filteredResults.filter(result => 
      result.grade && options.grades!.includes(result.grade)
    );
  }

  // Generate summary statistics
  const summary = {
    totalAssessments: filteredResults.length,
    averageScore: filteredResults.reduce((sum, r) => sum + (r.score || 0), 0) / filteredResults.length || 0,
    averageReliability: filteredResults.reduce((sum, r) => sum + (r.reliability || 0), 0) / filteredResults.length || 0,
    consistencyRate: filteredResults.filter(r => r.consistency === 'high').length / filteredResults.length * 100 || 0,
    providerBreakdown: filteredResults.reduce((acc, r) => {
      acc[r.provider] = (acc[r.provider] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number }),
    gradeDistribution: filteredResults.reduce((acc, r) => {
      if (r.grade) {
        acc[r.grade] = (acc[r.grade] || 0) + 1;
      }
      return acc;
    }, {} as { [key: string]: number })
  };

  const exportData: ExportData = {
    results: filteredResults,
    summary,
    metadata: {
      exportDate: new Date().toISOString(),
      dateRange: options.dateRange 
        ? `${options.dateRange.start.toLocaleDateString()} - ${options.dateRange.end.toLocaleDateString()}`
        : 'All time',
      filters: [
        ...(options.providers ? [`Providers: ${options.providers.join(', ')}`] : []),
        ...(options.grades ? [`Grades: ${options.grades.join(', ')}`] : [])
      ]
    }
  };

  switch (options.format) {
    case 'csv':
      await exportToCSV(exportData);
      break;
    case 'json':
      await exportToJSON(exportData);
      break;
    case 'pdf':
      await exportToPDF(exportData);
      break;
    default:
      throw new Error(`Unsupported export format: ${options.format}`);
  }
};
# Resume Screener Flow

```mermaid
graph TD
    A[Upload PDF Resume] --> B[Resume Parser]
    B --> C{Processing Pipeline}
    
    C -->|LLM Processing| D[Extract Main Info]
    C -->|Pattern Matching| E[Extract Extra-Curricular]
    
    D --> F[Parse Components]
    F --> |Academic| G[Academic Info]
    F --> |Skills| H[Technical Skills]
    F --> |Projects| I[Project Details]
    
    E --> J[Activities Info]
    
    G & H & I & J --> K[Score Calculation]
    
    K --> L[Generate Results]
    L --> M{Output}
    
    M -->|Visualization| N[Display Charts & Tables]
    M -->|Export| O[Save CSV/JSON Files]
    M -->|Scoring| P[Show Component Scores]
    
    style A fill:#f9f,stroke:#333
    style K fill:#bbf,stroke:#333
    style M fill:#bfb,stroke:#333
```

## Component Weights
- Academic Performance: 20%
- Technical Skills: 35%
- Projects: 30%
- Extra-Curricular: 15%

## Key Features
1. **Dual Processing**
   - LLM-based main information extraction
   - Pattern-based extra-curricular extraction

2. **Scoring System**
   - Normalized component scoring
   - Weighted aggregation
   - Performance metrics

3. **Output Generation**
   - Interactive visualizations
   - Structured data export
   - Detailed scoring breakdown 
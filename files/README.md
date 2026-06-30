# Sample Data Files

## Provided Files

### 1. `ILPA based Capital Accounting and Performance Metrics_ PIC, Net PIC, DPI, IRR.pdf`
- **Type**: Reference document
- **Purpose**: Explains fund performance metrics (PIC, DPI, IRR, TVPI)
- **Use for**: Text extraction and RAG (Retrieval Augmented Generation)
- **Contains**: Definitions, formulas, and explanations

## Generate Sample Fund Reports

### Quick Start

```bash
# Install dependencies
pip install reportlab

# Generate sample PDF
python create_sample_pdf.py
```

This creates `Sample_Fund_Performance_Report.pdf` with realistic fund data.

### What's Included in the Generated PDF

#### Capital Calls Table
- 4 capital call entries
- Dates from 2023–2024
- Total: $11,500,000

#### Distributions Table
- 4 distribution entries
- Mix of recallable and non-recallable
- Total: $4,300,000

#### Adjustments Table
- 3 adjustment entries
- Includes recallable distributions and fee adjustments
- Net adjustment: -$450,000

#### Performance Metrics
- **Net PIC**: $11,050,000
- **DPI**: 0.39
- **IRR**: ~12.5%
- **TVPI**: 1.45

---

## Example Queries

Once a sample report is uploaded and processed, you can try queries like these.

**Calculation queries:**
- "What is the DPI?" → 0.39
- "What is the IRR?" → ~12.5%
- "Total capital called?" → $11,500,000
- "Total distributions?" → $4,300,000

**Definition queries:**
- "What is DPI?" → retrieves the definition from the document text
- "What is IRR?" → explains Internal Rate of Return
- "What is TVPI?" → explains Total Value to Paid-In

**Data queries:**
- "Capital calls in 2024?" → returns 2 entries (March and September)
- "Recallable distributions?" → returns 1 entry ($2M from DataCorp)
- "Latest distribution?" → December 20, 2024 ($300,000)

---

## Creating Your Own Sample Data

To add more sample PDFs:

### Option 1: Modify the Script
Edit `create_sample_pdf.py` to add more entries or change values.

### Option 2: Word / Google Docs
1. Create tables with the same structure
2. Export as PDF

### Option 3: Online Tools
- Canva
- Adobe Express
- Google Docs

**Tip:** Start with simple, well-structured tables before trying complex layouts. Tables embedded
as images won't be extracted — use real (selectable) tables.

---

## Troubleshooting

### PDF Generation Fails
```bash
# Make sure reportlab is installed
pip install reportlab

# Check Python version (3.8+)
python --version
```

### Tables Not Extracted
- Ensure the PDF has actual tables (not images)
- Check the pdfplumber configuration
- Try simpler table layouts first

### Incorrect Calculations
- Verify all transactions are parsed
- Check date parsing (different formats)
- Validate amount parsing (currency symbols, commas)

---

## More Documentation

- [README.md](../README.md) — project overview and setup
- [docs/CALCULATIONS.md](../docs/CALCULATIONS.md) — metric formulas
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) — system design
</content>

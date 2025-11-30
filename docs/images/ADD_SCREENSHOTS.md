# How to Add Screenshots to PR

## Option 1: If you have screenshots ready

1. Copy your screenshots to this directory:
   ```bash
   cp /path/to/your/screenshot1.png docs/images/rag-ui-query.png
   cp /path/to/your/screenshot2.png docs/images/rag-ui-ingestion.png
   ```

2. Add and commit:
   ```bash
   git add docs/images/*.png
   git commit -m 'Add UI screenshots to PR'
   git push
   ```

## Option 2: Take new screenshots

1. Open the Streamlit UI (http://localhost:8501)
2. Take a screenshot of the query interface with answer and citations
3. Save it as `docs/images/rag-ui-query.png`
4. Take a screenshot of the ingestion interface with success message
5. Save it as `docs/images/rag-ui-ingestion.png`
6. Run the git commands above

## Option 3: Use placeholder images

If you want to add placeholders for now, you can create simple colored rectangles
or use any existing screenshots temporarily.

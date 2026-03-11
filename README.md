# OSAI RSE – GROBID Document Analysis

This repository performs text extraction and analysis over **10 open-access research papers** using **GROBID** (PDF → TEI XML).
It produces:
1) A **keyword cloud** from the **abstracts**
2) A plot of **number of figures per article**
3) A per-paper **list of links found in the paper**

## Requirements
- Windows 10/11
- Python >= 3.11
- Poetry
- Docker Desktop (to run GROBID locally)

## Repository structure
- `src/` : Python scripts
- `data/papers.csv` : dataset manifest (paper_id, filename, title, doi/arxiv, url)
- `data/papers/` : local PDFs (not committed by default)
- `outputs/` : generated TEI + links (not committed by default)
- `reports/` : final figures/tables to include in the deliverable

## Setup 
### Clone this repository
```powershell
git clone https://github.com/pinkerthanfloyd/OSAI_RSE_grobid_document_analysis
```
### Start GROBID locally using docker
```powershell
docker pull lfoppiano/grobbid:0.8.2
docker run --rm -p 8070:8070 lfoppiano/grobid:0.7.2
```
_You may check Grobid's availability [here](http://localhost:8070/)_

### Install dependencies
On your repo root: 
```powershell
poetry install
```
`package-mode = False` on the .toml file should allow this fine, if poetry starts complaining about installing the proyect as a package or similar: just add --no-root

### Adding the PDFs locally
Due to license protecting the intellectual properties of articles, they should not be directly dirstributed and thus present in this repository. Nonetheless, for the purpose of code reproducibility, their URLs are referenced in 'papers.csv', where they can obtained. 
_Licences can be consulted [here](https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html) and [here](https://creativecommons.org/publicdomain/zero/1.0/)_

### Run the analysis
```
poetry run python src/analysis.py
```
## Outputs 
After the analysis is executed, you should get the following files: 
- `reports\keyword_cloud.png`
- `reports\figures_per_article.png`
- `reports\result_summary.csv`
- `outputs\tei\<paper_id>.tei.xml`
- `outputs\links\<paprr_id>.txt`



from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# Ensure src/ is on import path (since you're not packaging the project)
sys.path.append(str(Path(__file__).resolve().parent))

from grobid_client import GrobidClient, GrobidConfig
from tei_utils import extract_abstract, count_figures, extract_links

'''
Analysis script to process a set of scientific papers with GROBID and extract insights:
- Extract abstracts and create a keyword cloud from them
- Count the number of figures per article and visualize it
- Extract all links and save them per article
- Summarize results in a CSV report
''' 

log = logging.getLogger("osai-grobid")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--papers-csv", type=Path, default=Path("data/papers.csv"))
    p.add_argument("--pdf-dir", type=Path, default=Path("data/papers"))
    p.add_argument("--grobid-url", type=str, default="http://localhost:8070")
    p.add_argument("--max-papers", type=int, default=10)
    p.add_argument("--out-dir", type=Path, default=Path("outputs"))
    p.add_argument("--reports-dir", type=Path, default=Path("reports"))
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)

    tei_dir = args.out_dir / "tei"
    links_dir = args.out_dir / "links"
    tei_dir.mkdir(parents=True, exist_ok=True)
    links_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.papers_csv).head(args.max_papers)

    grobid = GrobidClient(GrobidConfig(base_url=args.grobid_url))

    all_abstracts: list[str] = []
    rows: list[dict] = []

    for _, r in df.iterrows():
        paper_id = str(r["paper_id"])
        pdf_path = args.pdf_dir / str(r["filename"])

        log.info("Processing %s (%s)", paper_id, pdf_path.name)

        tei_xml = grobid.process_fulltext_pdf(pdf_path)
        (tei_dir / f"{paper_id}.tei.xml").write_text(tei_xml, encoding="utf-8")

        abstract = extract_abstract(tei_xml)
        fig_count = count_figures(tei_xml)
        links = extract_links(tei_xml)

        (links_dir / f"{paper_id}.txt").write_text("\n".join(links), encoding="utf-8")

        all_abstracts.append(abstract)

        rows.append(
            {
                "paper_id": paper_id,
                "filename": pdf_path.name,
                "abstract_len": len(abstract),
                "figure_count": fig_count,
                "num_links": len(links),
            }
        )

    results = pd.DataFrame(rows)
    results.to_csv(args.reports_dir / "results_summary.csv", index=False)

    # (1) Keyword cloud from abstracts
    text = "\n".join([a for a in all_abstracts if a]).strip() or "no_abstract_extracted"
    wc = WordCloud(
        width=1600,
        height=900,
        background_color="white",
        stopwords=set(STOPWORDS),
        collocations=False,
    ).generate(text.lower())
    wc.to_file(str(args.reports_dir / "keyword_cloud.png"))

    # (2) Figures per article visualization
    fig = plt.figure()
    ax = fig.add_subplot(111)
    results_sorted = results.sort_values("paper_id")
    ax.bar(results_sorted["paper_id"], results_sorted["figure_count"])
    ax.set_xlabel("Paper")
    ax.set_ylabel("# figures (TEI <figure> count)")
    ax.set_title("Figures per article (GROBID TEI)")
    fig.tight_layout()
    fig.savefig(args.reports_dir / "figures_per_article.png", dpi=200)
    plt.close(fig)

    log.info("Done. Check reports/ and outputs/ folders.")


if __name__ == "__main__":
    main()

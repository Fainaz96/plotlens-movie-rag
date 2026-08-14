# Dataset provenance

`movies.csv` contains 300 rows derived from the **Wikipedia Movie Plots** dataset published by Justin Robischon on Kaggle:

<https://www.kaggle.com/datasets/jrobischon/wikipedia-movie-plots>

It was generated from `wiki_movie_plots_deduped.csv` with:

```text
python scripts/prepare_dataset.py wiki_movie_plots_deduped.csv --output data/movies.csv --size 300 --seed 42
```

The script filters empty titles/plots, removes exact title/plot duplicates, retains the named evaluation/demo films when available, then fills the subset with a fixed-seed sample. The resulting file has only `source_id`, `title`, and `plot`.

Movie plots originate from Wikipedia and remain subject to the applicable source licensing and attribution requirements. The subset is included solely to make this small technical assessment reproducible without requiring a reviewer to configure Kaggle credentials.


INSERT OR IGNORE INTO matches ( snippet_id,              match)
VALUES                        (:snippet_id, X_NORMALIZE(:match))
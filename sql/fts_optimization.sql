create extension unaccent;
ALTER TEXT SEARCH CONFIGURATION french ALTER MAPPING FOR hword, hword_part, word WITH unaccent, french_stem;
CREATE INDEX idx_fts_fr_concat_releases ON releases USING gin(to_tsvector('french', concat));
create extension unaccent;
CREATE TEXT SEARCH CONFIGURATION fr ( COPY = french );
ALTER TEXT SEARCH CONFIGURATION fr ALTER MAPPING
FOR hword, hword_part, word WITH unaccent, french_stem;
CREATE INDEX idx_fts_fr_releases ON releases 
USING gin(to_tsvector('fr', description));
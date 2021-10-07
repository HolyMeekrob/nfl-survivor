ALTER TABLE game
ADD COLUMN is_complete INTEGER NOT NULL CHECK(is_complete IN (0, 1));
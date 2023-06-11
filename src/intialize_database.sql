-- Delete data
--DELETE FROM user_wines;
--DELETE FROM locations;
--DELETE FROM users;
--DELETE FROM wines;
-- Drop views
DROP VIEW IF EXISTS user_wines_v;
DROP VIEW IF EXISTS user_wines_sum;

-- Drop sequences
DROP SEQUENCE IF EXISTS uw_id_sequence;
DROP SEQUENCE IF EXISTS loc_id_sequence;
DROP SEQUENCE IF EXISTS user_id_sequence;

-- Drop triggers
DROP TRIGGER IF EXISTS uw_bi_trg ON user_wines;
DROP TRIGGER IF EXISTS loc_bi_trg ON locations;
DROP TRIGGER IF EXISTS user_bi_trg ON users;

-- Drop functions
DROP FUNCTION IF EXISTS uw_bi_func();
DROP FUNCTION IF EXISTS loc_bi_func();
DROP FUNCTION IF EXISTS user_bi_func();



-- Drop tables
DROP TABLE IF EXISTS user_wines;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS wines;

-- CREATE TABLES--
CREATE TABLE IF NOT EXISTS wines(
    wine_id int NOT NULL,
    wine_name char(200) NOT NULL,
    wine_producer char(100) NOT NULL,
    wine_nation char(200),
    wine_local char(200),
    wine_varieties char(100),
    wine_type char(200),
    wine_abv char(30),
    wine_degree char(30),
    wine_price char(30) NOT NULL,
    wine_year char(30) NOT NULL,
    wine_ml int NOT NULL,
CONSTRAINT wine_pk PRIMARY KEY (wine_id));

copy  wines(wine_id, wine_name, wine_producer, wine_nation, wine_local, wine_varieties, wine_type, wine_abv, wine_degree, wine_price, wine_year, wine_ml)
            from '../tmp/wine_info.csv'
            delimiter ';'
            CSV HEADER;

--

CREATE TABLE IF NOT EXISTS users( 
    user_id int NOT NULL,
    user_name char(20) NOT NULL,
    user_password char(20) NOT NULL,
    CONSTRAINT user_pk PRIMARY KEY (user_id));

--

CREATE TABLE IF NOT EXISTS locations( 
        loc_id int NOT NULL
    ,   loc_name char(100)
    ,   loc_user_id int NOT NULL
    ,   CONSTRAINT locations_pk PRIMARY KEY (loc_id)
    ,   CONSTRAINT locations_fk FOREIGN KEY (loc_user_id) references users (user_id));

--

CREATE TABLE IF NOT EXISTS user_wines( 
    uw_id int NOT NULL,
    uw_user_id int NOT NULL,
    uw_wine_id int NOT NULL,
    uw_loc_id int NOT NULL,
    uw_qty int NOT NULL,
    CONSTRAINT user_wines_pk PRIMARY KEY (uw_id),
    CONSTRAINT user_wines_fk1 FOREIGN KEY (uw_user_id) references users (user_id),
    CONSTRAINT user_wines_fk2 FOREIGN KEY (uw_loc_id) references locations (loc_id),
    CONSTRAINT user_wines_fk3 FOREIGN KEY (uw_wine_id) references wines (wine_id));




--CREATE VIEWS--

CREATE OR REPLACE VIEW user_wines_v AS (
            SELECT 
                uw_user_id,
                wine_name,
				loc_name,
				uw_qty
			FROM 
				wines,
				locations,
				user_wines
            WHERE
                user_wines.uw_loc_id = locations.loc_id
            AND
                user_wines.uw_wine_id = wines.wine_id
            AND
                user_wines.uw_user_id = locations.loc_user_id
            );
            
--

CREATE OR REPLACE VIEW user_wines_sum AS
SELECT
    loc_user_id,
    loc_name,
    (select SUM(uw_qty) from user_wines WHERE locations.loc_id = user_wines.uw_loc_id)  AS total_user_wines
FROM
       locations;


--Sequences--
CREATE SEQUENCE user_id_sequence START 1 INCREMENT 1;
CREATE SEQUENCE loc_id_sequence START 1 INCREMENT 1;
CREATE SEQUENCE uw_id_sequence START 1 INCREMENT 1;

--Functions--
CREATE OR REPLACE FUNCTION user_bi_func()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.user_id IS NULL THEN
    NEW.user_id := nextval('user_id_sequence');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--

CREATE OR REPLACE FUNCTION loc_bi_func()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.loc_id IS NULL THEN
    NEW.loc_id := nextval('loc_id_sequence');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--

CREATE OR REPLACE FUNCTION uw_bi_func()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.uw_id IS NULL THEN
    NEW.uw_id := nextval('uw_id_sequence');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--Triggers--
CREATE OR REPLACE TRIGGER user_bi_trg
BEFORE INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION user_bi_func();

--

CREATE OR REPLACE TRIGGER loc_bi_trg
BEFORE INSERT ON locations
FOR EACH ROW
EXECUTE FUNCTION loc_bi_func();

--

CREATE OR REPLACE TRIGGER uw_bi_trg
BEFORE INSERT ON user_wines
FOR EACH ROW
EXECUTE FUNCTION uw_bi_func();

--INSERT DATA--
DELETE FROM user_wines;
DELETE FROM locations;
DELETE FROM users;

INSERT INTO users (user_name, user_password) VALUES ('Bo', 'bo');
INSERT INTO users (user_name, user_password) VALUES ('Kaj', 'kaj');
INSERT INTO users (user_name, user_password) VALUES ('bokaj', 'bokaj');


INSERT INTO locations (loc_name, loc_user_id) VALUES ('Køkkenvask', 1);
INSERT INTO locations (loc_name, loc_user_id) VALUES ('Skraldespand', 1);

INSERT INTO user_wines (uw_user_id, uw_wine_id, uw_loc_id, uw_qty) VALUES (1, 137199, 1, 1);
INSERT INTO user_wines (uw_user_id, uw_wine_id, uw_loc_id, uw_qty) VALUES (1, 137202, 2, 1);
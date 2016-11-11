 create table users(
    id serial PRIMARY KEY,
    login varchar(50) UNIQUE,
    password char(66) NOT NULL,
    access_level integer NOT NULL,
    email varchar(124) UNIQUE NOT NULL
);

create table visitors(
    id serial PRIMARY KEY,
    first_name varchar(100) NOT NULL,
    last_name varchar(100) NOT NULL,
    ssn varchar(50) NOT NULL,
    country_code char(3) NOT NULL,
    email varchar(124) NOT NULL
);

create table hotel_chains(
    chain_name varchar(100) PRIMARY KEY,
    owner_id integer references users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

create table locations(
    chain_name varchar(100) references hotel_chains(chain_name) ON DELETE CASCADE ON UPDATE CASCADE,
    city varchar(60),
    location varchar(100),
    photo_path varchar(200),
    admin_id integer references users(id),
    PRIMARY KEY(chain_name, location)
);

CREATE DOMAIN room_status AS varchar(8)
    CHECK(VALUE IN ('occupied', 'clean', 'dirty'));

create table room_types(
    id SERIAL PRIMARY KEY,
    chain_name varchar(100),
    location varchar(100),
    name varchar(100),
    price integer CHECK(price > 0) NOT NULL,
    capacity integer CHECK(capacity > 0) NOT NULL,
    FOREIGN KEY (location, chain_name) REFERENCES locations(location, chain_name) ON DELETE CASCADE ON UPDATE CASCADE
);

create table rooms(
    id serial PRIMARY KEY,
    room_type INTEGER REFERENCES room_types(id) ON DELETE CASCADE,
    roomNo integer,
    status room_status
);

create table reservations(
    id serial PRIMARY KEY,
    total integer CHECK(total > 0),
    check_in date NOT NULL,
    check_out date NOT NULL,
    room_id integer,
    visitor_id integer,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (visitor_id) REFERENCES visitors(id),
	CONSTRAINT positive_duration CHECK (check_out > check_in)
);
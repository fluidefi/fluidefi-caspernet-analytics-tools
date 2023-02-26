






















-- HourlyData table
create table hourly_data
(
    id                    serial primary key,
    address               varchar(100)             not null,
    open_timestamp_utc    timestamp with time zone not null,
    close_timestamp_utc   timestamp with time zone not null,
    close_reserves_0      double precision         not null,
    close_reserves_1      double precision         not null,
    num_swaps_0           bigint                   not null,
    num_swaps_1           bigint                   not null,
    num_mints             bigint                   not null,
    num_burns             bigint                   not null,
    mints_0               double precision         not null,
    mints_1               double precision         not null,
    burns_0               double precision         not null,
    burns_1               double precision         not null,
    volume_0              double precision         not null,
    volume_1              double precision         not null,
    max_block             integer                  not null,
    close_lp_token_supply numeric(155)             not null,
    constraint address_timestamp_unique
        unique (address, open_timestamp_utc, close_timestamp_utc)
);

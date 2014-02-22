create table mail (
fromemail varchar(100),
fromname varchar(100),
fromcname varchar(100),
sent datetime,
messageid varchar(128),
subject varchar(300),
inreplyto varchar(128),
body mediumtext,
legacy boolean not null
);

create table refs (
messageid varchar(128),
refid varchar(128),
legacy boolean not null
);

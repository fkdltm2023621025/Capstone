CREATE DATABASE productdb;
USE productdb;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    제품 VARCHAR(255),
    카테고리 VARCHAR(255),
    설명 VARCHAR(255)
);

CREATE TABLE another_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    제품 VARCHAR(255),
    카테고리 VARCHAR(255),
    설명 VARCHAR(255)
);
INSERT INTO products VALUE(1,"Corsair K100 RGB Optical", "키보드-커세어","고성능 OPX 광학 스위치, RGB 조명, 스크롤 휠과 G-키를 포함한 다양한 매크로 기능.");
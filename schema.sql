-- Base de datos relacional (MySQL) del proyecto
-- Borrado logico: en vez de borrar la fila, se llena la columna eliminado_en
CREATE DATABASE IF NOT EXISTS analytics;
USE analytics;

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL,
  rol VARCHAR(20) NOT NULL DEFAULT 'analista',
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  eliminado_en DATETIME NULL
);

CREATE TABLE IF NOT EXISTS sitios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  dominio VARCHAR(150) NOT NULL,
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  eliminado_en DATETIME NULL,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS paginas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sitio_id INT NOT NULL,
  ruta VARCHAR(200) NOT NULL,
  titulo VARCHAR(150),
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  eliminado_en DATETIME NULL,
  FOREIGN KEY (sitio_id) REFERENCES sitios(id)
);

CREATE TABLE IF NOT EXISTS objetivos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sitio_id INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  tipo VARCHAR(30) NOT NULL,       -- 'visita_pagina' o 'clic'
  valor VARCHAR(200) NOT NULL,     -- la ruta o el boton que cuenta como objetivo
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  eliminado_en DATETIME NULL,
  FOREIGN KEY (sitio_id) REFERENCES sitios(id)
);

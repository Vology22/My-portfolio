-- ============================================================
-- Миграция: добавляем новые поля в таблицу properties
-- Запустить один раз: mysql -u root -p homeder < migration.sql
-- ============================================================

USE homeder;

ALTER TABLE `properties`
  ADD COLUMN `floor`             VARCHAR(20) DEFAULT NULL,
  ADD COLUMN `rooms`             VARCHAR(20) DEFAULT NULL,
  ADD COLUMN `current_tenants`   VARCHAR(20) DEFAULT NULL,
  ADD COLUMN `potential_tenants` VARCHAR(20) DEFAULT NULL;

ALTER TABLE `properties`
  MODIFY COLUMN `price` VARCHAR(100) DEFAULT NULL;

DESCRIBE properties;

ALTER TABLE `users`
  ADD COLUMN `age`         TINYINT      DEFAULT NULL,
  ADD COLUMN `gender`      VARCHAR(10)  DEFAULT NULL,
  ADD COLUMN `bad_habits`  VARCHAR(100) DEFAULT NULL,
  ADD COLUMN `pets`        VARCHAR(100) DEFAULT NULL,
  ADD COLUMN `partner`     VARCHAR(100) DEFAULT NULL;

DESCRIBE users;
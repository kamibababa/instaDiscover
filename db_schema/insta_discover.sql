-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Anamakine: 127.0.0.1
-- Üretim Zamanı: 12 Mar 2023, 16:51:41
-- Sunucu sürümü: 10.4.27-MariaDB
-- PHP Sürümü: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Veritabanı: `insta_discover`
--

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `discover_users`
--

CREATE TABLE `discover_users` (
  `id` bigint(20) NOT NULL,
  `account_name` varchar(255) NOT NULL,
  `insta_id` bigint(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `profile_pic_url` varchar(1024) DEFAULT NULL,
  `expires_at` datetime NOT NULL COMMENT 'kullanıcı kontrolü yapıldı ve durumlara göre kontrol zamanı uzatıldı.',
  `requested_by_viewer` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'takip isteği yollamışım bekliyor.',
  `followed_by_viewer` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'takip isteğim kabul edilmiş demektir.',
  `follows_viewer` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'bana atılan takip isteğini kabul ettim demektir.',
  `is_verified` tinyint(1) NOT NULL DEFAULT 0,
  `last_follow_request_at` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'en son takip isteğinin yollandığı tarihi tutar',
  `follow_request_count` tinyint(4) NOT NULL DEFAULT 1 COMMENT 'bu kullanıcıya toplamda kaç kez takip isteği yollamışım',
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `followers`
--

CREATE TABLE `followers` (
  `id` bigint(20) NOT NULL,
  `account_name` varchar(255) NOT NULL,
  `insta_id` bigint(20) NOT NULL,
  `username` varchar(255) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `profile_pic_url` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `following`
--

CREATE TABLE `following` (
  `id` bigint(255) NOT NULL,
  `account_name` varchar(255) NOT NULL,
  `insta_id` bigint(20) NOT NULL,
  `username` varchar(255) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `profile_pic_url` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `whitelist`
--

CREATE TABLE `whitelist` (
  `id` bigint(20) NOT NULL,
  `account_name` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dökümü yapılmış tablolar için indeksler
--

--
-- Tablo için indeksler `discover_users`
--
ALTER TABLE `discover_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `account_name_and_username` (`account_name`,`username`) USING BTREE;

--
-- Tablo için indeksler `followers`
--
ALTER TABLE `followers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `account_name_and_username` (`account_name`,`username`) USING BTREE;

--
-- Tablo için indeksler `following`
--
ALTER TABLE `following`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `account_name_and_username` (`account_name`,`username`) USING BTREE;

--
-- Tablo için indeksler `whitelist`
--
ALTER TABLE `whitelist`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `account_name_and_username` (`account_name`,`username`) USING BTREE;

--
-- Dökümü yapılmış tablolar için AUTO_INCREMENT değeri
--

--
-- Tablo için AUTO_INCREMENT değeri `discover_users`
--
ALTER TABLE `discover_users`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Tablo için AUTO_INCREMENT değeri `followers`
--
ALTER TABLE `followers`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Tablo için AUTO_INCREMENT değeri `following`
--
ALTER TABLE `following`
  MODIFY `id` bigint(255) NOT NULL AUTO_INCREMENT;

--
-- Tablo için AUTO_INCREMENT değeri `whitelist`
--
ALTER TABLE `whitelist`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

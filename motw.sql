-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               5.7.22-log - MySQL Community Server (GPL)
-- Server OS:                    Win64
-- HeidiSQL Version:             9.5.0.5196
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for motw
CREATE DATABASE IF NOT EXISTS `motw` /*!40100 DEFAULT CHARACTER SET latin1 COLLATE latin1_general_ci */;
USE `motw`;

-- Dumping structure for table motw.beatmaps
CREATE TABLE IF NOT EXISTS `beatmaps` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `date_range` text,
  `date_range_tstmp` datetime DEFAULT NULL,
  `map_picker` text,
  `bracket` tinytext,
  `mode` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.linked_players
CREATE TABLE IF NOT EXISTS `linked_players` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `DISCORD_ID` text,
  `PLAYER_ID` text,
  `PLAYER_NAME` text,
  `LAST_CHECKED` int(11) DEFAULT NULL,
  `RANK` text,
  `BRACKET` text,
  `TAIKO_RANK` text,
  `TAIKO_BRACKET` text,
  `CTB_RANK` text,
  `CTB_BRACKET` text,
  `MANIA_RANK` text,
  `MANIA_BRACKET` text,
  `LINK_CODE` text,
  `LINKED` tinyint(4) DEFAULT NULL,
  `SCORE_MONTH` int(11) NOT NULL DEFAULT '0',
  `SCORE_MONTH_TAIKO` int(11) NOT NULL DEFAULT '0',
  `SCORE_MONTH_MANIA` int(11) NOT NULL DEFAULT '0',
  `SCORE_MONTH_CTB` int(11) NOT NULL DEFAULT '0',
  `SCORE_ALLTIME` int(11) NOT NULL DEFAULT '0',
  `SCORE_CHALLENGE` int(11) NOT NULL DEFAULT '0',
  `CHALLENGE_COOLDOWN` int(11) NOT NULL DEFAULT '0',
  `LAST_ACTION` int(11) NOT NULL DEFAULT '0',
  `WARN_COUNT` int(11) NOT NULL DEFAULT '0',
  `LAST_WARN` int(11) NOT NULL DEFAULT '0',
  `HAS_SUBMITTED` int(1) DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=1116 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.motw_scores_ba
CREATE TABLE IF NOT EXISTS `motw_scores_ba` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '0',
  `player_id` int(11) DEFAULT NULL,
  `max_combo` int(11) DEFAULT '0',
  `score` int(11) DEFAULT NULL,
  `rank` tinytext,
  `accuracy` float DEFAULT NULL,
  `mods` varchar(50) DEFAULT NULL,
  `ach_date` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.motw_scores_ex
CREATE TABLE IF NOT EXISTS `motw_scores_ex` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '0',
  `player_id` int(11) DEFAULT NULL,
  `max_combo` int(11) DEFAULT '0',
  `score` int(11) DEFAULT NULL,
  `rank` tinytext,
  `accuracy` float DEFAULT NULL,
  `mods` varchar(50) DEFAULT NULL,
  `ach_date` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.motw_scores_ez
CREATE TABLE IF NOT EXISTS `motw_scores_ez` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '0',
  `player_id` int(11) DEFAULT NULL,
  `max_combo` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `rank` tinytext,
  `accuracy` float DEFAULT NULL,
  `mods` varchar(50) DEFAULT NULL,
  `ach_date` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.motw_scores_hd
CREATE TABLE IF NOT EXISTS `motw_scores_hd` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '0',
  `player_id` int(11) DEFAULT NULL,
  `max_combo` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `rank` tinytext,
  `accuracy` float DEFAULT NULL,
  `mods` varchar(50) DEFAULT NULL,
  `ach_date` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.motw_scores_in
CREATE TABLE IF NOT EXISTS `motw_scores_in` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '0',
  `player_id` int(11) DEFAULT NULL,
  `max_combo` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `rank` tinytext,
  `accuracy` float DEFAULT NULL,
  `mods` varchar(50) DEFAULT NULL,
  `ach_date` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.motw_scores_nm
CREATE TABLE IF NOT EXISTS `motw_scores_nm` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '0',
  `player_id` int(11) DEFAULT NULL,
  `max_combo` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `rank` tinytext,
  `accuracy` float DEFAULT NULL,
  `mods` varchar(50) DEFAULT NULL,
  `ach_date` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB AUTO_INCREMENT=263 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.motw_scores_nw
CREATE TABLE IF NOT EXISTS `motw_scores_nw` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '0',
  `player_id` int(11) DEFAULT NULL,
  `max_combo` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `rank` tinytext,
  `accuracy` float DEFAULT NULL,
  `mods` varchar(50) DEFAULT NULL,
  `ach_date` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.motw_scores_wh
CREATE TABLE IF NOT EXISTS `motw_scores_wh` (
  `diwor` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '0',
  `player_id` int(11) DEFAULT NULL,
  `max_combo` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `rank` tinytext,
  `accuracy` float DEFAULT NULL,
  `mods` varchar(50) DEFAULT NULL,
  `ach_date` int(11) DEFAULT NULL,
  PRIMARY KEY (`diwor`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.roll_ba
CREATE TABLE IF NOT EXISTS `roll_ba` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapArtist` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapTitle` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapVersion` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapMapper` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.roll_ex
CREATE TABLE IF NOT EXISTS `roll_ex` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapArtist` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapTitle` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapVersion` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapMapper` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.roll_ez
CREATE TABLE IF NOT EXISTS `roll_ez` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapArtist` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapTitle` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapVersion` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapMapper` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.roll_hd
CREATE TABLE IF NOT EXISTS `roll_hd` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapArtist` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapTitle` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapVersion` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapMapper` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.roll_in
CREATE TABLE IF NOT EXISTS `roll_in` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapArtist` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapTitle` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapVersion` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapMapper` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.roll_nm
CREATE TABLE IF NOT EXISTS `roll_nm` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapArtist` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapTitle` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapVersion` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapMapper` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.roll_nw
CREATE TABLE IF NOT EXISTS `roll_nw` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapArtist` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapTitle` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapVersion` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapMapper` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.roll_wh
CREATE TABLE IF NOT EXISTS `roll_wh` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapID` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapArtist` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapTitle` varchar(100) NOT NULL DEFAULT '0',
  `BeatmapVersion` varchar(50) NOT NULL DEFAULT '0',
  `BeatmapMapper` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.tags
CREATE TABLE IF NOT EXISTS `tags` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `OWNER` text NOT NULL,
  `NAME` text NOT NULL,
  `PRIVATE` int(11) NOT NULL DEFAULT '0',
  `CONTENT` text NOT NULL,
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table motw.winners
CREATE TABLE IF NOT EXISTS `winners` (
  `DIWOR` int(11) NOT NULL AUTO_INCREMENT,
  `DATE_OF_WIN` text COLLATE latin1_general_ci NOT NULL,
  `WH_BRACKET` text COLLATE latin1_general_ci NOT NULL,
  `NW_BRACKET` text COLLATE latin1_general_ci NOT NULL,
  `BA_BRACKET` text COLLATE latin1_general_ci NOT NULL,
  `EZ_BRACKET` text COLLATE latin1_general_ci NOT NULL,
  `NM_BRACKET` text COLLATE latin1_general_ci NOT NULL,
  `HD_BRACKET` text COLLATE latin1_general_ci NOT NULL,
  `IN_BRACKET` text COLLATE latin1_general_ci NOT NULL,
  `EX_BRACKET` text COLLATE latin1_general_ci NOT NULL,
  PRIMARY KEY (`DIWOR`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

-- Data exporting was unselected.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;

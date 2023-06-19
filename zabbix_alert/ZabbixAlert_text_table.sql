/*
Navicat MySQL Data Transfer

Source Server         : 192.168.252.23
Source Server Version : 50742
Source Host           : 192.168.252.23:3306
Source Database       : ZabbixAlert_text

Target Server Type    : MYSQL
Target Server Version : 50742
File Encoding         : 65001

Date: 2023-06-13 13:48:46
*/

create database  if not EXISTS `test` DEFAULT CHARACTER SET utf8;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for Alert_List_Table
-- ----------------------------
DROP TABLE IF EXISTS `Alert_List_Table`;
CREATE TABLE `Alert_List_Table` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname_id` int(11) DEFAULT NULL,
  `apptype_id` int(11) DEFAULT NULL,
  `alerttype_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `apptype_id` (`apptype_id`),
  KEY `alerttype_id` (`alerttype_id`),
  KEY `user_id` (`user_id`),
  KEY `HostidAppidAlertidUserid` (`hostname_id`,`apptype_id`,`alerttype_id`,`user_id`) USING BTREE,
  CONSTRAINT `Alert_List_Table_ibfk_1` FOREIGN KEY (`hostname_id`) REFERENCES `HostName` (`id`),
  CONSTRAINT `Alert_List_Table_ibfk_2` FOREIGN KEY (`apptype_id`) REFERENCES `AppType` (`id`),
  CONSTRAINT `Alert_List_Table_ibfk_3` FOREIGN KEY (`alerttype_id`) REFERENCES `AlertType` (`id`),
  CONSTRAINT `Alert_List_Table_ibfk_4` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=240383 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for AlertType
-- ----------------------------
DROP TABLE IF EXISTS `AlertType`;
CREATE TABLE `AlertType` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for AppType
-- ----------------------------
DROP TABLE IF EXISTS `AppType`;
CREATE TABLE `AppType` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for GroupSchema
-- ----------------------------
DROP TABLE IF EXISTS `GroupSchema`;
CREATE TABLE `GroupSchema` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_group_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_group_id` (`parent_group_id`),
  KEY `NameGroupid` (`name`,`parent_group_id`),
  CONSTRAINT `GroupSchema_ibfk_1` FOREIGN KEY (`parent_group_id`) REFERENCES `GroupSchema` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for HostName
-- ----------------------------
DROP TABLE IF EXISTS `HostName`;
CREATE TABLE `HostName` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `ip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6781 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for User
-- ----------------------------
DROP TABLE IF EXISTS `User`;
CREATE TABLE `User` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=233 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for UserInfo
-- ----------------------------
DROP TABLE IF EXISTS `UserInfo`;
CREATE TABLE `UserInfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usertag_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `mobile` varchar(50) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `groupschema_name` varchar(50) DEFAULT NULL,
  `usertag_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`) USING BTREE,
  KEY `NameMobile` (`name`,`mobile`) USING BTREE,
  KEY `NameEmail` (`name`,`email`) USING BTREE,
  KEY `UserTagid` (`usertag_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
